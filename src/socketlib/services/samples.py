import logging
import queue
import time
from typing import Callable, Optional
from socketlib.services.abstract_service import AbstractService


class MessageLogger(AbstractService):

    def __init__(self, messages: queue.Queue, logger: logging.Logger):
        super().__init__(in_queue=messages, logger=logger)

    def _handle_message(self):
        while not self._stop():
            msg = self._in.get()
            self._logger.info(f"New message {msg}")


class MessageGenerator(AbstractService):

    def __init__(self, messages: queue.Queue, logger: logging.Logger, name: Optional[str] = ""):
        super().__init__(out_queue=messages, logger=logger)
        self.name = name

    def _handle_message(self):
        count = 1
        while not self._stop():
            msg = f"{self.name} {count}"
            self._out.put(msg)

            count += 1
            if count > 100:
                count = 1

            time.sleep(5)


class ToUpper(AbstractService):

    def __init__(
            self,
            msg_in: Optional[queue.Queue[str]] = None,
            msg_out: Optional[queue.Queue[str]] = None,
            stop: Optional[Callable[[], bool]] = lambda: False,
    ):
        super().__init__(msg_in, msg_out, stop)

    @property
    def msg_in(self) -> queue.Queue[str]:
        return self.in_queue

    @property
    def msg_out(self) -> queue.Queue[str]:
        return self.out_queue

    def _handle_message(self):
        while not self._stop():
            msg_lower = self.msg_in.get()
            self.msg_out.put(msg_lower.upper())
