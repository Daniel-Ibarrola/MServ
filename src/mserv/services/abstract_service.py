import abc
import logging
import queue
import threading
from typing import Any, Callable, Optional


class AbstractService(abc.ABC):
    """ Abstract base class for all services.

        To add a new service implement the _handle_message method.

        A service consists of an input queue and an output queue. The purpose
        of a service is to apply some function to the inputs to obtain
        the outputs that can then be processed by another service or send to a receptor.

        Most services are meant to run indefinitely, and so they do not run in the
        main thread. However, a custom function to terminate the service when needed
        can be used, and the service can also run in the main thread if necessary.
    """
    def __init__(
            self,
            in_queue: Optional[queue.Queue] = None,
            out_queue: Optional[queue.Queue] = None,
            stop: Callable[[], bool] = lambda: False,
            events: Optional[dict[str, threading.Event]] = None,
            logger: Optional[logging.Logger] = None,
    ):
        # Main thread of this service
        self._in = in_queue if in_queue is not None else queue.Queue()
        self._out = out_queue if out_queue is not None else queue.Queue()
        self._events = events if events is not None else dict()
        self._logger = logger

        self._process_thread = threading.Thread(
            target=self._handle_message,
            daemon=True
        )
        self._stop = stop

    @property
    def process_thread(self) -> threading.Thread:
        return self._process_thread

    @property
    def in_queue(self) -> queue.Queue:
        return self._in

    @property
    def out_queue(self) -> queue.Queue:
        return self._out

    @abc.abstractmethod
    def _handle_message(self):
        raise NotImplementedError

    def start_main_thread(self):
        """ Starts this service in the main thread. """
        self._handle_message()

    def start(self) -> None:
        self._process_thread.start()
        if self._logger is not None:
            self._logger.debug(f"Started {self.__class__.__name__}")

    def join(self) -> None:
        self._process_thread.join()

    def shutdown(self) -> None:
        self._stop = lambda: True
        self.join()
        if self._logger is not None:
            self._logger.debug(f"Shutting down {self.__class__.__name__}")

    @staticmethod
    def _get_from_queue(data_queue: queue, timeout: float) -> Optional[Any]:
        """ Get an item from the queue. If timeout expires and there is
            nothing in the queue returns None.
        """
        try:
            return data_queue.get(timeout=timeout)
        except queue.Empty:
            pass
