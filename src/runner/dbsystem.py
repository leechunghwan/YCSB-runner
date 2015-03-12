import os
import sys
import tempfile
import subprocess

from pyjavaproperties import Properties
from datetime import datetime

from .      import constants as const
from .stats import Statistics, StatisticsSet

class DbSystem:
    # A list of required configuration fields
    __REQUIRED_FIELDS = [
        'trials'    , 'min_mpl'   , 'max_mpl',
        'inc_mpl'   , 'workload'  , 'output',
        'output_dir', 'avgkey'    , 'avgfields',
        'plotkey'   , 'plotfields',
    ]

    def __init__(self, dbname, config, label="",
            tablename=const.DEFAULT_TABLENAME, extraneous_config=None):
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
        self.__temp_workload_file = None
        self.__base_workload_props = None
        # Set up the YCSB workload file
        self.workload_config = self.__generate_workload_config(extraneous_config)
        self.__create_temp_workload_file()

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

    def __generate_workload_config(self, extraneous_config):
        # Read base workload properties into a dict if we haven't already
        if self.__base_workload_props is None:
            props = Properties()
            with open(self.workload_path) as wf:
                props.load(wf)
            self.__base_workload_props = props.getPropertyDict()
        if extraneous_config is None:
            extraneous_config = {}
        # Merge base workload properties with extraneous options
        workload_config = dict(self.__base_workload_props)
        workload_config.update(extraneous_config)
        # Merge and return the workload config dict
        return workload_config

    def __create_temp_workload_file(self):
        """__create_temp_workload_file
        Create a 'working' workload file from self.workload_config, update
        self.__temp_workload_file to store the file object of this new
        working workload file
        """
        temp_workload_file = tempfile.NamedTemporaryFile(mode='w')
        self.generate_workload_file(temp_workload_file.name)
        self.__temp_workload_file = temp_workload_file

    def __templateify(self, lst):
        """__templateify
        Replaces {PLACEHOLDERS} in the given list of strings

        :param lst: List of strings within which {PLACEHOLDERS} should be
                    subbed
        """
        # Handle DBMS-specific config substitutions
        # This is all a bit hacky, but it's fiiiiiiiiine, it's just code
        jdbc_config  = dict(const.CLEAN_DEFAULT_JDBC)
        mongo_config = dict(const.CLEAN_DEFAULT_MONGO)
        # JDBC-specific configuration
        if 'db.url' in self.workload_config:
            match = const.RE_HOSTNAME_PORT.search(self.workload_config['db.url'])
            if match:
                jdbc_config['host'], jdbc_config['port'] = match.groups()
        # Handle JDBC auth options
        for k in ('user', 'passwd', 'dbname'):
            dbK = 'db'+k
            if dbK in self.workload_config:
                jdbc_config[k] = self.workload_config[dbK]
        # Mongo-specific configuration
        if 'mongodb.url' in self.workload_config:
            match = const.RE_HOSTNAME_PORT.search(self.workload_config['db.url'])
            if match:
                mongo_config['host'], mongo_config['port'] = match.groups()
        if 'mongodb.database' in self.workload_config:
            mongo_config['dbname'] = self.workload_config['mongodb.database']
        # Build a substitution map
        subst = {
            "TABLENAME" : self.tablename,
        }
        # Add entries from {JDBC,MONGO}_CONFIG to subst, in the form
        #   {JDBC,MONGO}_{PORT,USER,PASSWD,DBNAME}
        subst.update({"JDBC_" +k.upper(): v for k, v in jdbc_config.items()})
        subst.update({"MONGO_"+k.upper(): v for k, v in mongo_config.items()})

        # Perform substitutions
        for k, v in subst.items():
            lst = [s.replace("{" + str(k) + "}", str(v)) for s in lst]
        return lst

    @property
    def clean_data(self):
        """cleandata: Decide whether or not the DBMA data should be cleaned
        and reloaded with 'ycsb load'"""
        if "clean_data" in self.config and self.config["clean_data"] == True:
            # We still clean the DBMS at the start of each trial, just not
            # between MPL increases
            return True if self.mpl == self.min_mpl else False
        else:
            return True

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
            self.__outdir = os.path.join(os.getcwd(), self.output_dir, self.__datestr +
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
            lfpath = self.makefpath("log-{}-{}.log")
            self.__logfile = open(lfpath, 'w', 1)
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
        message = "[%s] [%s] %s" % (self.__datestr, self.labelname, message)
        print(const.LOG_LINE_PREFIX % message)
        if lf:
            print(const.LOG_LINE_PREFIX % message, file=self.logfile)
        return message

    def raw_log(self, string, stdout=True):
        """raw_log
        Log a raw string directly to the output file, and to stdout.

        Returns the string passed in

        :param string: Raw string to be logged
        """
        string = str(string)
        print(string, file=self.logfile)
        if stdout:
            print(string)
        return string

    def cleanup(self):
        """cleanup
        Close file handles and perform clean-up.
        This should be called AFTER this DB has been processed.

        **NOTE** This is VERY different to DbSystem.clean(), which purges all
        YCSB data from the DBMS
        """
        if self.__logfile != None and not self.__logfile.closed:
            self.__logfile.close()
        if self.__temp_workload_file != None:
            self.__temp_workload_file.close()

    def export_stats(self):
        """export_stats
        Writes output to the output directory using some Exporter
        """
        exporter = const.SUPPORTED_OUTPUTS[self.output](self.stats)
        file_output   = self.makefpath("output-{}-{}")
        file_averages = self.makefpath("averages-{}-{}")
        file_plot     = self.makefpath("plot-{}-{}")
        # Export averages
        exporter.export_averages(file_averages, self.avgkey,
                *self.avgfields)
        # Export all data
        exporter.export(file_output, self.avgkey, *self.exportfields)
        # Output averages plot if configured
        if self.output_plots:
            exporter.export_averages_plot(file_plot, "{} {}".format(
                self.labelname, self.__datestr),
                    self.plotkey, *self.plotfields)

    @property
    def workload_path(self):
        """workload_path
        Path to the YCSB workload file for this DB instance
        """
        if self.__temp_workload_file is None:
            return self.base_workload_path
        else:
            return os.path.abspath(self.__temp_workload_file.name)
    @property
    def base_workload_path(self):
        """base_workload_path
        Path to the base YCSB workload file for this DB instance
        """
        return os.path.join(os.getcwd(), self.workload)

    def generate_workload_file(self, path=None):
        """generate_workload_file
        Writes the workload configuration dictionary to a workload file

        :param path: Path to file in which workload config should be written.
            If not given, self.workload_path will be used.
        """
        if path is None:
            path = self.workload_path
        with open(path, 'w') as f:
            for k, v in sorted(self.workload_config.items()):
                f.write("{}={}\n".format(k, v))

    def cmd_ycsb_load(self):
        """cmd_ycsb_load
        Gets the YCSB load command as a list that may be passed to Popen
        """
        return [
            "ycsb",
            "load",
            self.__ycsb_dbname(self.dbname),
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
            self.__ycsb_dbname(self.dbname),
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
        excode = subprocess.call(self.__templateify(const.CLEAN_COMMANDS[self.dbname.lower()]))
        # We don't want to continue if cleaning the DB failed (see #7)
        if excode != 0:
            raise RuntimeError("Error: db.clean() did not complete " +
                "successfully for DB %s" % self.dbname.lower())
        return excode

    @property
    def stats(self):
        """stats
        An instance of stats.StatisticsSet to store YCSB+T output statistics for
        this DBMS
        """
        if self.__stats is None:
            self.__stats = StatisticsSet()
        return self.__stats

    def makefpath(self, fstr):
        """makefpath
        Given a filename containing two format string spaces ({} {}), returns
        the full path to that file in the output directory, inserting the
        database name and timestamp into the format string spaces.

        :param fstr: A format string to become the name of an output file.
        """
        return os.path.join(self.outdirpath, self.__makefname(fstr))

    def __makefname(self, fstr):
        return fstr.format(self.labelname, self.__datestr)

    def __ycsb_dbname(self, runner_dbname):
        """__ycsb_dbname
        Maps a YCSB-runner database name to the name used by YCSB (uses simple
        lookup in const.SUPPORTED_DBS)
        """
        if const.SUPPORTED_DBS[runner_dbname] != None:
            return const.SUPPORTED_DBS[runner_dbname]
        return runner_dbname
