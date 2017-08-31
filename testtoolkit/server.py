import asyncio
import functools

# Decorator starting a server on address:port.
async def start_server(process, address, port):
    async def handle_listen(reader, writer):
        process.context.reader = reader
        process.context.writer = writer
    await asyncio.start_server(handle_listen, address, port)

async def open_connection(process, address, port):
    reader, writer = await asyncio.open_connection(address, port)
    process.context.reader = reader
    process.context.writer = writer
