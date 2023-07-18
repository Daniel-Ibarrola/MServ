# Changelog

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