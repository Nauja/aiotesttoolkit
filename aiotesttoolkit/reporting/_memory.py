__all__ = ["MemoryReporter"]
from ._base import AbstractReporter
import json


class MemoryReporter(AbstractReporter):
    def __init__(self):
        super(MemoryReporter, self).__init__()
        self.stats = []

    def report(self, stat):
        if self.started:
            self.stats.append(stat)

    def dumps(self):
        return json.dumps(self.stats)
