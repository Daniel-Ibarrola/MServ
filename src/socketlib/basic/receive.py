import logging
import queue
from typing import Callable, Optional

from socketlib.basic.buffer import Buffer
from socketlib.basic.queues import put_in_queue


def get_msg(buffer: Buffer, msg_end: bytes) -> Optional[bytes]:
    """ Get a message from a socket buffer.
    """
    try:
        return buffer.get_msg(msg_end=msg_end)
    except ConnectionError:
        return


def receive_msg(
        buffer: Buffer,
        msg_queue: queue.Queue,
        msg_end: bytes,
        logger: Optional[logging.Logger] = None,
        name: str = ""
) -> bool:
    """ Receive a message from a socket.

        Returns True if there is an error.
    """
    data = get_msg(buffer, msg_end)
    if data is not None:
        # handle_message_received(data)
        # TODO: add timeout to put
        msg_queue.put(data)
    else:
        if logger:
            logger.info(f"{name} failed to receive message")
        return True
    return False


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
        msg = get_msg(buffer, msg_end)
        if msg is not None:
            success = put_in_queue(msg, msg_queue, timeout)
            if not success and logger:
                logger.info(f"{name} failed to enqueue message")
        else:
            if logger:
                logger.info(f"{name} failed to receive message")
            break
