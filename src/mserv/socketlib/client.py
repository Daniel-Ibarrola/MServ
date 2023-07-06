import logging
import queue
import socket
import struct
import threading
import time
from typing import Callable, Optional

from mserv.socketlib.buffer import Buffer
from mserv.socketlib.send import send_msg
from mserv.socketlib.receive import receive_msg


class ClientBase:
    """ Parent class for other client classes that implements some common methods.

        This class should not be instantiated.
    """

    def __init__(
            self,
            address: tuple[str, int],
            reconnect: bool = True,
            stop: Optional[Callable[[], bool]] = lambda: False,
            logger: Optional[logging.Logger] = None,
    ):
        self._address = address
        self._socket = None
        self._reconnect = reconnect
        self._stop = stop
        self._logger = logger

        self._run_thread = threading.Thread()

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
        """ Connect to the server. """
        # TODO: reconnect
        start = time.time()
        if timeout is None:
            timeout = float("inf")

        error = False
        while time.time() - start <= timeout:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self._socket.connect((self.ip, self.port))
                error = False
                break
            except ConnectionError:
                error = True
                time.sleep(1)

        if error:
            raise ConnectionError(
                f"{self.__class__.__name__}: "
                f"failed to establish connection to {(self.ip, self.port)}"
            )

        if self._logger is not None and not error:
            self._logger.info(
                f"{self.__class__.__name__}: connected to {(self.ip, self.port)}"
            )

    def set_timeout(self, timeout: float):
        """ Set a timeout for sending and receiving messages.
        """
        timeval = struct.pack("ll", timeout, 0)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, timeval)

    def start(self) -> None:
        """ Start this client in a new thread. """
        self._run_thread.start()

    def join(self) -> None:
        self._run_thread.join()

    def shutdown(self) -> None:
        self._stop = lambda: True
        self.join()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self._socket is not None:
            self._socket.close()


class ClientReceiver(ClientBase):
    """ A client that receives messages from a server."""

    def __init__(
            self,
            address: tuple[str, int],
            received: Optional[queue.Queue[bytes]] = None,
            reconnect: bool = True,
            stop: Optional[Callable[[], bool]] = lambda: False,
            logger: Optional[logging.Logger] = None,
    ):
        super().__init__(address, reconnect, stop, logger)
        self.msg_end = b"\r\n"
        self._buffer = None  # type: Buffer
        self._received = received if received is not None else queue.Queue()
        self._run_thread = threading.Thread(target=self._recv, daemon=True)

    @property
    def received(self) -> queue.Queue[bytes]:
        return self._received

    def start_main_thread(self) -> None:
        """ Start this client in the main thread"""
        self._recv()

    def connect(self, timeout: Optional[float] = None) -> None:
        super().connect(timeout)
        self._buffer = Buffer(self._socket)

    def _recv(self):
        receive_msg(
            self._buffer,
            self._received,
            self._stop,
            self.msg_end,
            self._logger
        )


class ClientSender(ClientBase):
    """ A client that sends messages to a server"""

    def __init__(
            self,
            address: tuple[str, int],
            to_send: Optional[queue.Queue[str]] = None,
            reconnect: bool = True,
            stop: Optional[Callable[[], bool]] = lambda: False,
            logger: Optional[logging.Logger] = None,
    ):
        super().__init__(address, reconnect, stop, logger)
        self.msg_end = b"\r\n"
        self._to_send = to_send if to_send is not None else queue.Queue()
        self._run_thread = threading.Thread(target=self._send, daemon=True)

    @property
    def to_send(self) -> queue.Queue[str]:
        return self._to_send

    def _send(self) -> None:
        send_msg(
            self._socket,
            self._to_send,
            self._stop,
            self.msg_end,
            self._logger
        )

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
            stop_receive: Optional[Callable[[], bool]] = lambda: False,
            stop_send: Optional[Callable[[], bool]] = lambda: False,
            logger: Optional[logging.Logger] = None,
    ):
        super().__init__(address, reconnect, logger=logger)
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
        # TODO: connect can run in another thread
        super().connect(timeout)
        self._buffer = Buffer(self._socket)

    def _send(self) -> None:
        send_msg(
            self._socket,
            self._to_send,
            self._stop_send,
            self.msg_end,
            self._logger,
            self.__class__.__name__
        )

    def _recv(self):
        receive_msg(
            self._buffer,
            self._received,
            self._stop_receive,
            self.msg_end,
            self._logger,
            self.__class__.__name__
        )

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
