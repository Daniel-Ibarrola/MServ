import queue
import logging
import socket
import threading
from typing import Callable, Optional


class ServerReceiver:
    """ A server that receives messages from a single client.
    """
    def __init__(
            self,
            address: tuple[str, int],
            received: Optional[queue.Queue[bytes]] = None,
            reconnect: bool = True,
            stop: Optional[Callable[[], bool]] = lambda: False,
            logger: Optional[logging.Logger] = None,
    ):
        pass


class ServerSender:
    """ A server that sends messages to a single client"""

    def __init__(
            self,
            address: tuple[str, int],
            to_send: Optional[queue.Queue[str]] = None,
            reconnect: bool = True,
            stop: Optional[Callable[[], bool]] = lambda: False,
            logger: Optional[logging.Logger] = None,
    ):
        self._address = address
        self._socket = None
        self._connection = None  # The client connection
        self._conn_details = None

        self._to_send = to_send
        self._reconnect = reconnect
        self._stop = stop
        self._logger = logger

        self._run_thread = threading.Thread(
            target=self._send, daemon=True
        )

    @property
    def ip(self) -> str:
        return self._address[0]

    @property
    def port(self) -> int:
        return self._address[1]

    @property
    def to_send(self) -> queue.Queue[str]:
        return self._to_send

    def start(self) -> None:
        self.listen()
        self._run_thread.start()

    def start_main_thread(self) -> None:
        self.listen()
        self._send()

    def _send(self):
        self.accept_connection()
        while not self._stop():
            msg = self.to_send.get()
            msg_bytes = self.encode_msg(msg, msg_end=b"\r\n")
            try:
                self._connection.sendall(msg_bytes)
            except ConnectionError:
                if self._logger is not None:
                    self._logger.info(f"Failed to send message. Connection lost")
                break

        if self._logger is not None:
            self._logger.debug("Send thread stopped")

    def listen(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(self._address)
        self._socket.listen()

    def accept_connection(self) -> None:
        self._connection, self._conn_details = self._socket.accept()
        if self._logger is not None:
            self._logger.info(
                f"{self.__class__.__name__}: "
                f"connection accepted from {self._conn_details}"
            )

    @staticmethod
    def encode_msg(msg: str, msg_end: bytes = b"\r\n"):
        return msg.encode() + msg_end

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self._connection is not None:
            self._connection.close()
        if self._socket is not None:
            self._socket.close()

    def join(self) -> None:
        self._run_thread.join()

    def shutdown(self) -> None:
        self._stop = lambda: True
        self.join()


class Server:
    """ A server that sends and receives messages to and from a single client.
    """
    pass
