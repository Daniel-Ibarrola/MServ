import logging
import queue
import socket
import threading
import time
from typing import Callable, Optional

from socketlib.basic.buffer import Buffer
from socketlib.basic.send import send_msg
from socketlib.basic.receive import receive_msg


class ClientBase:
    """ Parent class for other client classes that implements some common methods.

        This class should not be instantiated.
    """

    def __init__(
            self,
            address: tuple[str, int],
            reconnect: bool = True,
            timeout: Optional[float] = None,
            stop: Optional[Callable[[], bool]] = lambda: False,
            stop_reconnect: Optional[Callable[[], bool]] = lambda: False,
            logger: Optional[logging.Logger] = None,
    ):
        self._address = address
        self._socket = None  # type: Optional[socket.socket]
        self._reconnect = reconnect
        self._stop = stop
        self._stop_reconnect = stop_reconnect
        self._logger = logger

        self._run_thread = threading.Thread()

        self._wait_for_connection = threading.Event()
        self._connection_failed = False
        self._connect_timeout = None

        self._timeout = timeout  # Timeout for send and receive

    @property
    def ip(self) -> str:
        return self._address[0]

    @property
    def port(self) -> int:
        return self._address[1]

    @property
    def run_thread(self) -> threading.Thread:
        return self._run_thread

    def connect(self, timeout: Optional[float] = None) -> None:
        """ Connect to the server. This will attempt to connect to the server indefinitively
            unless a timeout is give.

        """
        self._connect_timeout = timeout
        connect_thread = threading.Thread(target=self._connect_to_server, args=(timeout,), daemon=True)
        connect_thread.start()

    def _connect_to_server(self, timeout: Optional[float] = None) -> None:
        start = time.time()
        if timeout is None:
            timeout = float("inf")

        error = False
        while time.time() - start <= timeout:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self._socket.connect((self.ip, self.port))
                if self._timeout is not None:
                    self._socket.settimeout(self._timeout)
                error = False
                break
            except ConnectionError:
                error = True
                time.sleep(1)

        if error and self._logger:
            self._connection_failed = True
            self._logger.error(
                f"{self.__class__.__name__}: "
                f"failed to establish connection to {(self.ip, self.port)}"
            )

        if self._logger is not None and not error:
            self._logger.info(
                f"{self.__class__.__name__}: connected to {(self.ip, self.port)}"
            )

        self._wait_for_connection.set()

    def start(self) -> None:
        """ Start this client in a new thread. """
        self._run_thread.start()

    def join(self) -> None:
        self._run_thread.join()

    def shutdown(self) -> None:
        self._stop = lambda: True
        self._stop_reconnect = lambda: True
        self.join()

    def close_connection(self) -> None:
        if self._socket is not None:
            self._socket.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close_connection()


class ClientReceiver(ClientBase):
    """ A client that receives messages from a server."""

    def __init__(
            self,
            address: tuple[str, int],
            received: Optional[queue.Queue[bytes]] = None,
            reconnect: bool = True,
            timeout: Optional[float] = None,
            stop: Optional[Callable[[], bool]] = lambda: False,
            logger: Optional[logging.Logger] = None,
    ):
        super().__init__(
            address=address,
            reconnect=reconnect,
            timeout=timeout,
            stop=stop,
            logger=logger)
        self.msg_end = b"\r\n"
        self._buffer = None  # type: Optional[Buffer]
        self._received = received if received is not None else queue.Queue()
        self._run_thread = threading.Thread(target=self._recv, daemon=True)

    @property
    def received(self) -> queue.Queue[bytes]:
        return self._received

    def start_main_thread(self) -> None:
        """ Start this client in the main thread"""
        self._recv()

    def connect(self, timeout: Optional[float] = None) -> None:
        self._connect_timeout = timeout
        connect_thread = threading.Thread(target=self._connect_to_server, args=(timeout,), daemon=True)
        connect_thread.start()

    def _connect_to_server(self, timeout: Optional[float] = None) -> None:
        super()._connect_to_server(timeout)
        if not self._connection_failed:
            self._buffer = Buffer(self._socket)

    def _recv(self):
        self._wait_for_connection.wait()
        if self._reconnect:
            while not self._stop_reconnect():
                while not self._stop():
                    error = receive_msg(
                        self._buffer,
                        self._received,
                        self.msg_end,
                        self._logger,
                        self.__class__.__name__
                    )
                    if error:
                        break
                self._connect_to_server(self._connect_timeout)
        else:
            while not self._stop():
                error = receive_msg(
                    self._buffer,
                    self._received,
                    self.msg_end,
                    self._logger,
                    self.__class__.__name__
                )
                if error:
                    break


