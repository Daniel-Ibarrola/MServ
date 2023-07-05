import socket
from typing import Optional


class Buffer:

    def __init__(self, sock: socket.socket):
        self.socket = sock
        self.buffer = b''

    def get_msg(self, msg_end: bytes = b"\r\n") -> Optional[bytes]:
        """ Get a message from the socket until the end of message is reached.
        """
        while msg_end not in self.buffer:
            data = self.socket.recv(1024)
            if not data:  # socket closed
                return None
            self.buffer += data
        msg, sep, self.buffer = self.buffer.partition(b'\r\n')
        return msg
