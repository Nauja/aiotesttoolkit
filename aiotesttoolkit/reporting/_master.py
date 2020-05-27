__all__ = ["MasterReporter"]
import json
import asyncio
import logging


logger = logging.getLogger(__name__)


class MasterReporter(object):
    def __init__(self, host, port=None, *, handle_stat, buffer_size=None, receive=None, decode=None):
        '''Master reporter.

        Received stats emitted by slave reporters.

        :param host: master's host
        :param port: master's port
        :param buffer_size: size of buffer to receive data
        :param receive: how to receive data from slaves
        :param decode: how to decode received stats
        '''
        self._is_started = False
        self._host = host
        self._port = port
        self._server = None
        self._slaves = []
        self._handle_stat = handle_stat
        self._buffer_size = buffer_size if buffer_size is not None else 1024
        self._receive = receive if receive is not None else self.receive
        self._decode = decode if decode is not None else MasterReporter.decode

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    async def start(self):
        '''Start the master server.
        '''
        await self.__aenter__()

    async def stop(self):
        '''Stop the master server.
        '''
        await self.__aexit__()

    async def __aenter__(self):
        '''Open connection.
        '''
        if self._is_started:
            return

        self._is_started = True

        logger.info(f"Starting master on {self._host}:{self._port}...")
        try:
            self._slaves = []
            self._server = await asyncio.start_server(
                self._handle_slave,
                host=self._host,
                port=self._port
            )

            addr = self._server.sockets[0].getsockname()
            self._port = addr[1]
            logger.info(f'Master started on {self._host}:{self._port}')
        except:
            logger.error("Failed to start master")
            raise

        return self

    async def __aexit__(self, *args, **kwargs):
        '''Close connection.
        '''
        if not self._is_started:
            return

        self._is_started = False

    async def _handle_slave(self, reader, writer):
        addr = writer.get_extra_info("peername")
        self._slaves.append(addr)
        try:
            logger.info(f"Connection from {addr[0]}:{addr[1]}")
            data = None
            while True:
                if data is None:
                    data = await self._receive(reader)
                else:
                    data += await self._receive(reader)

                stats, data = self._decode(data)
                for _ in stats:
                    await self._handle_stat(_)
        except Exception as e:
            raise e

    async def emit(self, stat):
        pass

    async def receive(self, reader):
        '''Read data from connection.

        :param reader: connection
        :return: data
        '''
        return (await reader.read(self._buffer_size)).decode()

    @staticmethod
    def decode(data):
        '''Decode received data.

        :param data: received data
        :return: received stats, remaining data
        '''
        stats = []
        while '\n' in data:
            parts = data.split('\n')
            stats.append(parts[0])
            data = parts[1]

        return stats, data
