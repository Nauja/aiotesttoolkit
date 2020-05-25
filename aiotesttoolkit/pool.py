""" Module to setup and run a pool of tasks """
__all__ = ["create", "start", "create_tasks", "run_tasks"]
import asyncio
import functools


def create(coro, *, main=None, factory=None, size=None, loop=None):
    """ Return a pool of size tasks """
    main = main or run_tasks
    factory = factory or create_tasks
    return main(factory(coro, size=size), loop=loop)


def start(coro=None, *, main=None, factory=None, size=None, loop=None):
    """ Run a pool of size tasks until all are complete """

    def _start(fun):
        _loop = loop or asyncio.get_event_loop()
        pool = create(fun, main=main, factory=factory, size=size, loop=_loop)
        return _loop.run_until_complete(pool)

    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            return _start(functools.partial(fun, *args, **kwargs))

        return wrapper

    return decorator if coro is None else _start(coro)


def create_tasks(coro, *, size=None):
    """ Return size tasks to run """
    return (coro() for _ in range(0, size or 1))


async def run_tasks(tasks, *, loop=None, **kwargs):
    """ Main loop to run and wait for tasks completion """
    done, _ = await asyncio.wait([_ for _ in tasks], loop=loop, **kwargs)
    return done
