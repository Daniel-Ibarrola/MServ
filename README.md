# PySockLib

Helper library to implement socket client and servers as well as services to process, store, or 
send data received or send trough sockets.

## Installation

Create a virtual environment and activate it:

```shell
python3.11 -m venv venv
source venv/bin/activate
```

Install the latest version:

```shell
pip install pysocklib
```

## Python module

The python module contains several classes to easily implement client and/or server
programs. All available classes are listed below.

### ServerReceiver

A server that receives messages from a single client.

#### Constructor

```python
def __init__(
    self,
    address: tuple[str, int],
    received: Optional[queue.Queue[bytes]] = None,
    reconnect: bool = True,
    timeout: Optional[float] = None,
    stop: Optional[Callable[[], bool]] = None,
    stop_reconnect: Optional[Callable[[], bool]] = None,
    logger: Optional[logging.Logger] = None,
)
```

- `address`: A tuple representing the IP address and port number to bind the server to.
- `received`: Optional queue to store received messages.
- `reconnect`: If True, the server will attempt to reconnect after disconnection.
- `timeout`: Optional timeout value for send and receive operations.
- `stop`: A function that returns True to signal the server to stop.
- `stop_reconnect`: A function that returns True to signal the reconnecting loop to stop. Won't have
any effect if reconnect is set to False.
- `logger`: Optional logger for logging server events.

#### Properties
- `ip`: The IP address component of the server's address.
- `port`: The port number component of the server's address.
- `received`: The queue containing received messages.

#### Methods
- `listen()`: Creates the socket and puts it in listen mode.
- `accept_connection()`: Accepts a new connection.
- `start()`: Starts the server in a new thread.
- `join()`: Waits for the server thread to finish.
- `shutdown()`: Signals the server to shut down gracefully.
- `close_connection()`: Closes the client connection and the socket.
- `__enter__()`: Context manager entry point.
- `__exit__(...)`: Context manager exit point. Closes all sockets

### ServerSender

#### Constructor

```python
def __init__(
    self,
    address: tuple[str, int],
    to_send: Optional[queue.Queue[str | bytes]] = None,
    reconnect: bool = True,
    timeout: Optional[float] = None,
    stop: Optional[Callable[[], bool]] = None,
    stop_reconnect: Optional[Callable[[], bool]] = None,
    logger: Optional[logging.Logger] = None,
)
```

- `address`: A tuple representing the IP address and port number to bind the server to.
- `to_send`: Optional queue to store messages that will be sent.
- `reconnect`: If True, the server will attempt to reconnect after disconnection.
- `timeout`: Optional timeout value for send and receive operations.
- `stop`: A function that returns True to signal the server to stop.
- `stop_reconnect`: A function that returns True to signal the reconnecting loop to stop. Won't have
any effect if reconnect is set to False.
- `logger`: Optional logger for logging server events.

#### Properties
- `ip`: The IP address component of the server's address.
- `port`: The port number component of the server's address.
- `to_send`: The queue containing messages to be sent.

#### Methods
- `listen()`: Creates the socket and puts it in listen mode.
- `accept_connection()`: Accepts a new connection.
- `start()`: Starts the server in a new thread.
- `join()`: Waits for the server thread to finish.
- `shutdown()`: Signals the server to shut down gracefully.
- `close_connection()`: Closes the client connection and the socket.
- `__enter__()`: Context manager entry point.
- `__exit__(...)`: Context manager exit point. Closes all sockets

### Server

A server that sends and receives messages to and from a single client.
This server runs in two threads, one to send messages and another to receive messages.

```Python
def __init__(
    self,
    address: tuple[str, int],
    received: Optional[queue.Queue[bytes]] = None,
    to_send: Optional[queue.Queue[str | bytes]] = None,
    reconnect: bool = True,
    timeout: Optional[float] = None,
    stop_receive: Optional[Callable[[], bool]] = None,
    stop_send: Optional[Callable[[], bool]] = None,
    stop_reconnect: Optional[Callable[[], bool]] = None,
    logger: Optional[logging.Logger] = None,
)

```

