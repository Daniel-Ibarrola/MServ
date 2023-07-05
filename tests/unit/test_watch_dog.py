import threading
import time
from mserv.utils import watch_dog


def function_that_raises_error():
    while True:
        time.sleep(2)
        raise ValueError


def test_calls_exit_when_a_thread_dies(mocker):
    mock_exit = mocker.patch("mserv.utils.watch_dog.os._exit")
    thread = threading.Thread(target=function_that_raises_error, daemon=True)

    dog = watch_dog.WatchDog()
    dog.threads["function"] = thread
    dog.wait = 0

    thread.start()
    dog.start()
    dog.join()

    mock_exit.assert_called_once()
