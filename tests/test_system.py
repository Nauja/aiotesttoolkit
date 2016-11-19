from unittest import TestCase
from testtoolkit import system
 
class TestSystem(TestCase):
    # Test running the system
    def test_run(self):
        def test(context, process):
            for i in xrange(1, 3 + process):
                print "process %d: step %d" % (process, i)
                yield
        system.run(3, system.main_loop, test)
           
    # Test sending messages between processes 
    def test_send(self):
        def test(context, process):
            # Send message from process 0 to everyone
            if process == 0:
                print context
                sent_to = [_ for _ in system.send(context, process, system.send_all(context, 0), 1)]
                assert len(sent_to) == 2, "Message not sent to everyone"
                assert 1 in sent_to and 2 in sent_to, "Message sent to wrong process"
            yield
            # Check that process 1 and 2 received a message from process 0
            if process == 0:
                print context
                assert not system.has_message(context, process, system.recv_all()), "Message received"
            else:
                assert system.has_message(context, process, system.recv_all()), "No message received"
                msg = next(system.recv(context, process, system.recv_all()))
                msg["sender"] == 0, "Wrong message received"
                msg["message"] == 1, "Wrong message received"
            yield
            # Check that there is no received message remaining
            if process == 0:
                print context
            assert not system.has_message(context, process, system.recv_all()), "Message received"
            yield
        system.run(3, system.main_loop, test)
        
    # Test sending messages to processes in a group
    def test_send_group(self):
        def test(context, process):
            # Send message to processes in group 1
            if process == 0:
                sent_to = [_ for _ in system.send(context, process, system.send_group(context, process, 1), 1)]
                print sent_to
            yield
            # Check message has been received
            if process != 0:
                assert system.has_message(context, process, system.recv_all()), "No message received"
                msg = next(system.recv(context, process, system.recv_all()))
                msg["sender"] == 0, "Wrong message received"
                msg["message"] == 1, "Wrong message received"
        system.run(3, system.main_loop, test)
    
    # Test creating and joining groups
    def test_groups(self):
        def test(context, process):
            if process == 0:
                print context
            # All process join group 1
            system.join(context, process, 1)
            yield
            assert process in system.get_group_processes(context, 1), "Failed to join group"
            if process == 0:
                print context
            # Send message to processes in group 1
            if process == 0:
                sent_to = [_ for _ in system.send(context, process, system.send_group(context, process, 1), 1)]
                print sent_to
            yield
            # Check message has been received
            if process != 0:
                assert system.has_message(context, process, system.recv_all()), "No message received"
                msg = next(system.recv(context, process, system.recv_all()))
                msg["sender"] == 0, "Wrong message received"
                msg["message"] == 1, "Wrong message received"
            yield
            # All process join group 2
            system.join(context, process, 2)
            yield
            assert process in system.get_group_processes(context, 2), "Failed to join group"
            if process == 0:
                print context
            # All process leave group 1
            system.leave(context, process, 1)
            yield
            assert process not in system.get_group_processes(context, 1), "Failed to leave group"
            if process == 0:
                print context
        system.run(3, system.main_loop, test)