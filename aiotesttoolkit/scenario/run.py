__all__ = ["create", "start"]
import asyncio
import functools
from aiotesttoolkit import pool


def create(_fun=None, *, size=None, loop=None):
    """ Same as pool.create

    Usable as:

    @create
    async def fun():
        ...

    @create(size=...)
    async def fun(*, id):
        ...
    """

    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            def factory(_, *, size=None):
                size = size or 1
                if size == 1:
                    yield fun(*args, **kwargs)
                else:
                    yield from (fun(*args, id=i, **kwargs) for i in range(0, size))

            return pool.create(fun, main=None, factory=factory, size=size, loop=loop)

        return wrapper

    return decorator if _fun is None else decorator(_fun)


def start(_fun=None, *, size=None, loop=None):
    """ Same as pool.start

    Usable as:

    @start
    async def fun():
        ...

    @start(size=...)
    async def fun(*, id):
        ...
    """

    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            _loop = loop or kwargs.pop("loop", asyncio.get_event_loop())
            return _loop.run_until_complete(
                create(_fun=fun, size=size or kwargs.pop("size", 1), loop=_loop)(
                    *args, **kwargs
                )
            )

        return wrapper

    return decorator if _fun is None else decorator(_fun)
