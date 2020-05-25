""" Tests for the pool module """
import unittest
import asyncio
from aiotesttoolkit import scenario
from aiotesttoolkit import protocol
from aiotesttoolkit.loader import TestCase


class TestOpenConnectionDecorator(TestCase):
    """ Test to use protocol.start_server and open_connection as decorators """

    def setUp(self):
        self.result = False

    @scenario.with_new_event_loop
    def test_open_connection_decorator(self, loop):
        # Will be called when client is connected
        def handle_client(protocol):
            """ Validate test when client is connected """
            print("Server connection from", protocol)
            self.result = True

        # Start the local server
        @protocol.start_server(host="127.0.0.1", loop=loop)
        def run_server(*, server):
            print("Server started on port {}".format(server.port))
            server.factory.add_connection_made_callback(handle_client)

            # Start the client using decorator
            @scenario.start
            @protocol.open_connection(host="127.0.0.1", port=server.port, loop=loop)
            async def run_client(*, reader, writer):
                print("Client connected", reader, writer)

            run_client()

        run_server()

    def tearDown(self):
        self.assertTrue(self.result, "some workers didn't run")


class TestWithClientDecorator(TestCase):
    """ Test to use protocol.with_server and with_client as decorators """

    def setUp(self):
        self.result = False

    @scenario.with_new_event_loop
    def test_with_client_decorator(self, loop):
        def handle_data(protocol):
            """ Validate test when receiving "hello" """
            # We have to read data in async task
            async def run():
                print("Data from", protocol)
                data = await protocol.transport.read()
                self.result = data == b"hello"

            loop.create_task(run())

        # Start the local server
        @protocol.with_server(host="127.0.0.1", loop=loop)
        def run_server(*, server):
            print("Server started on port {}".format(server.port))
            server.factory.add_data_received_callback(handle_data)

            # Start the client using decorator
            @scenario.start
            @protocol.with_client(host="127.0.0.1", port=server.port)
            async def run_client(*, client):
                """ Try to send "hello" to server """
                print("Client connected", client)
                await client.write(b"hello")

            run_client()

        run_server()

    def tearDown(self):
        self.assertTrue(self.result, "some workers didn't run")


class TestWithMessagingDecorator(TestCase):
    """ Test to use protocol.with_messaging as decorator """

    def setUp(self):
        self.result = False

    @scenario.with_new_event_loop
    def test_with_messaging_decorator(self, loop):
        from messages import Messages, MessagesStream

        async def handle_client(*, client, messaging):
            """ Validate test when client is connected """
            for msg in await messaging.receive():
                if isinstance(msg, Messages.RequestLogin):
                    self.result = True

        @scenario.local_messaging_client(
            codec=MessagesStream, host="127.0.0.1", loop=loop
        )
        async def run(*, server, messaging, **_):
            await messaging.write(Messages.RequestLogin(username="u", password="p"))

        # Run test
        run()

    def tearDown(self):
        self.assertTrue(self.result, "some workers didn't run")
