
aiotesttoolkit
==============


.. image:: https://img.shields.io/pypi/pyversions/aiotesttoolkit.svg
   :target: https://img.shields.io/pypi/pyversions/aiotesttoolkit.svg
   :alt: versions


.. image:: https://badge.fury.io/py/aiotesttoolkit.svg
   :target: https://badge.fury.io/py/aiotesttoolkit
   :alt: PyPI version


.. image:: https://travis-ci.org/Nauja/aiotesttoolkit.png?branch=master
   :target: https://travis-ci.org/Nauja/aiotesttoolkit
   :alt: Build Status


.. image:: https://readthedocs.org/projects/aiotesttoolkit/badge/?version=latest
   :target: https://aiotesttoolkit.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


.. image:: https://codeclimate.com/github/Nauja/aiotesttoolkit/badges/coverage.svg
   :target: https://codeclimate.com/github/Nauja/aiotesttoolkit/coverage
   :alt: Test Coverage


.. image:: https://codeclimate.com/github/Nauja/aiotesttoolkit/badges/gpa.svg
   :target: https://codeclimate.com/github/Nauja/aiotesttoolkit
   :alt: Code Climate


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black


.. image:: https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat
   :target: https://github.com/Nauja/aiotesttoolkit/issues
   :alt: contributions welcome


A simple, lightweight yet powerful toolkit for running bots to stress test and benchmark servers.

Why ?
-----

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

Install
-------

Using pip:

.. code-block::

   pip install aiotesttoolkit

How it works
------------

Here is a little explanation of how this package works with one example:

.. code-block:: python

   >>> import aiotesttoolkit
   >>> async def worker():
   ...   print("Hello World !")
   ...
   >>> aiotesttoolkit.start(worker, size=2)
   Hello World !
   Hello World !

This is how you would run a pool of n concurrent workers.
It internally relies on asyncio to run the workers, and you could obtain the same
result with:

.. code-block:: python

   >>> import asyncio
   >>> import aiotesttoolkit
   >>> async def worker():
   ...   print("Hello World !")
   ...
   >>> loop = asyncio.get_event_loop()
   >>> loop.run_until_complete(aiotesttoolkit.create(worker, size=2))
   Hello World !
   Hello World !

Another way to use ``aiotesttoolkit.start`` is to use it as a decorator on your worker function:

.. code-block:: python

   >>> import aiotesttoolkit
   >>> @aiotesttoolkit.start(size=2)
   ... async def worker():
   ...   print("Hello World !")
   ...
   >>> worker()
   Hello World !
   Hello World !

As you can see, there no way to identify which worker is running. By default, ``aiotesttoolkit.start``
doesn't attribute an unique identifier to your worker as it tries not to make any presumption of
how your worker is written or will run. However you can customize how your workers are created with
a custom factory:

.. code-block:: python

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

Testing
-------

The test directory contains many tests that you can run with:

.. code-block::

   python setup.py test

Or with coverage:

.. code-block::

   coverage run --source=aiotesttoolkit setup.py test
