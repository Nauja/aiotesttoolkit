__all__ = [
    "TestCase",
    "load_tests_from_class",
    "load_tests_from_module",
    "load_tests",
    "run",
]
import unittest
import logging
import json
import importlib
import nose
from nose.plugins.cover import Coverage
import coverage

logger = logging.getLogger("testtoolkit")


class TestCase(unittest.TestCase):
    def __init__(self, method, db_config=None, options=None, **kwargs):
        unittest.TestCase.__init__(self, method)
        self.db_config = db_config
        self.options = options


def load_tests_from_class(clazz, config, default_options):
    """Use configuration to load all tests from a class.

    :param config: Configuration for the class.
    :param default_options: Global default options for tests.
    :param get_db_config: Get configuration for a database.
    :returns: All tests from class.
    """
    _options = dict(default_options)
    _options.update(config.get("options", {}))
    tests = config.get("tests", [])

    suite = unittest.TestSuite()
    for _ in [_ for _ in tests if hasattr(clazz, _["name"])]:
        logger.debug("Load test {}.{}".format(clazz.__name__, _["name"]))
        options = dict(_options)
        options.update(_.get("options", {}))

        suite.addTest(clazz(_["name"], options=options))
    return suite


def load_tests_from_module(module, config, default_options):
    """Use configuration to load all tests from a module.

    :param config: Configuration for the module.
    :param default_options: Global default options for tests.
    :returns: All tests from module.
    """
    _options = dict(default_options)
    _options.update(config.get("options", {}))
    test_cases = config.get("test_cases", [])

    for _ in [_ for _ in test_cases if hasattr(module, _["name"])]:
        logger.debug("Load tests from test case {}".format(_["name"]))
        for _ in load_tests_from_class(
            getattr(module, _["name"]), _, default_options=dict(_options)
        ):
            yield _


def load_tests(config_filename, **kwargs):
    """Load all configured tests.
    """
    parent_module = kwargs["parent_module"]
    parent_config = kwargs.get("parent_config", None)

    try:
        with open(config_filename, "r") as f:
            config = json.loads(f.read())
    except Exception:
        logger.error("Could not load {}".format(config_filename))
        raise
    # Copy and merge default options
    _config = dict(parent_config or {})
    _config.setdefault("options", {}).update(config.get("options", {}))

    # Gather all tests from children attribute
    suite = unittest.TestSuite()
    for _ in config.get("children", []):
        if isinstance(_, dict):
            # Dict type means test case description
            logger.debug("Load tests from module {}".format(_["name"]))
            module = importlib.import_module(
                _["name"]
                if not parent_module
                else "{}.{}".format(parent_module, _["name"])
            )
            for test in load_tests_from_module(
                module, _, default_options=dict(_config["options"])
            ):
                suite.addTest(test)
        else:
            # Str type means included json file
            suite.addTest(
                load_tests(_, parent_module=parent_module, parent_config=_config)
            )

    return suite


def run(config_filename, **kwargs):
    """Run all configured tests.

    Builtin tests options are:
    - server: Selected server.
    - database: Selected database.
    - size: Number of bots to run.
    - delay: Delay value.
    - timeout: Timeout value.

    You can use custom options that will be automatically
    passed to your tests.
    :param parent_module: parent module path
    """
    parent_module = kwargs["parent_module"]
    cover_package = kwargs.get("cover_package", None)
    cover_html = kwargs.get("cover_html", None)

    cov = coverage.Coverage()
    # cov.load()
    cov.start()
    suite = load_tests(config_filename, parent_module=parent_module)
    cov.stop()
    cov.save()
    argv = ["mock", "--with-coverage", "--verbosity=2"]
    if cover_package:
        argv.append("--cover-package={}".format(cover_package))
    if cover_html:
        argv.append("--cover-html")
    nose.run(argv=argv, plugins=[Coverage()], suite=suite)
