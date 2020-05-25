""" Common utility functions to control scenario execution """
__all__ = ["with_new_event_loop", "with_delay", "with_timeout", "run_forever"]
import asyncio
import functools


def with_new_event_loop(_fun=None):
    """Run a function with a new event loop.

    Equivalent to:

    .. code-block:: python

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        fun(loop=loop)

    - Ensure existing event loop is closed before creating
    the new one if any.
    - Ensure the created event loop is closed even if an
    exception occurs.
    """

    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            _loop = asyncio.get_event_loop()
            if _loop and not _loop.is_closed():
                try:
                    _loop.run_until_complete(_loop.shutdown_asyncgens())
                finally:
                    _loop.close()

            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)

            try:
                return fun(*args, loop=_loop, **kwargs)
            finally:
                _loop.run_until_complete(_loop.shutdown_asyncgens())
                _loop.close()

        return wrapper

    return decorator if _fun is None else decorator(_fun)


def with_delay(timer):
    """ Delay function execution by a timer:

        await asyncio.sleep(timer)
        await fun()
    """

    def decorator(fun):
        @functools.wraps(fun)
        async def wrapper(*args, **kwargs):
            await asyncio.sleep(timer or 0)
            return await fun(*args, **kwargs)

        return wrapper

    return decorator


def with_timeout(timer):
    """ Stop execution of a coroutine after a delay:

        await asyncio.wait(..., timeout=timer)
    """

    def decorator(fun):
        @functools.wraps(fun)
        async def wrapper(*args, **kwargs):
            return await asyncio.wait([fun(*args, **kwargs)], timeout=timer)

        return wrapper

    return decorator


def run_forever():
    """ Run a function forever:

        while True:
            await fun()
    """

    def decorator(fun):
        @functools.wraps(fun)
        async def wrapper(*args, **kwargs):
            while True:
                await fun(*args, **kwargs)

        return wrapper

    return decorator
