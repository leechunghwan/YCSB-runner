import os
import sys
import tempfile
import unittest

from .helpers import *

import runner.constants as const
from runner.dbsystem import DbSystem
from runner.stats    import Statistics, StatisticsSet

class DbSystemTestCase(unittest.TestCase):
    def setUp(self):
        # Set the working directory to some temp dir
        self.tempdir = tempfile.TemporaryDirectory()
        self.__real_cwd = os.getcwd()
        os.chdir(self.tempdir.name)
        # Insert some sneaky values into const for test purposes (shh!)
        const.SUPPORTED_DBS['foobardb'] = 'foobar'
        const.SUPPORTED_DBS['barfoodb'] = None
        const.CLEAN_COMMANDS['foobardb'] = ['false']
        const.CLEAN_COMMANDS['barfoodb'] = ['true']
        # Set up the DbSystem instance
        self.dbname = 'foobardb'
        self.db = DbSystem(self.dbname, {
            'trials'    : 1,
            'min_mpl'   : 1,
            'max_mpl'   : 5,
            'inc_mpl'   : 1,
            'workload'  : 'foo',
            'output'    : 'csv',
            'output_dir': 'output',
            'avgkey'    : 'mpl',
            'avgfields' : ['runtime'],
            'plotkey'   : 'mpl',
            'plotfields': ['runtime'],
        })
        # We don't want any stdout, so redirect to null device (/dev/null)
        self.__real_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        self.db.cleanup()
        self.tempdir.cleanup()
        # Close /dev/null and re-assign stdout back to the real stdout
        sys.stdout.close()
        sys.stdout = self.__real_stdout
        # Change CWD back to real CWD
        os.chdir(self.__real_cwd)

    def test_getattr(self):
        self.assertEqual(self.db.trials, 1)
        self.assertEqual(self.db.max_mpl, 5)
        with self.assertRaises(AttributeError):
            getattr(self.db, noattr(self.db))

    def test_setattr(self):
        self.assertEqual(self.db.max_mpl, 5)
        self.db.max_mpl = 10
        self.assertEqual(self.db.max_mpl, 10)

    def test_labelname(self):
        self.assertEqual(self.db.label, "")
        self.db.label = ":foobar"
        self.assertEqual(self.db.label, ":foobar")
        self.assertEqual(self.db.labelname, self.dbname + ":foobar")

    def test_outdirpath(self):
        # Ensure ouput directory is in CWD
        self.assertEqual(os.path.dirname(os.path.dirname(self.db.outdirpath)),
            os.getcwd())
        # Ensure output directory exists
        self.assertTrue(os.path.exists(self.db.outdirpath))
        # Ensure output dir contains db labelname
        self.assertTrue(self.db.labelname in self.db.outdirpath)

    def test_cleanup(self):
        loghandle = self.db.logfile
        self.assertFalse(loghandle.closed)
        self.db.cleanup()
        self.assertTrue(loghandle.closed)

    def test_log(self):
        # Ensure log file exists and is in output dir
        loghandle = self.db.logfile
        self.assertTrue(os.path.exists(loghandle.name))
        # Test logging to the log file
        self.db.log("TestFoobar")
        self.db.cleanup()
        self.assertTrue(loghandle.closed)
        with open(loghandle.name) as lh:
            cts = lh.read()
        self.assertTrue("TestFoobar" in cts)
        self.assertTrue(const.LOG_LINE_PREFIX.replace(" %s", "") in cts)

    def test_raw_log(self):
        # Ensure log file exists and is in output dir
        loghandle = self.db.logfile
        self.assertTrue(os.path.exists(loghandle.name))
        # Test logging to the log file
        self.db.raw_log("TestFoobar")
        self.db.cleanup()
        self.assertTrue(loghandle.closed)
        with open(loghandle.name) as lh:
            cts = lh.read()
        self.assertTrue("TestFoobar" in cts)

    def test_export_stats(self):
        self.db.stats.addstats(Statistics(mpl=1, runtime=3.),
                Statistics(mpl=2, runtime=6.))
        self.db.output_plots = False
        self.assertFalse(self.db.output_plots)
        self.assertTrue(len(os.listdir(self.db.outdirpath)) == 0)
        self.db.export_stats()
        self.assertTrue(len(os.listdir(self.db.outdirpath)) == 2)

    def test_export_stats_and_plots(self):
        self.db.stats.addstats(Statistics(mpl=1, runtime=5.),
                Statistics(mpl=2, runtime=8.))
        self.db.output_plots = True
        self.assertTrue(self.db.output_plots)
        self.assertTrue(len(os.listdir(self.db.outdirpath)) == 0)
        self.db.export_stats()
        self.assertTrue(len(os.listdir(self.db.outdirpath)) == 3)

    def test_workload_path(self):
        # Ensure workload path is in CWD
        self.assertEqual(os.path.dirname(self.db.workload_path), os.getcwd())
        # Test the workload name we gave in setUp()
        self.assertTrue(self.db.workload_path.endswith("foo"))

    def test_cmd_ycsb_load(self):
        self.assertEqual(self.db.dbname, 'foobardb')
        self.assertTrue('foobar' in self.db.cmd_ycsb_load())
        self.db.dbname = 'barfoodb'
        self.assertTrue('barfoodb' in self.db.cmd_ycsb_load())
        self.assertTrue(self.db.workload_path in self.db.cmd_ycsb_load())

    def test_cmd_ycsb_run(self):
        self.assertEqual(self.db.dbname, 'foobardb')
        self.assertTrue('foobar' in self.db.cmd_ycsb_run(123456789))
        self.db.dbname = 'barfoodb'
        self.assertTrue('barfoodb' in self.db.cmd_ycsb_run(123456789))
        self.assertTrue(self.db.workload_path in self.db.cmd_ycsb_run(123456789))
        self.assertTrue('123456789' in self.db.cmd_ycsb_run(123456789))
        self.assertTrue('987654321' in self.db.cmd_ycsb_run(987654321))

    # Note: this probably only passes when running on Unix-compliant systems
    # due to its reliance on the true and false commands
    def test_clean(self):
        self.assertEqual(self.db.dbname, 'foobardb')
        with self.assertRaises(RuntimeError):
            self.db.clean()
        self.db.dbname = 'barfoodb'
        self.assertEqual(self.db.clean(), 0)

    def test_stats(self):
        self.assertTrue(isinstance(self.db.stats, StatisticsSet))
        self.assertEqual(self.db.stats, self.db._DbSystem__stats)

    def test_makefpath(self):
        path = self.db.makefpath("test-file-{}-{}")
        self.assertTrue(os.path.basename(path).startswith("test-file-"))
        self.assertEqual(os.path.dirname(path), self.db.outdirpath)
