import logging
import queue
from typing import Optional
from socketlib.basic.buffer import Buffer


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
    """ Receive a message from a socket and put it in a queue.

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
