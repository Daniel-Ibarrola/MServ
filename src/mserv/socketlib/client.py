import logging
import queue
import socket
import struct
import threading
import time
from typing import Callable, Optional

from mserv.socketlib.buffer import Buffer


class ClientBase:

    def __init__(
            self,
            address: tuple[str, int],
            reconnect: bool = True,
            logger: Optional[logging.Logger] = None,
    ):
        self._address = address
        self._socket = None
        self._reconnect = reconnect
        self._logger = logger

    @property
    def ip(self) -> str:
        return self._address[0]

    @property
    def port(self) -> int:
        return self._address[1]

    def connect(self, timeout: Optional[float] = None) -> None:
        """ Connect to the server. """
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
        super().__init__(address, reconnect, logger)
        self.msg_end = b"\r\n"
        self._buffer = None  # type: Buffer
        self._received = received if received is not None else queue.Queue()
        self._stop = stop

        self._run_thread = threading.Thread(target=self._recv, daemon=True)

    @property
    def received(self) -> queue.Queue[bytes]:
        return self._received

    @property
    def run_thread(self) -> threading.Thread:
        return self._run_thread

    def start(self) -> None:
        """ Start this client in a new thread. """
        self._run_thread.start()

    def start_main_thread(self) -> None:
        """ Start this client in the main thread"""
        self._recv()

    def connect(self, timeout: Optional[float] = None) -> None:
        super().connect(timeout)
        self._buffer = Buffer(self._socket)

    def _recv(self):
        while not self._stop():
            data = self._get_msg()
            if data is not None:
                self._received.put(data)

        if self._logger is not None:
            self._logger.debug("Receive thread stopped")

    def _get_msg(self) -> Optional[bytes]:
        try:
            return self._buffer.get_msg(msg_end=self.msg_end)
        except ConnectionError:
            return

    def join(self) -> None:
        self._run_thread.join()

    def shutdown(self) -> None:
        self._stop = lambda: True
        self.join()


class ClientSender(ClientBase):
    """ A client that sends messages to a server"""
    pass


class Client(ClientBase):
    """ A client that sends and receives messages to and from a server.
    """
    pass
