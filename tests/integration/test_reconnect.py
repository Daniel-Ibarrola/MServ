import queue
import pytest
import random
import threading
import time
from socketlib import (
    ClientSender,
    ClientReceiver,
    ServerReceiver,
    ServerSender,
    get_module_logger
)


def put_msgs_in_queue(messages: queue.Queue[str]) -> None:
    for ii in range(50):
        messages.put(f"msg {ii}")


class TestServerReconnects:

    address1 = "localhost", random.randint(1024, 49150)
    address2 = "localhost", random.randint(1024, 49150)
    logger = get_module_logger("Test", "dev", use_file_handler=False)

    def get_client_sender(self, msg: str) -> ClientSender:
        to_send = queue.Queue()
        to_send.put(msg)
        return ClientSender(
            address=self.address1,
            to_send=to_send,
            reconnect=False,
            timeout=0.2,
            stop=lambda: to_send.empty(),
            logger=self.logger
        )

    @pytest.fixture
    def client_senders(self) -> tuple[ClientSender, ClientSender]:
        client1 = self.get_client_sender("msg 1")
        client2 = self.get_client_sender("msg 2")

        yield client1, client2

        # Make sure connection is closed if test fails
        try:
            client1.close_connection()
            client2.close_connection()
        except OSError:
            pass

    @staticmethod
    def wait_for_client(client: ClientReceiver | ClientSender) -> None:
        client.connect()
        client.start()
        client.join()
        client.close_connection()

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

        self.wait_for_client(client1)

        time.sleep(0.2)

        self.wait_for_client(client2)

        server.join()
        assert not server.received.empty()
        assert server.received.get() == b"msg 1"
        assert server.received.get() == b"msg 2"

    def get_client_receiver(self) -> ClientReceiver:
        received = queue.Queue()
        return ClientReceiver(
            address=self.address2,
            received=received,
            timeout=1,
            reconnect=False,
            stop=lambda: received.qsize() > 0,
            logger=self.logger
        )

    @pytest.fixture()
    def client_receivers(self):
        client1 = self.get_client_receiver()
        client2 = self.get_client_receiver()

        yield client1, client2

        # Make sure connection is closed if test fails
        try:
            client1.close_connection()
            client2.close_connection()
        except OSError:
            pass

    @pytest.mark.timeout(3)
    def test_server_sender_can_reconnect_clients(self, client_receivers):
        client1, client2 = client_receivers

        to_send = queue.Queue()
        put_msgs_in_queue(to_send)  # Put many messages so there is a connection error

        stop_server = threading.Event()
        server = ServerSender(
            address=self.address2,
            to_send=to_send,
            reconnect=True,
            timeout=0.1,
            stop=lambda: stop_server.is_set(),
            stop_reconnect=lambda: stop_server.is_set(),
            logger=self.logger
        )
        server.start()
        self.wait_for_client(client1)
        assert not client1.received.empty()

        time.sleep(0.5)
        self.wait_for_client(client2)

        stop_server.set()
        server.join()

        assert not client2.received.empty()
        msg = client1.received.get().decode()
        assert "msg" in msg
        msg = client2.received.get().decode()
        assert "msg" in msg


class TestClientReconnects:

    address1 = "localhost", random.randint(1024, 49150)
    address2 = "localhost", random.randint(1024, 49150)
    logger = get_module_logger("Test", "dev", use_file_handler=False)

    def get_server_sender(self, msg: str) -> ServerSender:
        to_send = queue.Queue()
        to_send.put(msg)
        return ServerSender(
            address=self.address1,
            to_send=to_send,
            reconnect=False,
            timeout=0.2,
            stop=lambda: to_send.empty(),
            logger=self.logger
        )

    @pytest.fixture
    def server_senders(self) -> tuple[ServerSender, ServerSender]:
        server1 = self.get_server_sender("msg 1")
        server2 = self.get_server_sender("msg 2")

        yield server1, server2

        # Close connection in case test fails
        try:
            server1.close_connection()
            server2.close_connection()
        except OSError:
            pass

    @pytest.mark.timeout(3)
    def test_client_receiver_can_reconnect(self, server_senders):
        server1, server2 = server_senders
        received = queue.Queue()
        client = ClientReceiver(
            address=self.address1,
            received=received,
            reconnect=True,
            timeout=0.2,
            stop=lambda: received.qsize() > 1,
            stop_reconnect=lambda: received.qsize() > 1,
            logger=self.logger
        )

        server1.start()
        client.connect()
        client.start()

        server1.join()
        server1.close_connection()
        time.sleep(0.2)
        self.logger.info(f"Server 1 shutdown")
        assert not client.received.empty()

        server2.start()
        server2.join()
        server2.close_connection()

        client.join()
        assert not client.received.empty()
        assert client.received.get() == b"msg 1"
        assert client.received.get() == b"msg 2"

    def get_server_receiver(self):
        received = queue.Queue()
        return ServerReceiver(
            address=self.address1,
            received=received,
            reconnect=False,
            timeout=0.2,
            stop=lambda: received.qsize() > 0,
            logger=self.logger
        )

    @pytest.fixture
    def server_receivers(self):
        server1 = self.get_server_receiver()
        server2 = self.get_server_receiver()

        yield server1, server2

        # Close connection in case test fails
        try:
            server1.close_connection()
            server2.close_connection()
        except OSError:
            pass

    @pytest.mark.timeout(3)
    def test_client_sender_can_reconnect(self, server_receivers):
        to_send = queue.Queue()
        put_msgs_in_queue(to_send)

        stop = threading.Event()
        client = ClientSender(
            address=self.address1,
            to_send=to_send,
            reconnect=True,
            timeout=0.2,
            stop=lambda: stop.is_set(),
            stop_reconnect=lambda: stop.is_set(),
            logger=self.logger
        )
        client.connect_timeout = 0.3

        server1, server2 = server_receivers
        server1.start()
        client.connect()
        client.start()

        server1.join()
        server1.close_connection()
        self.logger.info("Server 1 shutdown")
        assert not server1.received.empty()
        assert not client.to_send.empty()

        time.sleep(0.2)  # Wait for client to call connect to server method

        server2.start()
        server2.join()
        server2.close_connection()

        stop.set()
        client.join()

        assert not server2.received.empty()

        msg = server1.received.get().decode()
        assert "msg" in msg
        msg = server2.received.get().decode()
        assert "msg" in msg
