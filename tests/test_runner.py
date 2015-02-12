import unittest

from .helpers import *

import runner.constants as const
from runner.runner import Runner

class RunnerTestCase(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.__real_cwd = os.getcwd()
        os.chdir(self.tempdir.name)
        write_test_config()

    def tearDown(self):
        self.tempdir.cleanup()
        # Change CWD back to real CWD
        os.chdir(self.__real_cwd)

    def test_init(self):
        raise NotImplementedError

    def test_run(self):
        raise NotImplementedError

    def test_extract_stats(self):
        raise NotImplementedError

    def test_get_re_match(self):
        raise NotImplementedError

    def write_test_config(self):
        """write_test_config: Write a simple test INI config file to tempdir"""
        testconf = """

        """

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
