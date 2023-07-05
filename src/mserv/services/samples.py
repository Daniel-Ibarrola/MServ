import queue
from mserv.services.abstract_service import AbstractService
from typing import Callable, Optional


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
