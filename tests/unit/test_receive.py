import queue
from socketlib.basic.receive import receive_and_enqueue
from socketlib import Buffer
from .fake_socket import FakeSocket


def test_receive_and_enqueue():
    socket = FakeSocket()
    socket.recv_data = b"Hello World\r\n"
    buffer = Buffer(socket)
    messages = queue.Queue()
    receive_and_enqueue(
        buffer, b"\r\n", messages, lambda: messages.qsize() > 0, 5.)

    assert not messages.empty()
    assert messages.get() == b"Hello World"
