# Main loop: store processes results into the context and return the result produced by result_handler
def result_wrapper(result_handler, main_loop):
    def wrapper(context, processes):
        # Prepare a list of pool_size results for processes
        context.results = [None for _ in xrange(0, context.pool_size)]
        # Run main loop
        result = None
        for result in main_loop(context, processes):
            yield
        # Let result_handler process the results
        yield result_handler(result, (_ for _ in context.results))
    return wrapper

# Store the last process result into the context
def result_producer(method):
    def wrapper(context, process):
        for result in method(context, process):
            context.results[process] = result
            yield result
    return wrapper