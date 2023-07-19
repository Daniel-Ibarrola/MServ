import logging
import queue
import socket
from typing import Optional


def encode_msg(msg: str, msg_end: bytes = b"\r\n"):
    return msg.encode() + msg_end


def send_msg(
        sock: socket.socket,
        msg_queue: queue.Queue,
        msg_end: bytes = b"\r\n",
        logger: Optional[logging.Logger] = None,
        name: str = "",
) -> bool:
    """ Send a message through a socket. Returns true if there is an error
    """
    msg = msg_queue.get()
    msg_bytes = encode_msg(msg, msg_end)
    try:
        sock.sendall(msg_bytes)
        # handle_msg_sent()
    except (ConnectionError, socket.timeout):
        if logger is not None:
            logger.info(f"{name} failed to send message. Connection lost")
        return True
    return False
