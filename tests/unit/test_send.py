import queue
from socketlib.basic.send import get_and_send_messages
from .fake_socket import FakeSocket


def test_get_and_sends_str_message():
    socket = FakeSocket()
    messages = queue.Queue()
    messages.put("Hello World")
    assert not get_and_send_messages(
        socket, b"\r\n", messages, lambda: messages.empty(), 5.)
    assert socket.sent == [b"Hello World\r\n"]


def test_get_and_sends_bytes_message():
    socket = FakeSocket()
    messages = queue.Queue()
    messages.put(b"Hello World")
    assert not get_and_send_messages(
        socket, b"\r\n", messages, lambda: messages.empty(), 5.)
    assert socket.sent == [b"Hello World\r\n"]