class ClientSender(ClientBase):
    """ A client that sends messages to a server"""

    def __init__(
            self,
            address: tuple[str, int],
            to_send: Optional[queue.Queue[str]] = None,
            reconnect: bool = True,
            timeout: Optional[float] = None,
            stop: Optional[Callable[[], bool]] = lambda: False,
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
        self._run_thread = threading.Thread(target=self._send, daemon=True)

    @property
    def to_send(self) -> queue.Queue[str]:
        return self._to_send

    def _send(self) -> None:
        self._wait_for_connection.wait()
        if self._reconnect:
            while not self._stop_reconnect():
                while not self._stop():
                    error = send_msg(
                        self._socket,
                        self._to_send,
                        self.msg_end,
                        self._logger,
                        self.__class__.__name__
                    )
                    if error:
                        break
                self._connect_to_server(self._connect_timeout)
        else:
            while not self._stop():
                error = send_msg(
                    self._socket,
                    self._to_send,
                    self.msg_end,
                    self._logger,
                    self.__class__.__name__
                )
                if error:
                    break

    def start_main_thread(self) -> None:
        """ Start this client in the main thread"""
        self._send()


class Client(ClientBase):
    """ A client that sends and receives messages to and from a server.
    """

    def __init__(
            self,
            address: tuple[str, int],
            received: Optional[queue.Queue[bytes]] = None,
            to_send: Optional[queue.Queue[str]] = None,
            reconnect: bool = True,
            timeout: Optional[float] = None,
            stop_receive: Callable[[], bool] = lambda: False,
            stop_send: Callable[[], bool] = lambda: False,
            logger: Optional[logging.Logger] = None,
    ):
        super().__init__(address=address, reconnect=reconnect, timeout=timeout, logger=logger)
        self.msg_end = b"\r\n"
        self._buffer = None  # type: Optional[Buffer]

        self._received = received if received is not None else queue.Queue()
        self._to_send = to_send if to_send is not None else queue.Queue()
        self._stop_receive = stop_receive
        self._stop_send = stop_send

        self._send_thread = threading.Thread(target=self._send, daemon=True)
        self._recv_thread = threading.Thread(target=self._recv, daemon=True)

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

    def connect(self, timeout: Optional[float] = None) -> None:
        self._connect_timeout = timeout
        connect_thread = threading.Thread(target=self._connect_to_server, args=(timeout,), daemon=True)
        connect_thread.start()

    def _connect_to_server(self, timeout: Optional[float] = None) -> None:
        super()._connect_to_server(timeout)
        self._buffer = Buffer(self._socket)

    def _send(self) -> None:
        self._wait_for_connection.wait()
        if self._reconnect:
            while not self._stop_reconnect():
                while not self._stop_send():
                    error = send_msg(
                        self._socket,
                        self._to_send,
                        self.msg_end,
                        self._logger,
                        self.__class__.__name__
                    )
                    if error:
                        break
                self._wait_for_connection.clear()
                self._connect_to_server(self._connect_timeout)
        else:
            while not self._stop_send():
                error = send_msg(
                    self._socket,
                    self._to_send,
                    self.msg_end,
                    self._logger,
                    self.__class__.__name__
                )
                if error:
                    break

    def _recv(self) -> None:
        self._wait_for_connection.wait()
        if self._reconnect:
            while not self._stop_reconnect():
                while not self._stop_receive():
                    error = receive_msg(
                        self._buffer,
                        self._received,
                        self.msg_end,
                        self._logger,
                        self.__class__.__name__
                    )
                    if error:
                        self._wait_for_connection.clear()
                        break
                self._wait_for_connection.wait()
        else:
            while not self._stop_receive():
                error = receive_msg(
                    self._buffer,
                    self._received,
                    self.msg_end,
                    self._logger,
                    self.__class__.__name__
                )
                if error:
                    break

    def start(self) -> None:
        """ Start this client in a new thread. """
        self._recv_thread.start()
        self._send_thread.start()

    def join(self) -> None:
        self._recv_thread.join()
        self._send_thread.join()

    def shutdown(self) -> None:
        self._stop_send = lambda: True
        self._stop_receive = lambda: True
        self.join()


class ClientReportAlive(Client):
    """ Client that receives messages and sends and alive message periodically
        to the server
    """

    def _send_alive_message(self) -> None:
        while not self._stop_send():
            try:
                self._socket.sendall(b"Alive\r\n")
                # handle_msg_sent()
            except ConnectionError:
                if self._logger is not None:
                    self._logger.info(
                        f"{self.__class__.__name__} failed to send message. Connection lost")
                break
            time.sleep(30)

    def _send(self) -> None:
        if self._reconnect:
            while not self._stop_reconnect():
                self._send_alive_message()
                self._wait_for_connection.clear()
                self.connect()
        else:
            while not self._stop_send():
                self._send_alive_message()
