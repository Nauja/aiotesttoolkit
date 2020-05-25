__all__ = ["ServerContext", "with_server", "ClientContext", "with_client"]
import asyncio
import functools
from aiotesttoolkit import packet, tcp
from .socket import StartServerContext

_DEFAULT_SIZE_CODEC = packet.BinarySizeCodec


class ServerContext:
    """ Start a server.

    When entered: start a server.
    When exited: shutdown the server.

    Usage:

    .. code-block: python

        async def handle_client(client):
            ...

        async with ServerContext(handle=handle_client, host=..., port=...):
            ...

    Returned object is a :obj:`protocol.Client` instance.
    """

    def __init__(self, *, host=None, port=None, size_codec=None, **kwargs):
        """Initialize the context.

        :param host: Server's ip address.
        :param port: Server's port.
        :param size_codec: Codec for encoding/decoding data.
        :param loop: Events loop.
        """
        self._kwargs = kwargs
        self._host = host
        self._port = port
        self._loop = kwargs.pop("loop", None) or asyncio.get_event_loop()
        self._size_codec = size_codec or _DEFAULT_SIZE_CODEC

    def __enter__(self):
        protocol_type = functools.partial(
            tcp.TCPProtocol,
            transport_type=lambda reader, transport: packet.PacketTransport(
                reader,
                transport,
                size_codec=self._size_codec,
                inner_type=tcp.TCPTransport,
            ),
            loop=self._loop,
        )
        self._start_server_ctx = StartServerContext(
            protocol_type=protocol_type,
            host=self._host,
            port=self._port,
            loop=self._loop,
        )
        self._server = self._start_server_ctx.__enter__()
        return self._server

    def __exit__(self, *_):
        self._start_server_ctx.__exit__(*_)


def with_server(**_):
    """ Start a server.

    Usage:

    .. code-block: python

        async def handle_client(client):
            ...

        @with_server(handle=handle_client, host=..., port=...)
        async def fun():
            ...

    See :obj:`ServerContext` for more informations.
    """

    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            with ServerContext(
                handle=kwargs.pop("handle", _.get("handle", None)),
                host=kwargs.pop("host", _.get("host", None)),
                port=kwargs.pop("port", _.get("port", None)),
                size_codec=kwargs.pop(
                    "size_codec", _.get("size_codec", _DEFAULT_SIZE_CODEC)
                ),
                loop=kwargs.pop("loop", _.get("loop", None)),
            ) as server:
                return fun(*args, server=server, **kwargs)

        return wrapper

    return decorator


class ClientContext:
    """ Create a client connected to a server.

    When entered: return a client connected to the server.
    When exited: disconnect the client from server.

    To create a new connection:

    .. code-block: python

        async with ClientContext(host=..., port=...) as client:
            print(client.id)

    To use an existing connection:

    .. code-block: python

        async with ClientContext(reader=..., writer=...) as client:
            print(client.id)

    Returned object is a :obj:`protocol.Client` instance.
    """

    def __init__(
        self,
        *,
        host=None,
        port=None,
        reader=None,
        writer=None,
        size_codec=None,
        loop=None
    ):
        """Initialize the context.

        :param host: Server's ip address.
        :param port: Server's port.
        :param reader: Reader connected to server.
        :param writer: Writer connected to server.
        :param size_codec: Codec for encoding/decoding data.
        :param loop: Events loop.
        """
        self._id = 0 if id is None else id
        self._host = host
        self._port = port
        self._reader = reader
        self._writer = writer
        self._size_codec = size_codec or _DEFAULT_SIZE_CODEC
        self._loop = loop or asyncio.get_event_loop()

    async def __aenter__(self):
        self._is_managed = False
        # Open a connection if there is no reader and writer given
        if self._reader is None and self._writer is None:
            self._is_managed = True
            self._reader, self._writer = await asyncio.open_connection(
                self._host, self._port, loop=self._loop
            )
        # Wrap given connection as a client
        return packet.PacketTransport(
            self._reader,
            self._writer,
            size_codec=self._size_codec,
            inner_type=tcp.TCPTransport,
        )

    async def __aexit__(self, *_):
        if self._is_managed:
            self._writer.close()


def with_client(**_):
    """ Create a client connected to a server.

    To create a new connection:

    .. code-block: python

        @with_client(host=..., port=...)
        async def fun(*, client):
            ...

    To use an existing connection:

    .. code-block: python

        @with_client(reader=..., writer=...)
        async def fun(*, client)
            ...

    See :obj:`ClientContext` for more informations.
    """

    def decorator(fun):
        @functools.wraps(fun)
        async def wrapper(*args, **kwargs):
            async with ClientContext(
                host=kwargs.pop("host", _.get("host", None)),
                port=kwargs.pop("port", _.get("port", None)),
                reader=kwargs.pop("reader", _.get("reader", None)),
                writer=kwargs.pop("writer", _.get("writer", None)),
                size_codec=kwargs.pop(
                    "size_codec", _.get("size_codec", _DEFAULT_SIZE_CODEC)
                ),
                loop=kwargs.pop("loop", _.get("loop", None)),
            ) as client:
                return await fun(*args, client=client, **kwargs)

        return wrapper

    return decorator
