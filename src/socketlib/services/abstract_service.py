import abc
import logging
import queue
import threading
from typing import Callable, Optional


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
            stop: Optional[Callable[[], bool]] = None,
            events: Optional[dict[str, threading.Event]] = None,
            logger: Optional[logging.Logger] = None,
    ):
        """Initialize the AbstractService.

            :param in_queue: Input queue for receiving messages.
            :param out_queue: Output queue for sending messages.
            :param stop: Custom stop function.
            :param events: Dictionary of events.
            :param logger: Logger for logging events.
        """
        self._in = in_queue if in_queue is not None else queue.Queue()
        self._out = out_queue if out_queue is not None else queue.Queue()
        self._events = events if events is not None else dict()
        self._logger = logger

        self._process_thread = threading.Thread(
            target=self._handle_message,
            daemon=True
        )
        self._stop_event = threading.Event()
        self._stop = self._get_stop_function(stop, self._stop_event)

    @property
    def process_thread(self) -> threading.Thread:
        """The thread responsible for processing messages."""
        return self._process_thread

    @property
    def in_queue(self) -> queue.Queue:
        """The input queue for receiving messages."""
        return self._in

    @property
    def out_queue(self) -> queue.Queue:
        return self._out

    @abc.abstractmethod
    def _handle_message(self):
        """Abstract method to handle incoming messages."""
        raise NotImplementedError

    def start_main_thread(self):
        """ Starts this service in the main thread. """
        self._handle_message()

    def start(self) -> None:
        """Starts the service by launching the processing thread."""
        self._process_thread.start()
        if self._logger is not None:
            self._logger.debug(f"Started {self.__class__.__name__}")

    def join(self) -> None:
        """Waits for the processing thread to finish."""
        self._process_thread.join()

    @staticmethod
    def _get_stop_function(
            stop: Optional[Callable[[], bool]],
            stop_event: threading.Event
    ) -> Callable[[], bool]:
        """Returns a stop function based on the provided arguments."""
        if stop is None:
            return lambda: stop_event.is_set()
        return stop

    def shutdown(self) -> None:
        """Shuts down the service gracefully."""
        self._stop_event.set()
        self.join()
        if self._logger is not None:
            self._logger.debug(f"Shutting down {self.__class__.__name__}")