- `address`: A tuple representing the IP address and port number to bind the server to.
- `received`: Optional queue to store received messages.
- `to_send`: Optional queue containing messages to be sent.
- `reconnect`: If True, the server will attempt to reconnect after disconnection.
- `timeout`: Optional timeout value for send and receive operations.
- `stop_receive`:  A function that returns True to signal the receiving loop to stop.
- `stop_send`:  A function that returns True to signal the sending loop to stop.
- `stop_reconnect`: A function that returns True to signal the reconnecting loop to stop. Won't have
any effect if reconnect is set to False.
- `logger`: Optional logger for logging server events.

#### Properties
- `received`: The queue containing received messages.
- `to_send`: The queue containing messages to be sent.
- `send_thread`: The thread responsible for sending messages.
- `receive_thread`: The thread responsible for receiving messages.

#### Methods
- `listen()`: Creates the socket and puts it in listen mode.
- `accept_connection()`: Accepts a new connection.
- `start()`: Starts the server in a new thread.
- `join()`: Waits for both the sending and receiving threads to stop.
- `shutdown()`: Signals the server to shut down gracefully.
- `close_connection()`: Closes the client connection and the socket.
- `__enter__()`: Context manager entry point.
- `__exit__(...)`: Context manager exit point. Closes all sockets

### ClientReceiver

A client that receives messages from a server.

#### Constructor

```python
def __init__(
    self,
    address: tuple[str, int],
    received: Optional[queue.Queue[bytes]] = None,
    reconnect: bool = True,
    timeout: Optional[float] = None,
    stop: Optional[Callable[[], bool]] = None,
    stop_reconnect: Optional[Callable[[], bool]] = None,
    logger: Optional[logging.Logger] = None,
)
```

- `address`: A tuple representing the IP address and port number to connect to.
- `received`: Optional queue to store received messages.
- `reconnect`: If True, the client will attempt to reconnect after disconnection.
- `timeout`: Optional timeout value for send and receive operations.
- `stop`: A function that returns True to signal the client to stop.
- `stop_reconnect`: A function that returns True to signal the reconnecting loop to stop. Won't have
any effect if reconnect is set to False.
- `logger`: Optional logger for logging client events.

#### Properties

- `ip`: The IP address component of the client's address.
- `port`: The port number component of the client's address.
- `received`: The queue containing received messages.

#### Methods
- `connect(timeout: Optional[float] = None)`: Connects to the server with an optional timeout.
- `start()`: Starts the client in a new thread.
- `join()`: Waits for the client thread to finish.
- `shutdown()`: Signals the client to shut down gracefully.
- `close_connection()`: Closes the socket connection.
- `__enter__()`: Context manager entry point.
- `__exit__(...)`: Context manager exit point.

### ClientSender

```python
def __init__(
    self,
    address: tuple[str, int],
    to_send: Optional[queue.Queue[bytes | bytes]] = None,
    reconnect: bool = True,
    timeout: Optional[float] = None,
    stop: Optional[Callable[[], bool]] = None,
    stop_reconnect: Optional[Callable[[], bool]] = None,
    logger: Optional[logging.Logger] = None,
)
```

- `address`: A tuple representing the IP address and port number to connect to.
- `to_send`: Optional queue to store messages to be sent.
- `reconnect`: If True, the client will attempt to reconnect after disconnection.
- `timeout`: Optional timeout value for send and receive operations.
- `stop`: A function that returns True to signal the client to stop.
- `stop_reconnect`: A function that returns True to signal the reconnecting loop to stop. Won't have
any effect if reconnect is set to False.
- `logger`: Optional logger for logging client events.

#### Properties

- `ip`: The IP address component of the client's address.
- `port`: The port number component of the client's address.
- `to_send`: The queue containing messages to be sent.

#### Methods
- `connect(timeout: Optional[float] = None)`: Connects to the server with an optional timeout.
- `start()`: Starts the client in a new thread.
- `join()`: Waits for the client thread to finish.
- `shutdown()`: Signals the client to shut down gracefully.
- `close_connection()`: Closes the socket connection.
- `__enter__()`: Context manager entry point.
- `__exit__(...)`: Context manager exit point.

### Client

A client that sends and receives messages to and from a server.

