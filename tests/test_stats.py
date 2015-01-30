import unittest

import runner.constants as const
from runner.stats import Statistics, StatisticsSet

class StatisticsTestCase(unittest.TestCase):
    def setUp(self):
        self.stats = Statistics()

    def test_init_values(self):
        initvals = {k: const.TRACKED_STATS[k]() for k in const.TRACKED_STATS}
        stats = Statistics(**initvals)
        for k, v in initvals.items():
            self.assertEqual(getattr(stats, k), v)

    def test_default_values(self):
        for k, v in const.TRACKED_STATS.items():
            self.assertEqual(getattr(self.stats, k), v())

    def test_getitem(self):
        for k, v in const.TRACKED_STATS.items():
            self.assertEqual(self.stats[k], getattr(self.stats, k))

    def test_unexpected_init(self):
        with self.assertRaises(AttributeError):
            Statistics(__qwertyuiopasdfghjklzxcvbnm='foobar')

    def test_getattr(self):
        with self.assertRaises(AttributeError):
            self.stats.__qwertyuiopasdfghjklzxcvbnm

    def test_setattr(self):
        with self.assertRaises(TypeError):
            self.stats.totalcash = 'foobar'
        self.stats.totalcash = 1234.
        self.assertEqual(self.stats.totalcash, 1234.)

    def test_anomaly_score(self):
        self.stats.totalcash = 123.
        self.stats.countcash = 100.
        self.stats.opcount   = 50.
        self.assertEqual(self.stats.anomaly_score, 0.46)
        self.stats.totalcash = 0.
        self.stats.countcash = 0.
        self.assertEqual(self.stats.anomaly_score, 0.)
        self.stats.opcount = 0.
        self.assertIsNone(self.stats.anomaly_score)

    def test_dict(self):
        with self.assertRaises(TypeError):
            self.stats.dict(1,2,3)
        self.stats.mpl = 5
        self.stats.trial = 10
        self.assertEqual(self.stats.dict('mpl'), {'mpl': 5})
        self.assertEqual(self.stats.dict('mpl', 'trial'), {'mpl':5, 'trial':10})
