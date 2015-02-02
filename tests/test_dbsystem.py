import os
import sys
import tempfile
import unittest

from .helpers import *

import runner.constants as const
from runner.dbsystem import DbSystem
from runner.stats    import Statistics

class DbSystemTestCase(unittest.TestCase):
    def setUp(self):
        # Set the working directory to some temp dir
        self.tempdir = tempfile.TemporaryDirectory()
        self.__real_cwd = os.getcwd()
        os.chdir(self.tempdir.name)
        # Set up the DbSystem instance
        self.dbname = getone(const.SUPPORTED_DBS.keys())
        self.db = DbSystem(self.dbname, {
            'trials': 1,
            'min_mpl': 1,
            'max_mpl': 5,
            'inc_mpl': 1,
            'workload': 'foo',
            'output': 'csv',
            'output_dir': 'output',
            'statskey': 'mpl',
            'statsfields': ['runtime'],
            'plotkey': 'mpl',
            'plotfields': ['runtime'],
        })
        # We don't want any stdout, so redirect to null device (/dev/null)
        self.__real_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        # Change CWD back to real CWD
        os.chdir(self.__real_cwd)

    def tearDown(self):
        self.db.cleanup()
        self.tempdir.cleanup()
        # Close /dev/null and re-assign stdout back to the real stdout
        sys.stdout.close()
        sys.stdout = self.__real_stdout

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
        pass

    def test_cmd_ycsb_load(self):
        pass

    def test_cmd_ycsb_run(self):
        pass

    def test_clean(self):
        pass

    def test_stats(self):
        pass

    def test_makefpath(self):
        pass
