from unittest import TestCase
from testtoolkit import system, server
import socket

class TestServer(TestCase):
    # Test connecting two processes together via sockets
    def test_connect(self):
        def test(context, process):
            # Server-side
            def test_server(context, process):
                print "process %d: listen" % process
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.add(context, s)
                s.bind(("127.0.0.1", 8016))
                s.listen(1)
                yield
                conn, addr = s.accept()
                server.add(context, conn)
                print "process %d: connected by %s" % (process, str(addr))
                while not server.is_readable(context, conn):
                    yield
                print 'process %d: received "%s"' % (process, str(conn.recv(1024)))
                yield
                print "process %d: socket closed" % process
                conn.close()
                server.remove(context, conn)
                s.close()
                server.remove(context, s)
                yield True
            # Client-side
            def test_client(context, process):
                print "process %d: connect" % process
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.add(context, s)
                s.connect(("127.0.0.1", 8016))
                yield
                s.sendall("hello world")
                yield
                print "process %d: socket closed" % process
                s.close()
                server.remove(context, s)
                yield True
            # Run server if process id is 0, client otherwise
            for result in test_server(context, process) if process == 0 else test_client(context, process):
                yield result
        system.run(2, server.server_wrapper(system.main_loop), test)
        
    def test_example(self):
        def test(context, process):
            if process == 0:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.add(context, s)
                s.bind(("127.0.0.1", 1234))
                s.listen(1)
                print "process 0: listening on port 1234"
                yield
                conn, addr = s.accept()
                server.add(context, conn)
                print "process 0: connection from %s" % str(addr)
                conn.sendall("hello")
                yield
                conn.close()
                server.remove(context, conn)
                s.close()
                server.remove(context, s)
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.add(context, s)
                s.connect(("127.0.0.1", 1234))
                print "process 1: connected on port 1234"
                yield
                while not server.is_readable(context, s):
                    yield
                print 'process 1: received "%s"' % str(s.recv(1024))
                s.close()
                server.remove(context, s)
        system.run(2, server.server_wrapper(system.main_loop), test)