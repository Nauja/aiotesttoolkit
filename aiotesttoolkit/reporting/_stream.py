__all__ = ["StreamReporter"]
from ._base import AbstractReporter
import json


class StreamReporter(AbstractReporter):
    def __init__(self, stream, *, dumps=None):
        super(StreamReporter, self).__init__()
        self._stream = stream
        self._writer = None
        self._must_close = False
        self._dumps = dumps if dumps is not None else json.dumps

    async def __aenter__(self):
        if self.started:
            return

        if hasattr(self._stream, "write"):
            self._writer = self._stream
        else:
            self._writer = open(self._stream, "rb")
            self._must_close = True

        return await super(StreamReporter, self).__aenter__()


    async def __aexit__(self, *args, **kwargs):
        if not self.started:
            return

        if self._must_close:
            self._must_close = False
            self._writer.close()

        await super(StreamReporter, self).__aexit__(*args, **kwargs)

    async def emit(self, stat):
        if hasattr(self._stream, "write"):
            self._stream.write(self._dumps(stat))
