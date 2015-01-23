import os

from datetime import datetime

from .        import constants as const

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

    # Gets attributes from the configuration dict
    def __getattr__(self, name):
        if name in self.config:
            return self.config[name]
        raise AttributeError

    # Sets attributes in the configuration dict
    def __setattr__(self, name, value):
        if (name != 'config' and name in self.config and
                type(value) == type(self.config[name])):
            self.config[name] = value
        else:
            object.__setattr__(self, name, value)

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
        return self.__outdir

    @property
    def logfile(self):
        """logfile
        A Python file object for the output logfile for this database
        """
        if self.__logfile == None or self.__logfile.closed:
            lfname = "log-{}-{}.log".format(self.labelname, self.__datestr)
            lfpath = os.path.join(self.outdirpath, lfname)
            self.__logfile = open(lfpath, 'w')

    def log(self, message, lf=True):
        """log
        Logs the given message to the output log and STDOUT
        This should be used for messages specifically for the user to see.

        :param message:
        """
        message = str(message) # ensure message is always a string
        print(const.LOG_LINE_PREFIX % message)
        if lf:
            print(const.LOG_LINE_PREFIX % message, file=self.logfile)

    def cleanup(self):
        """cleanup
        Close file handles and perform clean-up.
        This should be called when this DB has been processed.
        """
        if self.__logfile != None and not self.__logfile.closed:
            self.logfile.close()

    @property
    def workload_path(self):
        """workload_path
        Path to the YCSB workload file for this DB instance
        """
        return os.path.join(os.getcwd(), self.workload),

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
        """
        if self.dbname.lower() == "jdbc":
            subprocess.call(self.__tablenameify(CLEAN_COMMANDS['mysql']))
            subprocess.call(self.__tablenameify(CLEAN_COMMANDS['psql']))
        else:
            subprocess.call(self.__tablenameify(CLEAN_COMMANDS[self.dbname.lower()]))
