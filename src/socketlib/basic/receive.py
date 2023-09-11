import logging
import queue
import socket
from typing import Callable, Optional

from socketlib.basic.buffer import Buffer
from socketlib.basic.queues import put_in_queue


def get_msg(
        buffer: Buffer,
        msg_end: bytes,
        logger: Optional[logging.Logger] = None,
        name: str = ""
) -> Optional[bytes]:
    """ Get a message from a socket buffer.
    """
    try:
        return buffer.get_msg(msg_end=msg_end)
    except ConnectionError:
        error = f"{name} failed to get message. Connection lost"
    except socket.timeout:
        error = f"{name} failed to get message. Timed out"

    if error and logger:
        logger.info(error)


def receive_and_enqueue(
        buffer: Buffer,
        msg_end: bytes,
        msg_queue: queue.Queue[bytes],
        stop: Callable[[], bool],
        timeout: float,
        logger: Optional[logging.Logger] = None,
        name: str = "",
):
    """ Receive a message and put it in a queue
    """
    while not stop():
        msg = get_msg(buffer, msg_end, logger, name)
        if msg is not None:
            success = put_in_queue(msg, msg_queue, timeout)
            if not success and logger:
                logger.info(f"{name} failed to enqueue message")
        else:
            break
