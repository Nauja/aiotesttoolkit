__all__ = ["AbstractReporter"]
from abc import ABC, abstractmethod
import time


class AbstractReporter(ABC):
    LOGGER = "logger"
    PROFILER = "profiler"

    def __init__(self):
        '''Base for reporters.
        '''
        self._is_started = False

    @property
    def started(self):
        '''Indicate if this reported is started.

        :return: started or not
        '''
        return self._is_started

    async def start(self):
        '''Start this reporter.

        All emitted stats will now be reported.
        '''
        await self.__aenter__()

    async def stop(self):
        '''Stop this reporter.

        All emitted stats will now ignored.
        '''
        await self.__aexit__()

    async def __aenter__(self):
        '''Allow use of this reporter as a context.
        '''
        self._is_started = True
        return self

    async def __aexit__(self, *args, **kwargs):
        '''Allow use of this reporter as a context.
        '''
        self._is_started = False

    @abstractmethod
    async def emit(self, stat):
        '''Emit a new stat.

        :param stat: dict stat
        '''
        raise NotImplementedError()

    async def _on_enter_function(self, name, start):
        '''Stat emitted when entering a function.

        :param name: function's name
        :param start: clock when entering
        '''
        await self.emit({
            "emitter": AbstractReporter.PROFILER,
            "reliable": False,
            "event": "enter",
            "name": name,
            "start": start
        })

    async def _on_exit_function(self, name, start, end):
        '''Stat emitted when exiting a function.

        :param name: function's name
        :param start: clock when entering
        :param end: clock when exiting
        '''
        await self.emit({
            "emitter": AbstractReporter.PROFILER,
            "reliable": False,
            "event": "exit",
            "name": name,
            "start": start,
            "end": end
        })

    def profile(self, _fun=None, *, name=None):
        '''Emit stats when entering and leaving decorated function.

        .. code-block:: python

            >>> reporter = reporting.Reporter()
            >>> @aiotesttoolkit.start()
            ... @reporter.profile()
            ... async def run():
            ...     await asyncio.sleep(1)
            ...
            >>> run()

        Stat when entering a function:

        .. code-block:: python
    
            {
                "emitter": "profiler",
                "event": "enter",
                "name": "foo",
                "start": x
            }

        Stat when exiting a function:

        .. code-block:: python
    
            {
                "emitter": "profiler",
                "event": "exit",
                "name": "foo",
                "start": x,
                "end": y
            }

        :param name: custom name
        '''
        def decorator(fun):
            async def wrapper(*args, **kwargs):
                _name = name if name is not None else str(fun)
                _start = time.clock()
                try:
                    await self._on_enter_function(name=_name, start=_start)
                    return await fun(*args, **kwargs)
                finally:
                    await self._on_exit_function(name=_name, start=_start, end=time.clock())

            return wrapper

        return decorator if _fun is None else decorator(_fun)

    async def info(self, message, *, reliable=None):
        '''Stat emitted when exiting a function.

        :param name: function's name
        :param start: clock when entering
        :param end: clock when exiting
        '''
        await self.emit({
            "emitter": AbstractReporter.LOGGER,
            "reliable": reliable,
            "event": "info",
            "message": message
        })
