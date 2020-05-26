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

## Install

Using pip:

```
pip install aiotesttoolkit
```

## How it works

Here is a little explanation of how this package works with one example:

```python
>>> import aiotesttoolkit
>>> async def worker():
...   print("Hello World !")
...
>>> aiotesttoolkit.start(worker, size=2)
Hello World !
Hello World !
```

This is how you would run a pool of n concurrent workers.
It internally relies on asyncio to run the workers, and you could obtain the same
result with:

```python
>>> import asyncio
>>> import aiotesttoolkit
>>> async def worker():
...   print("Hello World !")
...
>>> loop = asyncio.get_event_loop()
>>> loop.run_until_complete(aiotesttoolkit.create(worker, size=2))
Hello World !
Hello World !
```

Another way to use `aiotesttoolkit.start` is to use it as a decorator on your worker function:

```python
>>> import aiotesttoolkit
>>> @aiotesttoolkit.start(size=2)
... async def worker():
...   print("Hello World !")
...
>>> worker()
Hello World !
Hello World !
```

As you can see, there no way to identify which worker is running. By default, `aiotesttoolkit.start`
doesn't attribute an unique identifier to your worker as it tries not to make any presumption of
how your worker is written or will run. However you can customize how your workers are created with
a custom factory:

```python
>>> import aiotesttoolkit
>>> def create_workers(coro, *, size):
...   return (coro(_) for _ in range(0, size))
...
>>> @aiotesttoolkit.start(factory=create_workers, size=2)
... async def worker(i):
...   print("worker {}: Hello World !".format(i))
...
>>> worker()
worker 1: Hello World !
worker 0: Hello World !
```

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
