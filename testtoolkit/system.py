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
        self._processes = []
        
    # Start the main loop.
    def start(self, main_loop = main_loop):
        self._task_handle = asyncio.get_event_loop().create_task(self.run(main_loop))
        
    # Stop the System.
    def stop(self):
        # Stop the main loop.
        if self._task_handle:
            self._task_handle.cancel()
            self._task_handle = None
        # Stop all processes.
        for process in self._processes:
            process.cancel()
        self._processes = []
        
    # Block the thread until all processes are done.
    def run_until_complete(self):
        if self._task_handle:
            asyncio.get_event_loop().run_until_complete(self._task_handle)
        
    # Main loop.
    async def run(self, main_loop):
        while len(self._processes) != 0:
            await main_loop(self)
            self._processes[:] = (process for process in self._processes if not process.done())
            await asyncio.sleep(1)
        
    # Add a process to the System and run it.
    # Returns an handle on the process.
    def create_process(self, coro, *args):
        context = utils.ClassDict()
        context.system = self
        process = Process(context)
        self._processes.append(process)
        context.task = asyncio.get_event_loop().create_task(functools.partial(coro, process)(*args))
        return process
    
    # Stop a process.
    def stop_process(self, process):
        if process in self._processes:
            process.stop()
    
    # Get all processes matching a filter.
    def get_processes(self, filter, *args):
        for process in self._processes:
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