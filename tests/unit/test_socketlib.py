from socketlib import Buffer


class FakeSocket:

    def __init__(self, family=None, type=None):
        self.family = family
        self.type = type
        self._connected = False

        self.received = b""
        self.sent = b""

        self.recv_data = b""
        self._bytes_start = 0

    def recv(self, bufsize: int) -> bytes:
        fragment = self.recv_data[self._bytes_start:self._bytes_start + bufsize]
        self._bytes_start += bufsize
        return fragment

    def connect(self, address: tuple[str, int]):
        self._connected = True

    def sendall(self, msg: bytes):
        pass


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
