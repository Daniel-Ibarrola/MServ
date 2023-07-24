import logging
import queue
import socket
from typing import Callable, Optional

from socketlib.basic.queues import get_from_queue


def encode_msg(msg: str, msg_end: bytes = b"\r\n"):
    return msg.encode() + msg_end


def send_msg(
        sock: socket.socket,
        msg: str,
        msg_end: bytes = b"\r\n",
        logger: Optional[logging.Logger] = None,
        name: str = "",
) -> bool:
    """ Send a message through a socket. Returns true if there is an error
    """
    msg_bytes = encode_msg(msg, msg_end)
    try:
        sock.sendall(msg_bytes)
    except (ConnectionError, socket.timeout):
        if logger is not None:
            logger.info(f"{name} failed to send message. Connection lost")
        return True
    return False


def get_and_send_messages(
        sock: socket.socket,
        msg_end: bytes,
        msg_queue: queue.Queue[str],
        stop: Callable[[], bool],
        timeout: float,
        logger: Optional[logging.Logger] = None,
        name: str = "",
) -> None:
    """ Get messages from a queue and send them until the
        stop function evaluates to true.
    """
    while not stop():
        msg = get_from_queue(msg_queue, timeout=timeout)
        if msg is not None:
            error = send_msg(sock, msg, msg_end, logger, name)
            if error:
                break
