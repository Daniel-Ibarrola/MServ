from mserv.socketlib import Client
from mserv.utils.logger import get_module_logger
from services import MessageGenerator, MessageLogger


logger = get_module_logger(__name__, config="dev", use_file_handler=False)


def main():
    """ Client that sends and receives data from a server and should reconnect
        when the connexion is lost.
    """
    address = "localhost", 12345
    client = Client(address, reconnect=True)
    msg_logger = MessageLogger(client.received, logger)
    msg_gen = MessageGenerator(client.to_send, "Client")

    with client:
        client.connect()
        client.start()
        msg_logger.start()
        msg_gen.start()

        try:
            client.join()
        except KeyboardInterrupt:
            client.shutdown()
            msg_logger.shutdown()
            msg_gen.shutdown()

    logger.info("Graceful shutdown")


if __name__ == "__main__":
    main()
