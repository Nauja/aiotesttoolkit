__all__ = ["MetaReporter"]
import asyncio
from ._base import AbstractReporter


class MetaReporter(AbstractReporter):
    def __init__(self):
        '''Stats reporter.

        This class is used to report stats collected during tests.

        .. code-block:: python

            >>> reporter = reporting.Reporter()
            >>> reporter.add_handler(reporting.handlers.MemoryHandler())
            >>> reporter.start()
            >>> profiler = profiling.Profiler(reporter=reporter)
            >>> @aiotesttoolkit.start()
            ... @profiler.record
            ... async def worker():
            ...     print("worker")
            ...
            >>> worker()
            >>> reporter.stop()
            
        '''
        super(MetaReporter, self).__init__()
        self._reporters = []

    def add_reporter(self, reporter):
        '''Add a sub reporter to forward emitted stats to.
    
        :param reporter: reporter to add
        '''
        self._reporters.append(reporter)

    def remove_reporter(self, reporter):
        '''Remove a sub reporter.
    
        :param reporter: reporter to remove
        '''
        self._reporters.remove(reporter)

    async def __aenter__(self):
        '''Start all sub reporters.
        '''
        if self.started:
            return

        await asyncio.wait([_.__aenter__() for _ in self._reporters])
        return self

    async def __aexit__(self, *args, **kwargs):
        '''Stop all sub reporters.
        '''
        if not self.started:
            return

        await asyncio.wait([_.__aexit__(*args, **kwargs) for _ in self._reporters])  

    async def emit(self, stat):
        '''Forward an emitted stat to sub reporters.

        :param stat: emitted stat
        '''
        await asyncio.wait([_.emit(stat) for _ in self._reporters])
