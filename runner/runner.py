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
                    self.__popen(db.cmd_ycsb_load(), db)
                    db.log("Running YCSB workload...")
                    # Run YCSB+T, log output, collect stats
                    stats = Runner.extract_stats(self.__popen(db.cmd_ycsb_run(mpl), db))
                    # Set the MPL and trial number in the stats row
                    stats.mpl = mpl
                    stats.trial = trial
                    db.stats.addstats(stats)
            db.cleanup() # ensure file handles are closed properly and don't leak

    def __popen(self, cmd):
        """__popen
        Open a process given by the list of shell arguments, cmd

        Returns the stdout resulting from running the process

        :param cmd: List of shell arguments, including name of command as
        first element
        """
        try:
            with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
                # Collect and return stdout after running process
                stdout = proc.stdout.read().decode("utf-8")
                # Always print stdout back to stdout
                print(stdout)
                return stdout
        except OSError:
            # e.g. file doesn't exist, etc.
            return None

    @classmethod
    def extract_stats(cls, stdout):
        """__extract_stats
        Extracts statistics from the given YCSB+T output

        :param stdout: YCSB+T output from which statistics extraction should
        take place
        """
        stats = {}
        for k, regex in const.STAT_REGEXPS.items():
            m = Runner.get_re_match(regex, stdout)
            if m is not None:
                stats[k] = const.TRACKED_STATS[k](m)
        # Return new Statistics row storing extracted stats
        return Statistics(stats)

    @classmethod
    def get_re_match(cls, regex, string):
        """get_re_match
        Returns the contents of the first capturing group after running
        regex.search on the given string, or None if no matches found

        :param regex: Precompiled regex to run on string
        :param string: String on which to run regex
        """
        res = regex.search(string)
        if res != None and len(res.groups()) > 0:
            return res.group(1)
        return None
