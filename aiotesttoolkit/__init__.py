""" TestToolkit """
from . import __version__ as version_info
from .__version__ import __version_major__, __version_long__, __version__, __status__
from aiotesttoolkit._pool import *
from aiotesttoolkit._utils import *
from aiotesttoolkit._test_utils import *
__all__ = [
    "version_info",
    "__version_major__",
    "__version_long__",
    "__version__",
    "__status__",
    # _pool
    "create",
    "start",
    "create_tasks",
    "run_tasks",
    # _utils
    "with_new_event_loop",
    "with_delay",
    "with_timeout",
    # _test_utils
    "TestCase"
]


def setup_logging(output=None):
    import logging

    logger = logging.getLogger("testtoolkit")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")
    if output:
        file_handler = logging.FileHandler(output)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


def main():
    import argparse

    parser = argparse.ArgumentParser(prog="Testtoolkit Runner", description="Run tests")
    parser.add_argument("--output", type=str, help="Output log file")
    parser.add_argument("--parent-module", type=str, help="Path to parent module")
    parser.add_argument("config", type=str, help="Configuration file")
    args = parser.parse_args()

    setup_logging(args.output)

    from . import loader

    loader.run(args.config, parent_module=args.parent_module)


if __name__ == "__main__":
    main()
