import logging
import queue
import time

from mserv.services import AbstractService


class MessageLogger(AbstractService):

    def __init__(self, messages: queue.Queue, logger: logging.Logger):
        super().__init__(in_queue=messages, logger=logger)

    def _handle_message(self):
        while not self._stop():
            msg = self._in.get()
            self._logger.info(f"New message {msg}")


class MessageGenerator(AbstractService):

    def __init__(self, messages: queue.Queue, name: str):
        super().__init__(out_queue=messages)
        self.name = name

    def _handle_message(self):
        while not self._stop():
            count = 1
            msg = f"{self.name} {count}"
            self._out.put(msg)

            count += 1
            if count > 100:
                count = 1

            time.sleep(5)
