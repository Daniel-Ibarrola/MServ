import sys
from mserv.utils.logger import get_module_logger
from services import start_socket


logger = get_module_logger(__name__, config="dev", use_file_handler=False)


def main():
    client_type = "client"
    logger.info("Client Program")
    if len(sys.argv) > 1:
        client_type = sys.argv[1].lower()
    address = "localhost", 12345
    start_socket(
        address,
        client=True,
        sock_type=client_type,
        logger=logger
    )


if __name__ == "__main__":
    main()
