import system
import socket
import select

# Main loop: manage sockets used by the system
def server_wrapper(main_loop):
    def wrapper(context, processes):
        # Add sockets from sockets_to_add and remove the ones from sockets_to_remove
        def _dequeue_sockets_add_remove():
            for s in context.sockets_to_remove:
                sockets.discard(s)
                context.sockets_to_add.discard(s)
            for s in context.sockets_to_add:
                sockets.add(s)
            context.sockets_to_remove.clear()
            context.sockets_to_add.clear()
        # Add socket lists to context
        sockets = set([])
        context["sockets"] = sockets
        context["sockets_to_add"] = set([])
        context["sockets_to_remove"] = set([])
        context["readable"] = None
        context["writable"] = None
        context["exceptional"] = None
        # Run main loop
        loop = main_loop(context, processes)
        while True:
            # Pre loop processing
            yield next(loop)
            # Post loop processing
            result = next(loop)
            # Dequeue the sockets from add and remove lists
            _dequeue_sockets_add_remove()
            # Wait for sockets to be readable or writable
            if len(sockets) != 0:
                context.readable, context.writable, context.exceptional = select.select(sockets, sockets, sockets, 0.5)
            else:
                if context.readable:
                    context.readable = None
                if context.writable:
                    context.writable = None
                if context.exceptional:
                    context.exceptional = None
            # Wait for next loop
            yield result
    return wrapper

###########
# Sockets #
###########

# Add a socket to the context
def add(context, socket):
    context.sockets_to_add.add(socket)
    
# Remove a socket from the context
def remove(context, socket):
    context.sockets_to_remove.add(socket)
    
# Indicate if we can read from a socket
def is_readable(context, socket):
    return socket in context.readable if context.readable else False

# Indicate if we can write to a socket
def is_writable(context, socket):
    return socket in context.writable if context.writable else False
    
# Indicate if a socket has an error
def has_error(context, socket):
    return socket in context.exceptional if context.exceptional else False

#########
# Tests #
#########

# Test connecting two processes together via sockets
def test_connect(context, process):
    def server(context, process):
        print "process %d: listen" % process
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        add(context, s)
        s.bind(("127.0.0.1", 8016))
        s.listen(1)
        yield
        conn, addr = s.accept()
        add(context, conn)
        print "process %d: connected by %s" % (process, str(addr))
        while not is_readable(context, conn):
            yield
        print 'process %d: received "%s"' % (process, str(conn.recv(1024)))
        yield
        print "process %d: socket closed" % process
        conn.close()
        remove(context, conn)
        s.close()
        remove(context, s)
        yield True
        
    def client(context, process):
        print "process %d: connect" % process
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        add(context, s)
        s.connect(("127.0.0.1", 8016))
        yield
        s.sendall("hello world")
        yield
        print "process %d: socket closed" % process
        s.close()
        remove(context, s)
        yield True
        
    for result in server(context, process) if process == 0 else client(context, process):
        yield result
    
if __name__ == '__main__':
    system.run(2, server_wrapper(system.main_loop), test_connect)