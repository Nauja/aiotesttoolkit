""" Module to dispatch data from a producer to a consumer """
__all__ = ["consume"]
from asyncio import ensure_future


async def consume(fs, *, handle=None, loop=None):
    """ Consume results of Futures and coroutines given by fs """
    async for data in (await ensure_future(_, loop=loop) for _ in fs):
        if handle:
            await handle(data)
