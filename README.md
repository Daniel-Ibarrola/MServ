# SocketLib

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

## Contents

### Client and Servers
This package includes different socket clients and servers. The following classes are included:

- **ClientReceiver**: A client that receives messages from a server 
- **ClientSender**: A client that sends data to a server
- **Client**: A client that receives and sends data simultaneously to a server  

- **ServerReceiver**: A server that receives messages from a client 
- **ServerSender**: A server that sends data to a client
- **Server**: A server that receives and sends data simultaneously to a client.


### Services

This module main class is the AbstractService. This abstract base class is a blueprint
to easily create other services that communicate with each other trough queues. Very useful
for processing, storing, etc. the data received trough sockets.


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
from socketlib import ServerSender
from socketlib.services.samples import MessageGenerator

if __name__ == "__main__":

    address = ("localhost", 12345)
    server = ServerSender(address)
    
    msg_gen = MessageGenerator(server.to_send)
    
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