import logging
import threading
import time
import os
from typing import Optional


class WatchDog:
    """ Verifies that all threads are running.
    """
    def __init__(
            self,
            threads: dict[str, threading.Thread] = None,
            logger: Optional[logging.Logger] = None
    ):
        if threads is None:
            self.threads = {}  # type: dict[str, threading.Thread]
        else:
            self.threads = threads

        self.check_thread = threading.Thread(target=self.check_threads, daemon=True)
        self.wait = 5
        self._stop = False
        self._logger = logger

    def check_threads(self):
        # TODO: remove exit flag. Exit with return
        exit_ = False
        while not self._stop:
            for thread_name, thread in self.threads.items():
                if not thread.is_alive():
                    # TODO: should check only after all threads have started
                    if self._logger is not None:
                        self._logger.info(f"Thread {thread_name} is dead")
                    exit_ = True

            if exit_:
                break

            time.sleep(self.wait)

        if exit_:
            if self._logger is not None:
                self._logger.info("Some threads are dead. Exiting...")
            time.sleep(2)
            # Exit application
            os._exit(1)

    def start(self):
        self.check_thread.start()

    def join(self):
        self.check_thread.join()

    def shutdown(self):
        self._stop = True
        self.join()
