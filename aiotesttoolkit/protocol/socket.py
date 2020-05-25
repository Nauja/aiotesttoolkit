__all__ = ["StartServerContext", "start_server", "open_connection"]
import asyncio
import functools
from aiotesttoolkit import tcp


class StartServerContext:
    """ Start a server.

    When entered: start a server.
    When exited: shutdown the server.

    Usage:

    .. code-block: python

        async def handle_client(*, reader, writer):
            ...

        async with StartServerContext(handle=handle_client, host=..., port=...):
            ...
    """

    def __init__(self, *, host=None, port=None, **kwargs):
        """Initialize the context.
        """
        self._kwargs = kwargs
        self._host = host
        self._port = port
        self._factory = kwargs.pop("factory", None)
        self._protocol_type = kwargs.pop("protocol_type", None)
        self._loop = kwargs.pop("loop", None) or asyncio.get_event_loop()

    def __enter__(self):
        # Run the server with handle_client for callback
        self._server = tcp.TCPServer(
            factory=self._factory, protocol_type=self._protocol_type, loop=self._loop
        )
        self._protocol = self._loop.run_until_complete(
            self._server.start(self._host, self._port, **self._kwargs)
        )
        return self._server

    def __exit__(self, *_):
        # Make sure to close the server
        self._server.close()
        self._loop.run_until_complete(self._server.wait_closed())


def start_server(**_):
    """ Open a connection before calling a function and close it after

    Usable as:

    .. code-block: python

        async def handle_client(*, reader, writer):
            ...

        @start_server(handle=handle_client, host=..., port=...)
        def foo():
            ...
    """

    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            with StartServerContext(**_) as server:
                return fun(*args, server=server, **kwargs)

        return wrapper

    return decorator


def open_connection(_fun=None, *, host=None, port=None, loop=None):
    """ Open a connection before calling a function and close it after

    Usable as:

    @open_connection(host=..., port=...)
    async def fun(*, reader, writer):
        ...
    """

    def decorator(fun):
        @functools.wraps(fun)
        async def wrapper(*args, **kwargs):
            _reader, _writer = await asyncio.open_connection(
                host or kwargs.pop("host", None),
                port or kwargs.pop("port", None),
                loop=loop or kwargs.pop("loop", None),
            )
            kwargs["reader"] = _reader
            kwargs["writer"] = _writer
            # Close the connection after calling decorated function
            try:
                return await fun(*args, **kwargs)
            finally:
                _writer.close()

        return wrapper

    return decorator if _fun is None else decorator(_fun)
