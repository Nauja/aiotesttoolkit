__all__ = ["local_messaging_client"]
import functools
from aiotesttoolkit import scenario
from aiotesttoolkit import protocol


def local_messaging_client(
    _fun=None,
    *,
    host=None,
    port=None,
    nb_clients=None,
    size_codec=None,
    codec=None,
    loop=None
):
    """ Run nb_clients connected to a local messaging server

    Usable as:

    async def handle_client(*, client, messaging):
        ...

    @local_messaging_clients(host=..., port=..., handle=handle_client, nb_clients=..., codec=...)
    async def fun(*, client, messaging):
        ...
    """

    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            @protocol.with_messaging(codec=codec, loop=loop)
            async def handle_client(*, client, messaging):
                return await (handle or kwargs.pop("handle", None))(
                    client=client, messaging=messaging
                )

            # This run a local server
            @protocol.with_server(
                handle=handle_client,
                host=host,
                port=port,
                size_codec=size_codec,
                loop=loop,
            )
            def run_server(*, server):
                kwargs["server"] = server
                server.factory.add_connection_made_callback(handle_client)

                # This run the clients
                @scenario.start(size=nb_clients, loop=loop)
                @protocol.with_client(
                    host=host, port=server.port, size_codec=size_codec, loop=loop
                )
                @protocol.with_messaging(codec=codec, loop=loop)
                async def run_client(*, client, messaging):
                    kwargs["client"] = client
                    kwargs["messaging"] = messaging
                    return await fun(*args, **kwargs)

                return run_client()

            run_server()

        return wrapper

    return decorator if _fun is None else decorator(_fun)
