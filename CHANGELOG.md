# Changelog

## v0.6.0 (10/09/2023)

### Features
- `Client`, `ClientSender`, `ServerSender` and `Server` classes can use bytes or string queues for messages
that will be sent.
- The functions `get_and_send_messages`and `send_msg can accept string or bytes.
- Removed function `receive_msg`.
- Connection errors and socket timeout are logged with different messages.

### Tests
- Unit test for send and receive modules.

## v0.5.1 (4/09/2023)

### Bugfixes
- Fixed address already in use error when server tries to reconnect a client.
- Sockets are shutdown before closing

### Features
- All clients and servers have optional argument `stop_reconnect` to add
a custom function to stop the reconnection loop.

### Tests
- Integration tests for reconnection.

## v0.5.0

### Features
- ClientBase is now an abstract base class and cannot be instantiated.
- ServerBase is now an abstract base class and cannot be instantiated.
- Added docstrings.

### Documentation
- Added documentation for main classes in the readme.

## v0.4.0

Clients and Servers have a new attribute "encoding", which can be used to
set the encoding of the messages sent. The functions in the `basic.send` module
also accept a new optional argument encoding.

## v0.3.4
Fixed address already in use error when reconnecting a ServerReceiver or a ServerSender.

## v0.3.3
Handle error when client tries to connect to a domain that can not be resolved

## v0.3.2
Can pass None to AbstractService class stop parameter. AbstractService
uses threading event to stop.

## v0.3.1

Fixed clients and servers getting blocked when trying to shut them down due
to being stuck trying to get messages from a queue.

## v0.3.0 (19/07/2022)

Continuous integration and deployment with GitHub actions.

## v0.2.0 (19/07/2022)

### Renamed package
Renamed the package to socketlib. All main classes can be directly imported from
the socketlib module, for example:

```python
from socketlib import Client, ClientSender, Server, ServerSender
```

The `buffer.py`, `send.py`, and `receive.py` modules where moved to a
module `basic`.

### Updated installation and build tools

- The package configuration was moved to the new file `pyproject.toml`. The setup file
`setup.py` was removed.
- First version of the package published to PyPi.
- Readme updated-

### CLI program

The CLI program can now be called directly after installing the package like in 
the following example:

```shell
socketlib --ip localhost --port 1234 --server
python -m socketlib --ip localhost --port 1234 --server  # alternative way
```

## v0.1.2 (18/07/2022)
- All client and server classes can take an optional parameter 'timeout' to specify a timeout for
socket send and receive operations.
- CLI optional timeout parameter (-o or --timeout) to specify the socket timeout.
- CLI optional messages parameter (-m or --messages) to specify a set of messages
that will be sent by a ClientSender or ServerSender.
- Server classes have `close_connection` method.

## v0.1.1 (14/07/2023)
- Client classes `connect` method runs in another thread.
- New method `close_connection` to close client connection to server.

## v0.1.0 (13/07/2023)

- First release
- Client classes to send, receive, and send/receive simultaneously.
- Server classes to send, receive, and send/receive simultaneously.
- Abstract service class works as a template to create services.