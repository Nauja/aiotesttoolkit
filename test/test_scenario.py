""" Tests for the pool module """
import unittest
from aiotesttoolkit import scenario
from aiotesttoolkit.loader import TestCase


class TestScenario(TestCase):
    @scenario.with_new_event_loop
    @scenario.start
    async def test_single_task(self):
        """ Test to run a single task """
        pass


class TestScenarioDecorator(TestCase):
    """ Test to use scenario.start as a decorator """

    def setUp(self):
        self.result = 0

    @scenario.with_new_event_loop
    @scenario.start(size=5)
    async def test_start_decorator(self, id):
        self.result += 1

    def tearDown(self):
        self.assertEqual(self.result, 5, "some workers didn't run")
