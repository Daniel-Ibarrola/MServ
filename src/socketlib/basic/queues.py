import queue
from typing import Any, Optional


def get_from_queue(data_queue: queue, timeout: float) -> Optional[Any]:
    """ Get an item from the queue. If timeout expires and there is
        nothing in the queue returns None.
    """
    try:
        return data_queue.get(timeout=timeout)
    except queue.Empty:
        pass


def put_in_queue(data_queue: queue, timeout: float) -> bool:
    """ Put an item in the queue. If the operation was successful returns
        true, otherwise false.
    """
    try:
        data_queue.put(timeout=timeout)
        return True
    except queue.Full:
        return False
