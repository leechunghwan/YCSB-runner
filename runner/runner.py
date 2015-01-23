import os
import sys
import subprocess

from .       import constants as const
from .config import RunnerConfig

class Runner:
    def __init__(self, configpath):
        """__init__

        :param configpath: Path to YCSB Runner configuration file
        """
        self.config = RunnerConfig(configpath)

    @classmethod
    def log(cls, message):
        print("<<YCSB Runner>>: %s" % str(message))

    def run(self):
        for db in self.config.dbs:
            for trial in range(1, trials + 1):
                for mpl in count(start=db.min_mpl, step=db.inc_mpl):
                Runner.log("Starting trial %i (%s)..." % (trial, db.labelname))
                # Clean the database
                Runner.log("Cleaning the database...")
                db.clean()
                # Load data and run YCSB
                Runner.log("Loading YCSB data...")
                self.__popen(db.cmd_ycsb_load(), save_output=False)
                Runner.log("Running YCSB workload...")
                self.__popen(db.cmd_ycsb_run(mpl), save_output=True )

    def __popen(self, cmd, save_output=False):
        """__popen
        Open a process given by the list of shell arguments, cmd

        :param cmd: List of shell arguments, including name of command as
        first element
        :param save_output: Whether or not to write the STDOUT and STDERR
        output of this command to the output logfile (default is False)
        """
        raise NotImplementedError
