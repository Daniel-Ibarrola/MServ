from mserv.socketlib import MultiServerSender
from mserv.utils.logger import get_module_logger
from services import MessageGenerator

logger = get_module_logger(__name__, config="dev", use_file_handler=False)


def main():
    address = "localhost", 12345
    server = MultiServerSender(address)
    msg_gen = MessageGenerator(server.to_send, "MultiServer")

    with server:
        server.listen()
        server.start()
        msg_gen.start()

        try:
            server.join()
        except KeyboardInterrupt:
            server.shutdown()
            msg_gen.shutdown()

    logger.info("Graceful shutdown")


if __name__ == "__main__":
    main()
