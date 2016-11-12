import system

# Main loop: store processes results into the context and return the result produced by result_handler
def result_wrapper(result_handler, main_loop):
    def wrapper(context, processes):
        # Prepare a list of pool_size results for processes
        context["results"] = [None for _ in xrange(0, context.pool_size)]
        # Run main loop
        for result in main_loop(context, processes):
            # Return the final result produced by result_handler or go to the next step
            yield result_handler(result, (_ for _ in context.results)) if result else result
    return wrapper

# Store the last process result into the context
def result_producer(method):
    def wrapper(context, process):
        for result in method(context, process):
            context.results[process] = result
            yield result
    return wrapper

@result_producer
def test_result(context, process):
    yield process + 1
    
def sum(loop_result, processes_results):
    return reduce(lambda x, y: x + y, processes_results)
    
def mult(loop_result, processes_results):
    return reduce(lambda x, y: x * y, processes_results)
    
if __name__ == '__main__':
    result = system.run(4, result_wrapper(sum, system.main_loop), test_result)
    print "result", result
    result = system.run(4, result_wrapper(mult, system.main_loop), test_result)
    print "result", result