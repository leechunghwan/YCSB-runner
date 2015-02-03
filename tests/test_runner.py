import unittest

from .helpers import *

import runner.constants as const
from runner.runner import Runner

class RunnerTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        raise NotImplementedError

    def test_run(self):
        raise NotImplementedError

    def test_extract_stats(self):
        raise NotImplementedError

    def test_get_re_match(self):
        raise NotImplementedError

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
