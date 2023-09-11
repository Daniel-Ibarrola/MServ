from socketlib import Buffer
from .fake_socket import FakeSocket


class TestBuffer:

    def test_gets_small_message(self):
        sock = FakeSocket()
        sock.recv_data = b"Hello World\r\n"

        buffer = Buffer(sock)
        received = buffer.get_msg(b"\r\n")

        assert received == b"Hello World"

    def test_gets_very_large_message(self):
        msg = "HelloWorld" * 1000
        sock = FakeSocket()
        sock.recv_data = (msg + "\r\n").encode()

        buffer = Buffer(sock)
        received = buffer.get_msg(b"\r\n")

        assert received == msg.encode()
