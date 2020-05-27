__all__ = ["SlaveReporter"]
from ._base import AbstractReporter
import json
import asyncio
import logging


logger = logging.getLogger(__name__)


class SlaveReporter(AbstractReporter):
    def __init__(self, host, port, *, nb_retries=None, retry_delay=None, connect=None, encode=None):
        '''Slave reporter.

        Report collected stats to a master server.

        :param host: master's host
        :param port: master's port
        :param nb_retries: number of connection retries (None = unlimited)
        :param retry_delay: delay before retrying to connect
        :param connect: how to connect to master server
        :param encode: how to encode emitted stats
        '''
        super(SlaveReporter, self).__init__()
        self._host = host
        self._port = port
        self._reader = None
        self._writer = None
        self._nb_retries = nb_retries
        self._retry_delay = retry_delay if retry_delay is not None else 1
        self._connect = connect if connect is not None else asyncio.open_connection
        self._encode = encode if encode is not None else SlaveReporter.encode

    async def __aenter__(self):
        '''Connect to master server.

        This support multiple retries with delay.
        '''
        if self.started:
            return

        retry = 0
        def has_retries():
            return self._nb_retries is None or retry < self._nb_retries

        while has_retries():
            logger.info("Connecting to master {}:{}...".format(self._host, self._port))
            try:
                self._reader, self._writer = await self._connect(
                    host=self._host,
                    port=self._port
                )

                logger.info("Connected to master")
                break
            except Exception as e:
                if not has_retries():
                    raise Exception("Connection to master failed") from e

                logger.error(e)
                logger.info("Connection failed, retry in {} second(s)...".format(self._retry_delay))

                await asyncio.sleep(self._retry_delay)

                retry += 1

        return await super(SlaveReporter, self).__aenter__()

    async def __aexit__(self, *args, **kwargs):
        '''Disconnect from master server.
        '''
        if not self.started:
            return

        self._writer.close()
        await self._writer.wait_closed()

        await super(SlaveReporter, self).__aexit__(*args, **kwargs)

    async def emit(self, stat):
        '''Send emitted stats to master server.

        :param stat: emitted stat
        '''
        if self.started:
            self._writer.write(self._encode(stat))

    @staticmethod
    def encode(stat: dict) -> bytes:
        '''Default stats encoder.

        Stats are dumped with `json.dumps` and separated with newlines.

        :param stat: stat to encode
        :return: encoded stat
        '''
        return (json.dumps(stat) + '\n').encode()