```python
def __init__(
    self,
    address: tuple[str, int],
    received: Optional[queue.Queue[bytes]] = None,
    to_send: Optional[queue.Queue[str | bytes]] = None,
    reconnect: bool = True,
    timeout: Optional[float] = None,
    stop_receive: Callable[[], bool] = None,
    stop_send: Callable[[], bool] = None,
    stop_reconnect: Optional[Callable[[], bool]] = None,
    logger: Optional[logging.Logger] = None,
)
```
- `address`: A tuple representing the IP address and port number to connect to.
- `received`: Optional queue to store received messages.
- `to_send`: Optional queue containing messages to be sent.
- `reconnect`: If True, the client will attempt to reconnect after disconnection.
- `timeout`: Optional timeout value for send and receive operations.
- `stop_receive`: A function that returns True to signal the receiving loop to stop.
- `stop_send`: A function that returns True to signal the sending loop to stop.
- `stop_reconnect`: A function that returns True to signal the reconnecting loop to stop. Won't have
any effect if reconnect is set to False.
- `logger`: Optional logger for logging client events.

#### Properties

- `ip`: The IP address component of the client's address.
- `port`: The port number component of the client's address.
- `received`: The queue containing received messages.
- `to_send`: The queue containing messages to be sent.
- `send_thread`: The thread responsible for sending messages.
- `receive_thread`: The thread responsible for receiving messages.

#### Methods
- `connect(timeout: Optional[float] = None)`: Connects to the server with an optional timeout.
- `start()`: Starts the client in a new thread.
- `join()`: Waits for the client thread to finish.
- `shutdown()`: Signals the client to shut down gracefully.
- `close_connection()`: Closes the socket connection.
- `__enter__()`: Context manager entry point.
- `__exit__(...)`: Context manager exit point.


### AbstractService

This abstract base class is a blueprint  to easily create other services that communicate with each other trough queues. Very useful
for processing, storing, etc. the data received trough sockets.

Abstract base class for all services.

To add a new service, implement the `_handle_message` method.

A service consists of an input queue and an output queue. The purpose of a service is to apply some function to the inputs to obtain the outputs that can then be processed by another service or sent to a receptor.

Most services are meant to run indefinitely, and so they do not run in the main thread. However, a custom function to terminate the service when needed can be used, and the service can also run in the main thread if necessary.

#### Constructor

```python
def __init__(
            self,
            in_queue: Optional[queue.Queue] = None,
            out_queue: Optional[queue.Queue] = None,
            stop: Optional[Callable[[], bool]] = None,
            events: Optional[dict[str, threading.Event]] = None,
            logger: Optional[logging.Logger] = None,
    ):
```

#### Parameters:

- `in_queue` (Optional[queue.Queue]): Input queue for receiving messages.
- `out_queue` (Optional[queue.Queue]): Output queue for sending messages.
- `stop` (Optional[Callable[[], bool]]): Custom stop function.
- `events` (Optional[dict[str, threading.Event]]): Dictionary of events.
- `logger` (Optional[logging.Logger]): Logger for logging events.

### Examples 

Sample usage of a client that sends receives data from a server. The `client.py` program
will use a custom `MessageLogger` service to log all the data it receives, while the
`server.py` program whill use a service `MessageGenerator`to generate messages continuously
and send them to the client.

```python
# client.py
from socketlib import ClientReceiver
from socketlib.services.samples import MessageLogger
from socketlib.utils.logger import get_module_logger

if __name__ == "__main__":

    address = ("localhost", 12345)
    client = ClientReceiver(address, reconnect=True)
    
    logger = get_module_logger(__name__, "dev")
    msg_logger = MessageLogger(client.received, logger)
    
    with client:
        client.connect()
        client.start()
        msg_logger.start()
        
        try:
            client.join()
        except KeyboardInterrupt:
            client.shutdown()
            msg_logger.shutdown()

```

```python
# server.py
from socketlib import ServerSender, get_module_logger
from socketlib.services.samples import MessageGenerator


if __name__ == "__main__":

    address = ("localhost", 12345)
    server = ServerSender(address)
    
    logger = get_module_logger(__name__, "dev", use_file_handler=False)
    msg_gen = MessageGenerator(server.to_send, logger)
    
    with server:
        server.start()
        msg_gen.start()
        
        try:
            server.join()
        except KeyboardInterrupt:
            server.shutdown()
            msg_gen.shutdown()

```

## Developing

Developed in Python 3.11.4

Installing the development environment:

```shell
git clone https://github.com/Daniel-Ibarrola/MServ
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt
pip install -e .
```

## License

`pysocklib` was created by Daniel Ibarrola. It is licensed under the terms
of the MIT license.