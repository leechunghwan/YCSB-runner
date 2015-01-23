import os
import sys
import subprocess

from shutil    import copyfile
from itertools import count

from .         import constants as const
from .config   import RunnerConfig

class Runner:
    """Runner: Makes Popen calls to run YCSB, collects output, extracts data
    from YCSB output, handles logging"""
    def __init__(self, configpath):
        """__init__

        :param configpath: Path to YCSB Runner configuration file
        """
        self.config = RunnerConfig(configpath)

    def run(self):
        for db in self.config.dbs:
            for trial in range(1, trials + 1):
                for mpl in count(start=db.min_mpl, step=db.inc_mpl):
                db.log("Starting trial %i (%s)..." % (trial, db.labelname))
                # Clean the database
                db.log("Cleaning the database...")
                db.clean()
                # Load data and run YCSB
                db.log("Loading YCSB data...")
                self.__popen(db.cmd_ycsb_load(), save_output=False)
                db.log("Running YCSB workload...")
                self.__popen(db.cmd_ycsb_run(mpl), save_output=True)
            db.cleanup() # ensure file handles are closed properly and don't leak

    def __popen(self, cmd):
        """__popen
        Open a process given by the list of shell arguments, cmd

        :param cmd: List of shell arguments, including name of command as
        first element
        """
        raise NotImplementedError
