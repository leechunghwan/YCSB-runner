import os
import sys
import subprocess

from shutil    import copyfile
from itertools import count

from .         import constants as const
from .config   import RunnerConfig
from .stats    import Statistics

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
            for trial in range(1, db.trials + 1):
                for mpl in count(start=db.min_mpl, step=db.inc_mpl):
                    # Obvious; don't go above configured maximum MPL
                    if mpl > db.max_mpl:
                        break
                    db.log("Starting trial %i..." % (trial), mpl=mpl, trial=trial)
                    # Clean the database
                    db.log("Cleaning the database...", mpl=mpl, trial=trial)
                    db.clean()
                    # Load data and run YCSB
                    db.log("Loading YCSB data...", mpl=mpl, trial=trial)
                    self.__popen(db.cmd_ycsb_load())
                    db.log("Running YCSB workload...", mpl=mpl, trial=trial)
                    # Run YCSB+T, log output, collect stats
                    stats = Runner.extract_stats(self.__popen(db.cmd_ycsb_run(mpl)))
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
        with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
            # Collect and return stdout after running process
            stdout = proc.stdout.read().decode("utf-8")
            # If this doesn't hold then something is horribly wrong and we
            #   should abort mission
            assert type(stdout) is str
            # Always print stdout back to stdout
            print(stdout)
            return stdout

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
        return Statistics(**stats)

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
