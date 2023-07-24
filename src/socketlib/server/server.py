import queue
import logging
import socket
import threading
from typing import Callable, Optional

from socketlib.basic.buffer import Buffer
from socketlib.basic.receive import receive_and_enqueue
from socketlib.basic.send import get_and_send_messages


class ServerBase:
    """ Parent class for other server classes that implements some common methods.

        This class should not be instantiated.
    """

    def __init__(
            self,
            address: tuple[str, int],
            reconnect: bool = True,
            timeout: Optional[float] = None,
            stop: Optional[Callable[[], bool]] = None,
            stop_reconnect: Optional[Callable[[], bool]] = None,
            logger: Optional[logging.Logger] = None,
    ):
        self._address = address
        self._socket = None  # type: Optional[socket.socket]
        self._connection = None  # The client connection
        self._conn_details = None

        self._stop_event = threading.Event()
        self._stop_reconnect_event = threading.Event()
        self._stop = self._get_stop_function(stop, self._stop_event)
        self._stop_reconnect = self._get_stop_function(
            stop_reconnect, self._stop_reconnect_event)

        self._reconnect = reconnect
        self._logger = logger

        self._run_thread = threading.Thread()

        self._timeout = timeout  # Timeout for send and receive

        self.msg_end = b"\r\n"

    @property
    def ip(self) -> str:
        return self._address[0]

    @property
    def port(self) -> int:
        return self._address[1]

    def listen(self) -> None:
        """ Creates the socket and puts it in listen mode.
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(self._address)
        self._socket.listen()
        if self._logger is not None:
            self._logger.info(
                f"{self.__class__.__name__}: "
                f"Listening for connections in {self._address}"
            )

    def accept_connection(self) -> None:
        """ Accept a new connection.
        """
        self._connection, self._conn_details = self._socket.accept()
        if self._timeout is not None:
            self._connection.settimeout(self._timeout)
        if self._logger is not None:
            self._logger.info(
                f"{self.__class__.__name__}: "
                f"connection accepted from {self._conn_details}"
            )

    def start(self) -> None:
        """ Start this server in a new thread.

            If this method is used, there is no need to call the `listen` and `accept_connection`
            as they are called behind the scenes.
        """
        self.listen()
        self._run_thread.start()

    def join(self) -> None:
        self._run_thread.join()

    def shutdown(self) -> None:
        self._stop_event.set()
        self._stop_reconnect_event.set()
        self.join()

    def __enter__(self):
        return self

    def close_connection(self) -> None:
        if self._connection is not None:
            self._connection.close()
        if self._socket is not None:
            self._socket.close()

    @staticmethod
    def _get_stop_function(
            stop: Optional[Callable[[], bool]],
            stop_event: threading.Event
    ) -> Callable[[], bool]:
        if stop is None:
            return lambda: not stop_event.is_set()
        return stop

    def __exit__(self, *args):
        self.close_connection()


class ServerReceiver(ServerBase):
    """ A server that receives messages from a single client.
    """
    def __init__(
            self,
            address: tuple[str, int],
            received: Optional[queue.Queue[bytes]] = None,
            reconnect: bool = True,
            timeout: Optional[float] = None,
            stop: Optional[Callable[[], bool]] = None,
            logger: Optional[logging.Logger] = None,
    ):
        super().__init__(
            address=address,
            reconnect=reconnect,
            timeout=timeout,
            stop=stop,
            logger=logger)
        self._buffer = None  # type: Optional[Buffer]
        self._received = received if received is not None else queue.Queue()
        self._run_thread = threading.Thread(
            target=self._recv, daemon=True
        )

    @property
    def received(self) -> queue.Queue[bytes]:
        return self._received

    def accept_connection(self) -> None:
        super().accept_connection()
        self._buffer = Buffer(self._connection)

    def _recv(self):
        if self._reconnect:
            while not self._stop_reconnect():
                self.accept_connection()
                receive_and_enqueue(
                    buffer=self._buffer,
                    msg_end=self.msg_end,
                    msg_queue=self.received,
                    stop=self._stop,
                    timeout=self._timeout,
                    logger=self._logger,
                    name=self.__class__.__name__
                )
                self.listen()
        else:
            self.accept_connection()
            receive_and_enqueue(
                buffer=self._buffer,
                msg_end=self.msg_end,
                msg_queue=self.received,
                stop=self._stop,
                timeout=self._timeout,
                logger=self._logger,
                name=self.__class__.__name__
            )

    def start_main_thread(self) -> None:
        self.listen()
        self._recv()


class ServerSender(ServerBase):
    """ A server that sends messages to a single client"""

    def __init__(
            self,
            address: tuple[str, int],
            to_send: Optional[queue.Queue[str]] = None,
            reconnect: bool = True,
            timeout: Optional[float] = None,
            stop: Optional[Callable[[], bool]] = None,
            logger: Optional[logging.Logger] = None,
    ):
        super().__init__(
            address=address,
            reconnect=reconnect,
            timeout=timeout,
            stop=stop,
            logger=logger)
        self.msg_end = b"\r\n"
        self._to_send = to_send if to_send is not None else queue.Queue()
        self._run_thread = threading.Thread(
            target=self._send, daemon=True
        )

    @property
    def to_send(self) -> queue.Queue[str]:
        return self._to_send

    def start_main_thread(self) -> None:
        self.listen()
        self._send()

    def _send(self):
        if self._reconnect:
            while not self._stop_reconnect():
                self.accept_connection()
                get_and_send_messages(
                    sock=self._connection,
                    msg_end=self.msg_end,
                    msg_queue=self.to_send,
                    stop=self._stop,
                    timeout=self._timeout,
                    logger=self._logger,
                    name=self.__class__.__name__
                )
                self.listen()
        else:
            self.accept_connection()
            get_and_send_messages(
                sock=self._connection,
                msg_end=self.msg_end,
                msg_queue=self.to_send,
                stop=self._stop,
                timeout=self._timeout,
                logger=self._logger,
                name=self.__class__.__name__
            )


class Server(ServerBase):
    """ A server that sends and receives messages to and from a single client.
    """

    def __init__(
            self,
            address: tuple[str, int],
            received: Optional[queue.Queue[bytes]] = None,
            to_send: Optional[queue.Queue[str]] = None,
            reconnect: bool = True,
            timeout: Optional[float] = None,
            stop_receive: Optional[Callable[[], bool]] = lambda: False,
            stop_send: Optional[Callable[[], bool]] = lambda: False,
            logger: Optional[logging.Logger] = None,
    ):
        super().__init__(address=address, reconnect=reconnect, timeout=timeout, logger=logger)
        self._buffer = None  # type: Optional[Buffer]

        self._received = received if received is not None else queue.Queue()
        self._to_send = to_send if to_send is not None else queue.Queue()
        self._stop_receive = stop_receive
        self._stop_send = stop_send

        self._send_thread = threading.Thread(target=self._send, daemon=True)
        self._recv_thread = threading.Thread(target=self._recv, daemon=True)
        self._connected = threading.Event()

    @property
    def to_send(self) -> queue.Queue[str]:
        return self._to_send

    @property
    def received(self) -> queue.Queue[bytes]:
        return self._received

    @property
    def send_thread(self) -> threading.Thread:
        return self._send_thread

    @property
    def receive_thread(self) -> threading.Thread:
        return self._recv_thread

    def _send(self) -> None:
        self._connected.wait()
        if self._reconnect:
            while not self._stop_reconnect():
                get_and_send_messages(
                    sock=self._connection,
                    msg_end=self.msg_end,
                    msg_queue=self.to_send,
                    stop=self._stop_send,
                    timeout=self._timeout,
                    logger=self._logger,
                    name=self.__class__.__name__
                )
                self._connected.clear()
                self.listen()
                self.accept_connection()
        else:
            get_and_send_messages(
                sock=self._connection,
                msg_end=self.msg_end,
                msg_queue=self.to_send,
                stop=self._stop_send,
                timeout=self._timeout,
                logger=self._logger,
                name=self.__class__.__name__
            )

    def _recv(self):
        self._connected.wait()
        if self._reconnect:
            while not self._stop_reconnect():
                receive_and_enqueue(
                    buffer=self._buffer,
                    msg_end=self.msg_end,
                    msg_queue=self.received,
                    stop=self._stop_receive,
                    timeout=self._timeout,
                    logger=self._logger,
                    name=self.__class__.__name__
                )
                self._connected.wait()
        else:
            receive_and_enqueue(
                buffer=self._buffer,
                msg_end=self.msg_end,
                msg_queue=self.received,
                stop=self._stop_receive,
                timeout=self._timeout,
                logger=self._logger,
                name=self.__class__.__name__
            )

    def accept_connection(self) -> None:
        super().accept_connection()
        self._buffer = Buffer(self._connection)
        self._connected.set()

    def start(self) -> None:
        """ Start this server in a new thread. """
        self.listen()
        accept = threading.Thread(target=self.accept_connection, daemon=True)
        accept.start()
        self._recv_thread.start()
        self._send_thread.start()

    def join(self) -> None:
        self._recv_thread.join()
        self._send_thread.join()

    def shutdown(self) -> None:
        self._stop_send = lambda: True
        self._stop_receive = lambda: True
        self._stop_reconnect = lambda: True
        self.join()
