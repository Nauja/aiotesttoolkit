import sys
import asyncio
import aiotesttoolkit
from aiotesttoolkit import reporting, _scenario
import logging


class ScenarioTestCase(aiotesttoolkit.TestCase):
    @aiotesttoolkit.with_new_event_loop()
    @aiotesttoolkit.start()
    async def test(self):
        logger = logging.getLogger()
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.DEBUG)

        reporter = reporting.MetaReporter()
        reporter.add_reporter(reporting.SlaveReporter("127.0.0.1", 8081))
        await reporter.start()
        scenario = _scenario.Scenario()

        hosted_event = asyncio.Event()
        joining_event = asyncio.Event()
        joined_event = asyncio.Event()

        @scenario.with_node("create_game")
        @reporter.profile()
        async def create_game(fail):
            await asyncio.sleep(2)
            return {}

        @scenario.with_node("match")
        @reporter.profile()
        async def match():
            await asyncio.sleep(2)

        @scenario.with_node("disconnect")
        @reporter.profile()
        async def disconnect():
            await asyncio.sleep(2)

        @scenario.with_node("host")
        @reporter.profile()
        async def host():
            await reporter.info("host started")
            await asyncio.sleep(2)
            await create_game(False)
            hosted_event.set()
            await joining_event.wait()
            await asyncio.sleep(2)
            joined_event.set()
            await match()
            await disconnect()

        @scenario.with_node("join")
        @reporter.profile()
        async def join():
            await reporter.info("client started")
            await hosted_event.wait()
            await asyncio.sleep(2)
            joining_event.set()
            await joined_event.wait()
            await match()
            await disconnect() 

        await asyncio.wait([host(), join()])

        await reporter.stop()
