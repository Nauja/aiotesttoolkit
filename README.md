# aiotesttoolkit

![versions](https://img.shields.io/pypi/pyversions/aiotesttoolkit.svg)
[![PyPI version](https://badge.fury.io/py/aiotesttoolkit.svg)](https://badge.fury.io/py/aiotesttoolkit)
[![Build Status](https://travis-ci.org/Nauja/aiotesttoolkit.png?branch=master)](https://travis-ci.org/Nauja/aiotesttoolkit)
[![Documentation Status](https://readthedocs.org/projects/aiotesttoolkit/badge/?version=latest)](https://aiotesttoolkit.readthedocs.io/en/latest/?badge=latest)
[![Test Coverage](https://codeclimate.com/github/Nauja/aiotesttoolkit/badges/coverage.svg)](https://codeclimate.com/github/Nauja/aiotesttoolkit/coverage)
[![Code Climate](https://codeclimate.com/github/Nauja/aiotesttoolkit/badges/gpa.svg)](https://codeclimate.com/github/Nauja/aiotesttoolkit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/Nauja/aiotesttoolkit/issues)

A simple, lightweight yet powerful toolkit for running bots to stress test and benchmark servers.

## Why ?

This package was created because while working on a game server I needed a tool that:
* Is simple, lightweight, and doesn't come with tons of unnecessary classes.
* Can run bots acting like normal players for unit testing and debugging purposes.
* Can stress test the server by running a massive amount of bots on the same computer for benchmarking purposes.
* Is generic and extensible enough to use it on any project with their own game servers and networking protocols.

From theses needs came the requirements that the tool should:
* Run all the bots in one single thread: for not having 100+ threads.
* Allow bots to communicate with each other: to simulate players playing together.
* Allow each bot to have its own socket to connect to the game server.
* Use a **selector** to handle the sockets created by all the bots: because of the single thread.
* Doesn't make any presumption of **what for** or **how** someone will use it.

And this is exactly what you can expect to find in this package.

## Installation

### setup.py

```
python setup.py install
```

## How it works

Here is a little explanation of how this package works with one example:

```python
from testtoolkit import system

def do_something(context, process):
  print "process %d: started" % process
  yield
  print "process %d: working" % process
  yield
  print "process %d: terminated" % process

system.run(2, system.main_loop, do_something)
```

It would output:

```
process 0: started
process 1: started
process 0: working
process 1: working
process 0: terminated
process 1: terminated
```

Firstly, it is important to understand that this package makes heavy use of python generators to achieve **cooperative threading** with a single thread. Processes are run sequentially and are required to **yield** when they want to let other processes to continue.

In the example, the function **do_something** that is passed to **run** is treated as a generator, and basically what the **main_loop** is doing is:

```python
processes = [do_something(context, i) for i in xrange(0, nb_processes)]
for process in processes:
  next(process)
```

So, if **do_something** contained no **yield** then the processes would all run sequentially.

## system.py

This module is the core of the package. By itself it contains only the bare minimum to run a system of any amount of bots on the same function and allow them to interact with each others.

Here is a complete example of what you can do with this module:

```python
from testtoolkit.system import *

def example(context, process):
  # Processes 0 and 1: join group 0, processes 2 and 3: join group 1
  my_group = process / 2
  join(context, process, my_group)
  # Necessary to let all processes join the groups before the next step
  yield
  # Process 0: send "Hello" to group 0, process 2: send "Hello" to group 1
  if process % 2 == 0:
    send_filter = send_group(context, process, my_group)
    for receiver in send(context, process, send_filter, "Hello"):
      print 'process %d: sent "Hello" to process %d' % (process, receiver)
  else:
    while not has_message(context, process, recv_all()):
      yield
    for msg in recv(context, process, recv_all()):
      print 'process %d: received "%s" from process %d' % (process, msg.data, msg.sender)
      
run(4, main_loop, example)
```

It would output:

```
process 0: sent "Hello" to process 1
process 2: sent "Hello" to process 3
process 1: received "Hello" from process 0
process 3: received "Hello" from process 2
```

Used functions:

```
join(context, process, group): make a process join a group.
send(context, process, filter, data): send data to all processes matching a filter.
recv(context, process, filter): receive all messages matching a filter.
```

## server.py

This module simply add a wrapper to the system main loop that manage a list of sockets, allowing processes to communicate with a server. It shows how you can extend the system main loop to add new and non intrusive functionalities to the system.

Here is a complete example of what you can do with this module:

```python
from testtoolkit.system import *
from testtoolkit.server import *
import socket

def example(context, process):
  # Process 0 act as a server, process 1 as a client
  if process == 0:
    # Create a server on port 1234
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    add(context, s)
    s.bind(("127.0.0.1", 1234))
    s.listen(1)
    print "process 0: listening on port 1234"
    yield
    # Accept a connection and send "hello"
    conn, addr = s.accept()
    add(context, conn)
    print "process 0: connection from %s" % str(addr)
    conn.sendall("hello")
    yield
    # Close the server and connection
    conn.close()
    remove(context, conn)
    s.close()
    remove(context, s)
  else:
    # Connect to the server on port 1234
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    add(context, s)
    s.connect(("127.0.0.1", 1234))
    print "process 1: connected on port 1234"
    yield
    # Wait to receive some data
    while not server.is_readable(context, s):
      yield
    print 'process 1: received "%s"' % str(s.recv(1024))
    # Close the connection
    s.close()
    remove(context, s)
      
run(2, server_wrapper(main_loop), example)
```

It would output:

```
process 0: listening on port 1234
process 1: connected on port 1234
process 0: connection from ('127.0.0.1', 57602)
process 1: received "hello"
```

Of course in a real world example, the processes would connect to a real server.

Used functions:

```
add(context, socket): register a socket to the system.
remove(context, socket): unregister a socket from the system.
is_readable(context, socket): indicate if there is data to read from a socket.
```
