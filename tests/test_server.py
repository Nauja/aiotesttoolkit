import sys
sys.path.append("../testtoolkit")
import asyncio
from unittest import TestCase
from testtoolkit import system, server

class TestServer(TestCase):
    # Test connecting two processes together via sockets
    def test_connect(self):
        async def test_server(self):   
            await server.start_server(self, "127.0.0.1", 1234)
            print("server started", self.context.reader)
                    
        async def test_client(self):
            await server.open_connection(self, "127.0.0.1", 1234)
            print("client connected to server")
            
        # Setup the System.
        s = system.get_instance()
        s.create_process(test_server)
        s.create_process(test_client)
        s.create_process(test_client)
        s.start()
        s.run_until_complete()