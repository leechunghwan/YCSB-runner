import unittest

from .helpers import *

import runner.constants as const
from runner.stats import Statistics, StatisticsSet

class StatisticsTestCase(unittest.TestCase):
    def setUp(self):
        self.stats = Statistics()
        self.statitem1, self.statitem2 = get(const.TRACKED_STATS.items(), 2)

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
            Statistics(**{noattr(Statistics()): 'foobar'})

    def test_getattr(self):
        with self.assertRaises(AttributeError):
            getattr(self.stats, noattr(self.stats))

    def test_setattr(self):
        with self.assertRaises(TypeError):
            setattr(self.stats, self.statitem1[0], weirdtype())
        setattr(self.stats, self.statitem1[0], self.statitem1[1]() + 1234)
        self.assertEqual(getattr(self.stats, self.statitem1[0]), 1234)

    def test_anomaly_score(self):
        if hasattrs(self.stats, 'totalcash', 'countcash', 'opcount'):
            self.stats.totalcash = 100.
            self.stats.countcash = 123.
            self.stats.opcount   = 50.
            self.assertEqual(self.stats.anomaly_score, 0.46)
            self.stats.totalcash = 0.
            self.stats.countcash = 0.
            self.assertEqual(self.stats.anomaly_score, 0.)
            self.stats.opcount = 0.
            self.assertEqual(self.stats.anomaly_score, 0.)

    def test_dict(self):
        with self.assertRaises(TypeError):
            self.stats.dict(weirdtype(), weirdtype(), weirdtype())
        setattr(self.stats, self.statitem1[0], self.statitem1[1]() + 5)
        setattr(self.stats, self.statitem2[0], self.statitem2[1]() + 10)
        self.assertEqual(self.stats.dict(self.statitem1[0]), {
            self.statitem1[0]: self.statitem1[1]() + 5
        })
        self.assertEqual(self.stats.dict(self.statitem1[0], self.statitem2[0]), {
            self.statitem1[0]: self.statitem1[1]() + 5,
            self.statitem2[0]: self.statitem2[1]() + 10,
        })

class StatisticsSetTestCase(unittest.TestCase):
    def setUp(self):
        self.statitem1, = get(const.TRACKED_STATS.items(), 1)
        self.stat1 = Statistics()
        self.stat2 = Statistics()
        self.ss = StatisticsSet(self.stat1, self.stat2)

    def test_init(self):
        ss = StatisticsSet()
        self.assertEqual(ss.items(), [])
        self.assertEqual(self.ss.items(), [self.stat1, self.stat2])

    def test_getattr(self):
        self.assertEqual(self.ss.avg_anomaly_score, 0.)
        self.assertEqual(getattr(self.ss, 'avg_' + self.statitem1[0]), 0.)
        with self.assertRaises(AttributeError):
            getattr(self.ss, noattr(self.ss))

    def test_getitem(self):
        self.assertIsInstance(self.ss[0], Statistics)
        self.assertIsInstance(self.ss[1], Statistics)
        self.assertEqual(self.ss[0], self.stat1)
        self.assertEqual(self.ss[1], self.stat2)
        self.assertEqual(self.ss['avg_' + self.statitem1[0]], 0.)
        with self.assertRaises(IndexError):
            self.ss[100]
        with self.assertRaises(KeyError):
            self.ss[noattr(self.ss)]
        with self.assertRaises(TypeError):
            self.ss[object()]

    def test_len(self):
        ss = StatisticsSet(self.stat1, self.stat2, self.stat1)
        self.assertEqual(len(self.ss), 2)
        self.assertEqual(len(ss), 3)

    def test_getfields(self):
        self.assertEqual(self.ss.getfields(self.statitem1[0]),
                [{self.statitem1[0]: self.statitem1[1]()},
                 {self.statitem1[0]: self.statitem1[1]()}])

    def test_average(self):
        kwarg_map1 = {self.statitem1[0]: self.statitem1[1]() + 2}
        kwarg_map2 = {self.statitem1[0]: self.statitem1[1]() + 4}
        stat1 = Statistics(**kwarg_map1)
        stat2 = Statistics(**kwarg_map2)
        ss = StatisticsSet(stat1, stat2)
        self.assertEqual(ss.average(self.statitem1[0]), 3)

    def test_sum(self):
        kwarg_map1 = {self.statitem1[0]: self.statitem1[1]() + 2}
        kwarg_map2 = {self.statitem1[0]: self.statitem1[1]() + 4}
        stat1 = Statistics(**kwarg_map1)
        stat2 = Statistics(**kwarg_map2)
        ss = StatisticsSet(stat1, stat2)
        self.assertEqual(ss.sum(self.statitem1[0]), 6)

    def test_getvalues(self):
        self.assertEqual(self.ss.getvalues(self.statitem1[0]),
             [const.TRACKED_STATS[self.statitem1[0]]() for x in range(len(self.ss))])
