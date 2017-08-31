import sys
sys.path.append("../testtoolkit")
import asyncio
from unittest import TestCase
from testtoolkit import system
 
class TestSystem(TestCase):
    # Test joining and leaving groups
    def test_groups(self):
        async def main_loop(system):
            print ("main_loop")
            
        async def test(self):
            print (list(self.system.get_processes_in_group("group1")))
            await asyncio.sleep(1)
            
            print (list(self.system.get_processes_in_group("group1")))
            self.join_group("group1")
            await asyncio.sleep(1)
            
            print (list(self.system.get_processes_in_group("group1")))
            await asyncio.sleep(1)
            
            print (list(self.system.get_processes_in_group("group1")))
            self.leave_group("group1")
            await asyncio.sleep(1)
            
            print (list(self.system.get_processes_in_group("group1")))
            print ("done")
            
        # Setup the System.
        s = system.get_instance()
        for _ in range(2):
            s.create_process(test)
        s.start(main_loop)
        s.run_until_complete()