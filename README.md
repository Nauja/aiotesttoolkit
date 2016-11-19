# testtoolkit

[![Build Status](https://travis-ci.org/Nauja/testtoolkit.png?branch=master)](https://travis-ci.org/Nauja/testtoolkit)
[![Test Coverage](https://codeclimate.com/github/Nauja/testtoolkit/badges/coverage.svg)](https://codeclimate.com/github/Nauja/testtoolkit/coverage)
[![Code Climate](https://codeclimate.com/github/Nauja/testtoolkit/badges/gpa.svg)](https://codeclimate.com/github/Nauja/testtoolkit)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/Nauja/testtoolkit/issues)

A simple, lightweight yet powerful toolkit for stress testing and benchmarking servers.

### Why ?

This package was created because while working on a game server I needed a tool that:
* Is simple, lightweight, and doesn't come with tons of unnecessary classes.
* Can run bots acting like normal players for unit testing and debugging purposes.
* Can stress test the server by running a massive amount of bots on the same computer for benchmarking purposes.
* Is generic and extensible enough so that I can use it on other projects with their own game servers.

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

## Examples

### Run multiple processes on a function

This example shows the minimum required code to run 2 processes on a single function:

```python
from testtoolkit import system

def print_process(context, process):
  print "process %d: %d" % (process, 1)
  print "process %d: %d" % (process, 2)

system.run(2, system.main_loop, print_process)
```

The code above produces the following result:

```python
process 0: 1
process 0: 2
process 1: 1
process 1: 2
```

As you can see the system run the processes sequentially as there is only one single thread for all the processes.

### Run multiple processes on a function in parallel

This example shows how to run the processes in parallel by using **yield**:

```python
from testtoolkit import system

def print_process(context, process):
  print "process %d: %d" % (process, 1)
  yield
  print "process %d: %d" % (process, 2)

system.run(2, system.main_loop, print_process)
```

The code above produces the following result:

```python
process 0: 1
process 1: 1
process 0: 2
process 1: 2
```

Adding the keyword **yield** between the two print allow our processes to do cooperative threading and run in parallel.
