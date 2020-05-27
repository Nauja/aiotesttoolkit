__all__ = ["ServerReporter"]
from ._base import AbstractReporter


class ServerReporter(AbstractReporter):
    def __init__(self):
        '''Reporting server.

        Stats collected during tests are reported via this server.
        '''
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def report(self, stat):
        pass
