# Changelog

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