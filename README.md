# testtoolkit

[![Build Status](https://travis-ci.org/Nauja/testtoolkit.png?branch=master)](https://travis-ci.org/Nauja/testtoolkit)
[![Test Coverage](https://codeclimate.com/github/Nauja/testtoolkit/badges/coverage.svg)](https://codeclimate.com/github/Nauja/testtoolkit/coverage)
[![Code Climate](https://codeclimate.com/github/Nauja/testtoolkit/badges/gpa.svg)](https://codeclimate.com/github/Nauja/testtoolkit)

## Installation

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
