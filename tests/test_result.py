from unittest import TestCase
from testtoolkit import system, result
    
def sum(loop_result, processes_results):
    return reduce(lambda x, y: x + y, processes_results)
    
def mult(loop_result, processes_results):
    return reduce(lambda x, y: x * y, processes_results)

class TestResult(TestCase):
    def test_result(self):
        @result.result_producer
        def test(context, process):
            yield process + 1
        value = system.run(4, result.result_wrapper(sum, system.main_loop), test)
        self.assertEquals(value, 10, "Wrong result: expected %d, got %d" % (10, value))
        value = system.run(4, result.result_wrapper(mult, system.main_loop), test)
        self.assertEquals(value, 24, "Wrong result: expected %d, got %d" % (24, value))