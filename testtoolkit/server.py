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