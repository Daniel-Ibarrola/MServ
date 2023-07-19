from queue import Queue
from socketlib.services.samples import ToUpper


def test_to_upper():
    """ Tests sample service that transform all input messages to uppercase
    """
    msg_in = Queue()
    to_upper = ToUpper(
        msg_in=msg_in,
        stop=lambda: msg_in.empty()
    )
    to_upper.msg_in.put("hello")
    to_upper.msg_in.put("world")

    to_upper.start()
    to_upper.join()
    assert msg_in.empty()

    assert to_upper.msg_out.get() == "HELLO"
    assert to_upper.msg_out.get() == "WORLD"
    assert to_upper.msg_out.empty()
