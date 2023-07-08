from mserv.utils.logger import get_module_logger
from services import start_socket
import sys

logger = get_module_logger(__name__, config="dev", use_file_handler=False)


def main():
    server_type = "server"
    logger.info("Server Program")
    if len(sys.argv) > 1:
        server_type = sys.argv[1].lower()
    address = "localhost", 12345
    start_socket(
        address,
        client=False,
        sock_type=server_type,
        logger=logger
    )


if __name__ == "__main__":
    main()
