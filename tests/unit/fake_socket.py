

class FakeSocket:

    def __init__(self, family=None, type=None):
        self.family = family
        self.type = type
        self._connected = False

        self.recv_data = b""
        self._bytes_start = 0

        self.sent: list[bytes] = []

    def recv(self, bufsize: int) -> bytes:
        fragment = self.recv_data[self._bytes_start:self._bytes_start + bufsize]
        self._bytes_start += bufsize
        return fragment

    def connect(self, address: tuple[str, int]):
        self._connected = True

    def sendall(self, msg: bytes):
        self.sent.append(msg)
