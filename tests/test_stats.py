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
        self.stats.totalcash = 100.
        self.stats.countcash = 123.
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

class StatisticsSetTestCase(unittest.TestCase):
    def setUp(self):
        self.stat1 = Statistics()
        self.stat2 = Statistics()
        self.ss = StatisticsSet(self.stat1, self.stat2)

    def test_init(self):
        ss = StatisticsSet()
        self.assertEqual(ss.items(), [])
        self.assertEqual(self.ss.items(), [self.stat1, self.stat2])

    def test_getattr(self):
        self.assertIsNone(self.ss.avg_anomaly_score)
        self.assertEqual(self.ss.avg_runtime, 0.)
        with self.assertRaises(AttributeError):
            self.ss.__qwertyuiopasdfghjklzxcvbnm

    def test_getitem(self):
        self.assertIsInstance(self.ss[0], Statistics)
        self.assertIsInstance(self.ss[1], Statistics)
        self.assertEqual(self.ss[0], self.stat1)
        self.assertEqual(self.ss[1], self.stat2)
        self.assertEqual(self.ss['avg_runtime'], 0.)
        with self.assertRaises(IndexError):
            self.ss[100]
        with self.assertRaises(KeyError):
            self.ss['__qwertyuiopasdfghjklzxcvbnm']
        with self.assertRaises(TypeError):
            self.ss[object()]

    def test_len(self):
        ss = StatisticsSet(self.stat1, self.stat2, self.stat1)
        self.assertEqual(len(self.ss), 2)
        self.assertEqual(len(ss), 3)

    def test_getfields(self):
        self.assertEqual(self.ss.getfields('mpl'), [{'mpl': 0.}, {'mpl': 0.}])

    def test_average(self):
        stat1 = Statistics(mpl=2)
        stat2 = Statistics(mpl=4)
        ss = StatisticsSet(stat1, stat2)
        self.assertEqual(ss.average('mpl'), 3)

    def test_sum(self):
        stat1 = Statistics(mpl=2)
        stat2 = Statistics(mpl=4)
        ss = StatisticsSet(stat1, stat2)
        self.assertEqual(ss.sum('mpl'), 6)

    def test_getvalues(self):
        self.assertEqual(self.ss.getvalues('mpl'),
             [const.TRACKED_STATS['mpl']() for x in range(len(self.ss))])
