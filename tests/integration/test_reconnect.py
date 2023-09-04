import queue
import pytest
import random
import time
from socketlib import ServerReceiver, ClientSender, get_module_logger


class TestServerSenderReconnects:

    address1 = "localhost", random.randint(1024, 49150)
    logger = get_module_logger("Test", "dev", use_file_handler=False)

    def get_client_sender(self, msg: str) -> ClientSender:
        to_send = queue.Queue()
        to_send.put(msg)
        client = ClientSender(
            address=self.address1,
            to_send=to_send,
            reconnect=False,
            timeout=0.2,
            stop=lambda: to_send.empty(),
            logger=self.logger
        )

        return client

    @pytest.fixture
    def client_senders(self) -> tuple[ClientSender, ClientSender]:
        client1 = self.get_client_sender("msg 1")
        client2 = self.get_client_sender("msg 2")

        yield client1, client2

        client1.close_connection()
        client2.close_connection()

    @pytest.mark.timeout(3)
    def test_server_receiver_can_reconnect_clients(self, client_senders):
        client1, client2 = client_senders

        received = queue.Queue()
        server = ServerReceiver(
            address=self.address1,
            received=received,
            reconnect=True,
            timeout=0.2,
            stop=lambda: received.qsize() == 2,
            stop_reconnect=lambda: received.qsize() == 2,
            logger=self.logger
        )
        server.start()

        client1.connect()
        client1.start()
        client1.join()

        time.sleep(0.2)

        client2.connect()
        client2.start()
        client2.join()

        server.join()
        assert not server.received.empty()
        assert server.received.get() == b"msg 1"
        assert server.received.get() == b"msg 2"

    def test_server_sender_can_reconnect_clients(self):
        pass
