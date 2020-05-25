""" Some functions to manage specific contexts """
__all__ = ["AsyncContextDecorator", "CreateTask"]
import asyncio


class AsyncContextDecorator(object):
    """ Context decorator for asyncio """

    def __call__(self, fun):
        async def wrapper(*args, **kwargs):
            async with self:
                await fun(*args, **kwargs)

        return wrapper


class CreateTask(AsyncContextDecorator):
    """ Start a task on enter, cancel it on exit """

    def __init__(self, coro, *, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._task = None
        self._coro = coro

    async def __aenter__(self):
        self._task = asyncio.ensure_future(self._coro)
        return self._task

    async def __aexit__(self, *_):
        self._task.cancel()
