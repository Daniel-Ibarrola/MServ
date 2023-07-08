import logging
import queue
import time

from mserv.services import AbstractService
from mserv.socketlib import (
    Client,
    ClientReceiver,
    ClientSender,
    Server,
    ServerReceiver,
    ServerSender,
)


class MessageLogger(AbstractService):

    def __init__(self, messages: queue.Queue, logger: logging.Logger):
        super().__init__(in_queue=messages, logger=logger)

    def _handle_message(self):
        while not self._stop():
            msg = self._in.get()
            self._logger.info(f"New message {msg}")


class MessageGenerator(AbstractService):

    def __init__(self, messages: queue.Queue, name: str, logger: logging.Logger):
        super().__init__(out_queue=messages, logger=logger)
        self.name = name

    def _handle_message(self):
        count = 1
        while not self._stop():
            msg = f"{self.name} {count}"
            self._out.put(msg)

            count += 1
            if count > 100:
                count = 1

            time.sleep(5)


def start_socket(
        address: tuple[str, int],
        client: bool,
        sock_type: str,
        logger: logging.Logger
) -> None:
    valid_types = ["multi", "receiver", "sender"]
    if client and sock_type == "client":
        sock_type = "multi"
    elif not client and sock_type == "server":
        sock_type = "multi"

    if sock_type not in valid_types:
        raise ValueError(f"Unexpected type {sock_type}")

    msg_logger = None
    msg_gen = None
    name = "Client" if client else "Server"

    if sock_type == "multi":
        if client:
            socket = Client(address, reconnect=True, logger=logger)
        else:
            socket = Server(address, reconnect=True, logger=logger)
        msg_logger = MessageLogger(socket.received, logger)
        msg_gen = MessageGenerator(socket.to_send, name, logger)

    elif sock_type == "receiver":
        if client:
            socket = ClientReceiver(address, reconnect=True, logger=logger)
        else:
            socket = ServerReceiver(address, reconnect=True, logger=logger)
        msg_logger = MessageLogger(socket.received, logger)

    elif sock_type == "sender":
        if client:
            socket = ClientSender(address, reconnect=True, logger=logger)
        else:
            socket = ServerSender(address, reconnect=True, logger=logger)
        msg_gen = MessageGenerator(socket.to_send, name, logger)

    else:
        raise ValueError(f"Unexpected type {sock_type}")

    with socket:
        if isinstance(socket,
                      (Client, ClientReceiver, ClientSender)):
            socket.connect()

        socket.start()
        if msg_logger is not None:
            msg_logger.start()

        if msg_gen is not None:
            msg_gen.start()

        try:
            socket.join()
        except KeyboardInterrupt:
            socket.shutdown()
            if msg_logger is not None:
                msg_logger.shutdown()
            if msg_gen is not None:
                msg_gen.shutdown()

    logger.info("Graceful shutdown")
