""" Tests for the _utils module """
import asyncio
import aiotesttoolkit


class UtilsTestCase(aiotesttoolkit.TestCase):
    @aiotesttoolkit.with_new_event_loop()
    def test_new_event_loop(self):
        print("with_new_event_loop")

    @aiotesttoolkit.with_new_event_loop()
    @aiotesttoolkit.start()
    @aiotesttoolkit.with_delay(1)
    async def test_delay(self):
        print("with_delay")

    @aiotesttoolkit.with_new_event_loop()
    @aiotesttoolkit.start()
    @aiotesttoolkit.with_timeout(1)
    async def test_timeout(self):
        print("with_timeout")
        await asyncio.sleep(10)
