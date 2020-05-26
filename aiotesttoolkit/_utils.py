""" Common utility functions to control execution """
__all__ = ["with_new_event_loop", "with_delay", "with_timeout"]
import asyncio
import functools


def with_new_event_loop(_fun=None):
    """Run a function with a new event loop.

    .. code-block:: python

        @aiotesttoolkit.with_new_event_loop()
        def foo():
            loop = asyncio.get_event_loop()
            ...

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
                return fun(*args, **kwargs)
            finally:
                _loop.run_until_complete(_loop.shutdown_asyncgens())
                _loop.close()

        return wrapper

    return decorator if _fun is None else decorator(_fun)


def with_delay(delay):
    """Delay function execution.

    .. code-block:: python

        @aiotesttoolkit.with_delay(1)
        async def foo():
            ...
    
    :param delay: value
    """

    def decorator(fun):
        @functools.wraps(fun)
        async def wrapper(*args, **kwargs):
            delay = delay if delay is not None else 0
            await asyncio.sleep(delay)
            return await fun(*args, **kwargs)

        return wrapper

    return decorator


def with_timeout(timeout):
    """Timeout execution of a function.

    .. code-block:: python

        @aiotesttoolkit.with_timeout(1)
        async def foo():
            ...
    
    :param timeout: value
    """

    def decorator(fun):
        @functools.wraps(fun)
        async def wrapper(*args, **kwargs):
            timeout = timeout if timeout is not None else 0
            return await asyncio.wait([fun(*args, **kwargs)], timeout=timeout)

        return wrapper

    return decorator
