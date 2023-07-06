import logging
import queue
from typing import Callable, Optional
from mserv.socketlib.buffer import Buffer


def get_msg(buffer: Buffer, msg_end: bytes) -> Optional[bytes]:
    try:
        return buffer.get_msg(msg_end=msg_end)
    except ConnectionError:
        return


def receive_msg(
        buffer: Buffer,
        msg_queue: queue.Queue,
        stop: Callable[[], bool],
        msg_end: bytes,
        logger: Optional[logging.Logger] = None
) -> None:
    # setup()
    while not stop():
        data = get_msg(buffer, msg_end)
        if data is not None:
            # handle_message_received(data)
            msg_queue.put(data)

    # teardown()
    if logger is not None:
        logger.debug("Receive thread stopped")
