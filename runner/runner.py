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

    def log(self, message):
        """log
        Logs the given message to the output log and STDOUT
        This should be used for messages specifically for the user to see.

        :param message:
        """
        message = "<<YCSB Runner>>: %s" % str(message)
        # TODO: Log to logfile
        print(message)

    def run(self):
        for db in self.config.dbs:
            for trial in range(1, trials + 1):
                for mpl in count(start=db.min_mpl, step=db.inc_mpl):
                self.log("Starting trial %i (%s)..." % (trial, db.labelname))
                # Clean the database
                self.log("Cleaning the database...")
                db.clean()
                # Load data and run YCSB
                self.log("Loading YCSB data...")
                self.__popen(db.cmd_ycsb_load(), save_output=False)
                self.log("Running YCSB workload...")
                self.__popen(db.cmd_ycsb_run(mpl), save_output=True )

    @property
    def __logfile(self):
        raise NotImplementedError

    def __popen(self, cmd, save_output=False):
        """__popen
        Open a process given by the list of shell arguments, cmd

        :param cmd: List of shell arguments, including name of command as
        first element
        :param save_output: Whether or not to write the STDOUT and STDERR
        output of this command to the output logfile (default is False)
        """
        raise NotImplementedError
