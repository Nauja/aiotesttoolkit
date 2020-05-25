__all__ = ["with_messaging", "Messaging"]
import asyncio
from typing import Callable, Optional
import functools
import aiotesttoolkit
from aiotesttoolkit.context import AsyncContextDecorator, CreateTask
from aiotesttoolkit.producer import consume


class Messaging(AsyncContextDecorator):
    def __init__(self, client, codec, *, loop):
        self._client = client
        self._codec = codec
        self._loop = loop or asyncio.get_event_loop()
        self._taskContext = None
        self._message_queue = []

    async def __aenter__(self):
        def data_reader():
            while True:
                yield self._client.read()

        async def handle_data(data):
            stream = aiotesttoolkit.Stream(data)
            await self.on_received(self._codec.decode(stream))

        self._taskContext = CreateTask(
            consume(data_reader(), handle=handle_data, loop=self._loop)
        )
        await self._taskContext.__aenter__()
        return self

    async def __aexit__(self, *_):
        await self._taskContext.__aexit__(*_)

    def encode(self, message):
        """ Encode a message """
        stream = aiotesttoolkit.Stream()
        self._codec.encode(message, stream)
        return stream.to_bytes()

    async def write(self, message):
        """ Convert a message to bytes and send it """
        await self._client.write(self.encode(message))

    async def wait_message(self, *, accept=None):
        """ Wait for messages matching the filter to be received """
        accept = accept or (lambda _: True)
        while True:
            received = [_ for _ in self._message_queue if accept(_)]
            if received:
                return received
            await asyncio.sleep(0, loop=self._loop)

    async def on_received(self, message):
        self._message_queue.append(message)

    async def receive(self, *, accept=None):
        """ Wait to receive messages matching a filter """
        received = await self.wait_message(accept=accept)
        self.discard(received)
        return received

    async def send_and_receive(self, message, *, accept=None):
        """ Send a message and wait to receive messages matching a filter """
        self.send(message)
        return await self.receive(accept=accept)

    def discard(self, messages):
        for m in messages:
            self._message_queue.remove(m)

    def discard_all(self, *, accept=None):
        """ Discard all received messages matching a filter """
        self._message_queue[:] = [
            _ for _ in self._message_queue if not (accept and accept(_))
        ]


def with_messaging(
    _fun=None,
    *,
    codec=None,
    factory: Optional[Callable[[], Messaging]] = None,
    loop=None
):
    """Wrap a client with a messaging system

    Usable as:

    .. code-block:: python

        @with_client(...)
        @with_messaging(codec=...)
        async def fun(*, client, messaging):
            ...

    :param codec: Codec to decode and encode messages.
    :param factory: How to create the Messaging instance.
    """

    def decorator(fun):
        @functools.wraps(fun)
        async def wrapper(*args, **kwargs):
            _client = kwargs.get("client", None)
            _codec = codec or kwargs.pop("codec", None)
            _loop = loop or kwargs.pop("loop", asyncio.get_event_loop())
            async with (factory or Messaging)(_client, _codec, loop=_loop) as messaging:
                kwargs["messaging"] = messaging
                return await fun(*args, **kwargs)

        return wrapper

    return decorator if _fun is None else decorator(_fun)
