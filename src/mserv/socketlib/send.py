import logging
import queue
import socket
from typing import Callable, Optional


def encode_msg(msg: str, msg_end: bytes = b"\r\n"):
    return msg.encode() + msg_end


def send_msg(
        sock: socket.socket,
        msg_queue: queue.Queue,
        stop: Callable[[], bool],
        msg_end: bytes = b"\r\n",
        logger: Optional[logging.Logger] = None,
        name: str = "",
) -> None:
    # setup()
    while not stop():
        msg = msg_queue.get()
        msg_bytes = encode_msg(msg, msg_end)
        try:
            sock.sendall(msg_bytes)
            # handle_msg_sent()
        except ConnectionError:
            if logger is not None:
                logger.info(f"{name} failed to send message. Connection lost")
            break

    # teardown()
    if logger is not None:
        logger.debug("Send thread stopped")
