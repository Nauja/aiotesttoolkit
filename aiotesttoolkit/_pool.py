""" Module to setup and run a pool of tasks """
__all__ = ["create", "start", "create_tasks", "run_tasks"]
import asyncio
import functools


def create(coro, *, main=None, factory=None, size=None, **kwargs):
    """Create a pool of n tasks.

    This wraps a list of n `coro` tasks into a single `main` task you
    can run in asyncio's event loop.

    Running n workers:

    .. code-block:: python

        >>> async def worker():
        ...     print("Hello World !")
        ...
        >>> loop = asyncio.get_event_loop()
        >>> loop.run_until_complete(aiotesttoolkit.create(worker, size=2))
        Hello World !
        Hello World !

    Customize how workers are created by providing a custom `factory` function:

    .. code-block:: python

        >>> async def worker(i):
        ...     print("worker {}: Hello World !".format(i))
        ...
        >>> def factory(coro, *, size):
        ...     return (coro(_) for _ in range(0, size))
        ...
        >>> loop.run_until_complete(aiotesttoolkit.create(worker, factory=factory, size=2))
        worker 1: Hello World !
        worker 0: Hello World !

    Customize how tasks are run by providing a custom `main` function:

    .. code-block:: python

        >>> async def worker(i):
        ...     print("worker {}: Hello World !".format(i))
        ...
        >>> async def main(*args, **kwargs):
        ...     print("before")
        ...     await aiotesttoolkit.run_tasks(*args, **kwargs)
        ...     print("after")
        ...
        >>> loop.run_until_complete(aiotesttoolkit.create(worker, main=main, size=2))
        before
        worker 1: Hello World !
        worker 0: Hello World !
        after
    
    :param coro: task to run
    :param main: how to run the tasks
    :param factory: how to instantiate tasks
    :param size: size of the pool
    :param kwargs: additional arguments passed to `main`.
    :return: new pool
    """
    main = main or run_tasks
    factory = factory or create_tasks
    return main(factory(coro, size=size), **kwargs)


def start(coro=None, *, main=None, factory=None, size=None, loop=None, **kwargs):
    """Run a pool of n tasks until completion.
    
    Running n workers:

    .. code-block:: python

        >>> async def worker():
        ...     print("Hello World !")
        ...
        >>> aiotesttoolkit.start(worker, size=2)
        Hello World !
        Hello World !
    
    Using as a decorator:

    .. code-block:: python

        >>> @aiotesttoolkit.start(size=2)
        ... async def worker():
        ...     print("Hello World !")
        ...
        >>> worker()
        Hello World !
        Hello World !
    
    Running with 1s timeout:

    .. code-block:: python

        >>> @aiotesttoolkit.start(timeout=1)
        ... async def worker():
        ...     await asyncio.sleep(10)
        ...
        >>> worker()

    :param coro: task to run
    :param main: how to run the tasks
    :param factory: how to instantiate tasks
    :param size: size of the pool
    :param loop: asyncio's loop
    :param kwargs: additional arguments passed to `main`.
    :return: result
    """

    def _start(fun):
        _loop = loop or asyncio.get_event_loop()
        pool = create(fun, main=main, factory=factory, size=size, loop=_loop, **kwargs)
        return _loop.run_until_complete(pool)

    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            return _start(functools.partial(fun, *args, **kwargs))

        return wrapper

    return decorator if coro is None else _start(coro)


def create_tasks(coro, *, size=None):
    """Create n tasks.

    :param coro: task to run
    :param size: number of tasks
    :return: tasks
    """
    return (coro() for _ in range(0, size or 1))


async def run_tasks(tasks, **kwargs):
    """Run a pool of tasks.

    This function returns when all tasks are completed.

    :param tasks: tasks to run
    :param kwargs: additional arguments passed to `asyncio.wait`.
    :return: completed tasks
    """
    done, _ = await asyncio.wait([_ for _ in tasks], **kwargs)
    return done
