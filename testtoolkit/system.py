import asyncio
import functools
import utils
    
# Empty main loop for the System.
async def main_loop(system):
    pass

# System object.
# Handle a pool of running processes.
class System(object):
    def __init__(self):
        self.processes = []
        self.task = None
        
    # Start the main loop.
    def start(self, main_loop = main_loop):
        self.task = asyncio.get_event_loop().create_task(self.run(main_loop))
        
    # Stop the System.
    def stop(self):
        # Stop the main loop.
        if self.task:
            self.task.cancel()
            self.task = None
        # Stop all processes.
        for process in self.processes:
            process.cancel()
        self.processes = []
        
    # Block the thread until all processes are done.
    def run_until_complete(self):
        if self.task:
            asyncio.get_event_loop().run_until_complete(self.task)
        
    # Main loop.
    async def run(self, main_loop):
        while len(self.processes) != 0:
            await main_loop(self)
            self.processes[:] = (process for process in self.processes if not process.done())
            await asyncio.sleep(1)
        
    # Add a process to the System and run it.
    # Returns an handle on the process.
    def create_process(self, coro, *args):
        context = utils.ClassDict()
        context.system = self
        process = Process(context)
        self.processes.append(process)
        context.task = asyncio.get_event_loop().create_task(functools.partial(coro, process)(*args))
        return process
    
    # Stop a process.
    def stop_process(self, process):
        if process in self.processes:
            process.stop()
    
    # Get all processes matching a filter.
    def get_processes(self, filter, *args):
        for process in self.processes:
            if filter(process, *args):
                yield process
                
    # Get all processes of a group.
    def get_processes_in_group(self, id):
        yield from self.get_processes(process_has_group, id)
        
# Process object.
# Represent a running task in the System.
class Process(object):
    def __init__(self, context):
        self.system = context.system
        self.context = context
        self.context.groups = set()
        
    # Join a group of processes.
    def join_group(self, id):
        self.context.groups.add(id)
        
    # Leave a group of processes.
    def leave_group(self, id):
        self.context.groups.remove(id)
        
    # Indicate if the process is in a group.
    def has_group(self, id):
        return id in self.context.groups
        
    # Indicate if the task is done.
    def done(self):
        return not self.context.task or self.context.task.done()
        
    # Stop this process.
    def stop(self):
        self._to_stop = True

# Create and start an instance of System.
_instance = System()

# Get the System instance.
def get_instance():
    return _instance

# Set the System instance.
def set_instance(instance):
    _instance = instance
    
# Indicate if a process is in a group.
def process_has_group(process, group):
    return process.has_group(group)