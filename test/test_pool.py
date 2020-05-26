""" Tests for the _pool module """
import asyncio
import aiotesttoolkit


class PoolTestCase(aiotesttoolkit.TestCase):
    def test_create(self):
        async def worker():
            print("Hello World !")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(aiotesttoolkit.create(worker, size=2))

    def test_create_factory(self):
        async def worker(i):
            print("worker {}: Hello World !".format(i))

        def factory(coro, *, size):
            return (coro(_) for _ in range(0, size))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(aiotesttoolkit.create(worker, factory=factory, size=2))

    def test_create_main(self):
        async def worker():
            print("Hello World !")

        async def main(*args, **kwargs):
            print("before")
            await aiotesttoolkit.run_tasks(*args, **kwargs)
            print("after")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(aiotesttoolkit.create(worker, main=main, size=2))

    def test_start(self):
        async def worker():
            print("worker with start")

        aiotesttoolkit.start(worker, size=2)

    def test_start_decorator1(self):
        @aiotesttoolkit.start(size=2)
        async def worker():
            print("worker with start decorator")

        worker()

    def test_start_decorator2(self):
        @aiotesttoolkit.start()
        async def worker():
            print("worker with start decorator")

        worker()

    def test_start_timeout(self):
        @aiotesttoolkit.start(size=2, timeout=1)
        async def worker():
            print("worker with timeout")
            await asyncio.sleep(10)
            raise Exception("should have timed out")

        worker()
        print("worker timed out")
