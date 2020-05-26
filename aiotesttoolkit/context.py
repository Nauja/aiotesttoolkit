""" Some functions to manage specific contexts """
__all__ = ["CreateTask"]
import asyncio


class CreateTask(object):
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
