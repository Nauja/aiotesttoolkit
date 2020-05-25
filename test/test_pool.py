""" Tests for the pool module """
from aiotesttoolkit import pool
from aiotesttoolkit.loader import TestCase


class TestPoolFunction(TestCase):
    """ Test to use pool.start as a function """

    def __init__(self, *args, **kwargs):
        super(TestPoolFunction, self).__init__(*args, **kwargs)
        self.result = None

    def run_test(self, worker, *, default=None, expected=None, msg=None, **kwargs):
        """ Run a test and check that result is correct """
        self.result = default
        pool.start(worker, **kwargs)
        self.assertEqual(self.result, expected, msg)

    def test_worker(self):
        """ Test to run multiple tasks """

        async def worker():
            """ Increment result when run """
            self.result += 1

        self.run_test(
            worker, size=10, default=0, expected=10, msg="some workers didn't run"
        )

    def test_factory(self):
        """ Test to create tasks with a custom factory """

        async def worker(side):
            """ Increment result when run """
            self.result[side] += 1

        def factory(coro, size=None):
            """ Return task A or B depending on i """
            return [coro(0 if _ < 5 else 1) for _ in range(0, size)]

        self.run_test(
            worker,
            factory=factory,
            size=10,
            default=[0, 0],
            expected=[5, 5],
            msg="some workers didn't run",
        )


class TestPoolDecorator(TestCase):
    """ Test to use pool.start as a decorator """

    def setUp(self):
        self.result = False

    @pool.start()
    async def test_start_decorator(self):
        self.result = True

    def tearDown(self):
        self.assertEqual(self.result, True, "worker didn't run")
