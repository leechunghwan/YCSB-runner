import os
import subprocess

from datetime import datetime

from .      import constants as const
from .stats import Statistics, StatisticsSet

class DbSystem:
    # A list of required configuration fields
    __REQUIRED_FIELDS = [
        'trials' , 'min_mpl' , 'max_mpl',
        'inc_mpl', 'workload'
    ]

    def __init__(self, dbname, config, label="", tablename=const.DEFAULT_TABLENAME):
        # Ensure we have all required fields
        self.__validate_config(config)
        # Set public instance vars
        self.config = config
        self.dbname = dbname
        self.label = label
        self.tablename = tablename
        # Private instance vars
        self.__datestr = datetime.now().isoformat()
        self.__outdir = None
        self.__stats = None
        self.__logfile = None

    # Gets attributes from the configuration dict
    def __getattr__(self, name):
        if name in self.config:
            return self.config[name]
        raise AttributeError("Attribute '%s' not found" % name)

    # Sets attributes in the configuration dict
    def __setattr__(self, name, value):
        if (name != 'config' and name in self.config and
                type(value) == type(self.config[name])):
            self.config[name] = value
        else:
            object.__setattr__(self, name, value)

    def __dir__(self):
        objdir = list(dir(super(DbSystem, self)))
        objdir += list(self.__dict__.keys())
        objdir +=  list(self.config.keys())
        return objdir

    def __validate_config(self, config):
        """__validate_config
        Ensure the given config dict contains all required keys, and no
        extraneous keys
        Raises an AttributeError for invalid or missing keys

        :param config: dict of configuration key -> value mappings
        """
        for k in self.__REQUIRED_FIELDS:
            if k not in config:
                raise AttributeError("Missing required configuration parameter: %s" % k)
        return True # presumably nothing was raised and all is well

    def __tablenameify(self, lst):
        """__tablenameify
        Replaces {TABLENAME} with the configured name of the YCSB+T table in
        the given list of strings

        :param lst: List of strings within which {TABLENAME} should be subbed
        """
        return [s.replace("{TABLENAME}", self.tablename) for s in lst]

    @property
    def labelname(self):
        """labelname
        The name of the database with its label
        """
        return self.dbname + self.label

    @property
    def outdirpath(self):
        """outdirpath
        Name and path to the directory for output for this DBMS
        """
        if self.__outdir == None:
            self.__outdir = os.path.join(".", "output", self.__datestr +
                    "-{}".format(self.labelname))
        # Make the output dir if it doesn't exist, since we might as well do
        #   this ASAP
        if not os.path.exists(self.__outdir):
            os.makedirs(self.__outdir)
        return self.__outdir

    @property
    def logfile(self):
        """logfile
        A Python file object for the output logfile for this database
        """
        if self.__logfile == None or self.__logfile.closed:
            lfpath = self.__makefpath("log-{}-{}.log")
            self.__logfile = open(lfpath, 'w')
        return self.__logfile

    def log(self, message, lf=True, mpl=None, trial=None):
        """log
        Logs the given message to the output log and STDOUT
        This should be used for messages specifically for the user to see.

        Returns the message

        :param message: Message to be logged
        :param lf: Whether or not to write message to the logfile for this DB
        :param mpl: The current MPL (will be displayed if set)
        :param trial: The current trial number (will be displayed if set)
        """
        message = str(message)
        # Add MPL and trial number if provided
        if mpl is not None:
            message = "(MPL=%s) %s" % (mpl, message)
        if trial is not None:
            message = "(Trial=%s) %s" % (trial, message)
        # Prepend dbname to message for user reference
        message = "[%s] %s" % (self.labelname, message)
        print(const.LOG_LINE_PREFIX % message)
        if lf:
            print(const.LOG_LINE_PREFIX % message, file=self.logfile)
        return message

    def cleanup(self):
        """cleanup
        Close file handles and perform clean-up.
        This should be called AFTER this DB has been processed.

        **NOTE** This is VERY different to DbSystem.clean(), which purges all
        YCSB data from the DBMS
        """
        if self.__logfile != None and not self.__logfile.closed:
            self.__logfile.close()

    def export_stats(self):
        exporter = const.SUPPORTED_OUTPUTS[self.output](self.stats)
        file_output   = self.__makefpath("output-{}-{}.csv")
        file_averages = self.__makefpath("averages-{}-{}.csv")
        file_plot     = self.__makefpath("plot-{}-{}.pdf")
        # Export averages
        exporter.export_averages(file_averages, self.statskey,
                *self.statsfields)
        # Export all data
        exporter.export(file_output, self.statskey,
                *const.TRACKED_STATS.keys())
        # Output averages plot if configured
        if self.output_plots:
            exporter.export_averages_plot(file_plot, self.labelname,
                    self.plotkey, *self.plotfields)

    @property
    def workload_path(self):
        """workload_path
        Path to the YCSB workload file for this DB instance
        """
        return os.path.join(os.getcwd(), self.workload)

    def cmd_ycsb_load(self):
        """cmd_ycsb_load
        Gets the YCSB load command as a list that may be passed to Popen
        """
        return [
            "ycsb",
            "load",
            self.dbname,
            "-P",
            self.workload_path,
            "-s",
            "-threads",
            "1",
        ]

    def cmd_ycsb_run(self, mpl):
        """cmd_ycsb_run
        Gets the YCSB run command as a list that may be passed to Popen
        """
        return [
            "ycsb",
            "run",
            self.dbname,
            "-P",
            self.workload_path,
            "-s",
            "-threads",
            str(mpl),
        ]

    def clean(self):
        """clean
        Cleans all YCSB+T data from the database by calling the corresponding
        clean command (configured in constants.py)

        This should be called BEFORE the DB is processed
        """
        if self.dbname.lower() == "jdbc":
            subprocess.call(self.__tablenameify(const.CLEAN_COMMANDS['mysql']))
            subprocess.call(self.__tablenameify(const.CLEAN_COMMANDS['psql']))
        else:
            subprocess.call(self.__tablenameify(const.CLEAN_COMMANDS[self.dbname.lower()]))

    @property
    def stats(self):
        """stats
        An instance of stats.StatisticsSet to store YCSB+T output statistics for
        this DBMS
        """
        if self.__stats is None:
            self.__stats = StatisticsSet()
        return self.__stats

    def __makefname(self, fstr):
        return fstr.format(self.labelname, self.__datestr)

    def __makefpath(self, fstr):
        return os.path.join(self.outdirpath, self.__makefname(fstr))
