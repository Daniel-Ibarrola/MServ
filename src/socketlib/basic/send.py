import logging
import queue
import socket
from typing import Callable, Optional
import time

from socketlib.basic.queues import get_from_queue


def encode_msg(msg: str,
               msg_end: bytes = b"\r\n",
               encoding: str = "utf-8"
               ) -> bytes:
    return msg.encode(encoding) + msg_end


def send_msg(
        sock: socket.socket,
        msg: str | bytes,
        msg_end: bytes = b"\r\n",
        logger: Optional[logging.Logger] = None,
        name: str = "",
        encoding: str = "utf-8"
) -> bool:
    """ Send a message through a socket. Returns true if there is an error
    """
    if isinstance(msg, str):
        msg_bytes = encode_msg(msg, msg_end, encoding)
    else:
        msg_bytes = msg + msg_end

    error = ""
    try:
        sock.sendall(msg_bytes)
    except ConnectionError:
        error = f"{name} failed to send message. Connection lost"
    except socket.timeout:
        error = f"{name} failed to send message. Timed out"

    if error and logger is not None:
        logger.info(error)

    if error:
        return True
    return False


def get_and_send_messages(
        sock: socket.socket,
        msg_end: bytes,
        msg_queue: queue.Queue[str | bytes],
        stop: Callable[[], bool],
        timeout: float,
        logger: Optional[logging.Logger] = None,
        name: str = "",
        encoding: str = "utf-8",
        wait: float = 0,
) -> None:
    """ Get messages from a queue and send them until the
        stop function evaluates to true.
    """
    while not stop():
        # TODO: add a small (optional) wait period before sending messages
        msg = get_from_queue(msg_queue, timeout=timeout)
        if msg is not None:
            error = send_msg(sock, msg, msg_end, logger, name, encoding)
            time.sleep(wait)
            if error:
                break
