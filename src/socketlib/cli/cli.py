import argparse
import logging
import queue

from socketlib.services.samples import MessageGenerator, MessageLogger
from socketlib import (
    Client,
    ClientReceiver,
    ClientSender,
    Server,
    ServerReceiver,
    ServerSender,
)
from socketlib.utils.logger import get_module_logger


def start_socket(
        address: tuple[str, int],
        client: bool,
        sock_type: str,
        reconnect: bool,
        timeout: float,
        messages: list[str],
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

    if name == "Client":
        logger.info(f"{name} will connect to {address}")
    else:
        logger.info(f"{name} will listen for connections in {address}")

    if sock_type == "multi":
        if client:
            socket = Client(
                address,
                reconnect=reconnect,
                timeout=timeout,
                logger=logger
            )
        else:
            socket = Server(
                address,
                reconnect=reconnect,
                timeout=timeout,
                logger=logger
            )
        msg_logger = MessageLogger(socket.received, logger)
        msg_gen = MessageGenerator(socket.to_send, name=name, logger=logger)

    elif sock_type == "receiver":
        if client:
            socket = ClientReceiver(
                address,
                reconnect=reconnect,
                timeout=timeout,
                logger=logger
            )
        else:
            socket = ServerReceiver(
                address,
                reconnect=reconnect,
                timeout=timeout,
                logger=logger
            )
        msg_logger = MessageLogger(socket.received, logger)

    elif sock_type == "sender":
        if not messages:
            if client:
                socket = ClientSender(
                    address,
                    reconnect=reconnect,
                    timeout=timeout,
                    logger=logger
                )
            else:
                socket = ServerSender(
                    address,
                    reconnect=reconnect,
                    timeout=timeout,
                    logger=logger
                )
            msg_gen = MessageGenerator(socket.to_send, name=name, logger=logger)
        else:
            to_send = queue.Queue()
            for msg in messages:
                to_send.put(msg)
            if client:
                socket = ClientSender(
                    address,
                    to_send=to_send,
                    reconnect=False,
                    timeout=timeout,
                    stop=lambda: to_send.empty(),
                    logger=logger
                )
            else:
                socket = ServerSender(
                    address,
                    to_send=to_send,
                    reconnect=False,
                    timeout=timeout,
                    stop=lambda: to_send.empty(),
                    logger=logger
                )

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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a socket client or a socket server")

    parser.add_argument(
        "--ip",
        "-i",
        type=str,
        default="localhost",
        help="The ip where the client will connect or where the server will connect"
             " (default localhost)."
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=12345,
        help="The port where the client will connect or where the server will connect"
             " (default 12345)."
    )
    parser.add_argument(
        "--server",
        "-s",
        action="store_true",
        help="If this flag is passed a server will be started. If not a client."
    )
    parser.add_argument(
        "--type",
        "-t",
        type=str,
        choices=["multi", "receiver", "sender"],
        default="multi",
        help="The type of the server or client. Can be multi, receiver or sender"
             " (default multi)."
    )
    parser.add_argument(
        "--reconnect",
        "-r",
        action="store_true",
        help="Whether the client or server should try to reconnect if the connection is lost."
    )
    parser.add_argument(
        "--timeout",
        "-o",
        type=float,
        default=5,
        help="Timeout in seconds for socket receive and send operations."
             " (default (5 seconds)"
    )
    parser.add_argument(
        "--messages",
        "-m",
        type=str,
        nargs="+",
        help="A set of messages that will be sent by a client sender or server sender."
             " The program will exit after sending all messages. "
    )

    args = parser.parse_args()
    address = (args.ip, args.port)
    return address, args.server, args.type, args.reconnect, args.timeout, args.messages


def main():
    address, server, sock_type, reconnect, timeout, messages = parse_args()
    logger = get_module_logger(__name__, config="dev", use_file_handler=False)
    start_socket(
        address,
        client=not server,
        sock_type=sock_type,
        reconnect=reconnect,
        timeout=timeout,
        messages=messages,
        logger=logger
    )


if __name__ == "__main__":
    main()
