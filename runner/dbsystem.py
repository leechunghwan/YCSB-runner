import os

from .constants import *

class DbSystem:
    # A list of required configuration fields
    REQUIRED_FIELDS = [
        'trials' , 'min_mpl' , 'max_mpl',
        'inc_mpl', 'workload'
    ]

    def __init__(self, dbname, config, label="", tablename=DEFAULT_TABLENAME):
        self.dbname = dbname
        self.label = label
        self.tablename = tablename
        self.config = config

    # Gets attributes from the configuration dict
    def __getattr__(self, name):
        if name in self.config:
            return self.config[name]
        else:
            return super(DbSystem, self).__getattr__(name)

    # Sets attributes in the configuration dict
    def __setattr(self, name, value):
        if name in self.config and type(value) == type(self.config[name]):
            self.config[name] = value
        else:
            super(DbSystem, self).__setattr__(name, value)

    def __validate_config(self, config):
        """__validate_config
        Ensure the given config dict contains all required keys, and no
        extraneous keys

        Raises an AttributeError for invalid or missing keys

        :param config: dict of configuration key -> value mappings
        """
        for k in config:
            if k not in REQUIRED_FIELDS:
                raise AttributeError("Key %s is not a configuration parameter" % k)
        for k in REQUIRED_FIELDS:
            if k not in self.config:
                raise AttributeError("Missing required configuration parameter: %s" % k)
        return true # presumably nothing was raised and all is well

    def __tablenameify(self, lst):
        """__tablenameify

        Replaces {TABLENAME} with the configured name of the YCSB+T table in
        the given list of strings

        :param lst: List of strings within which {TABLENAME} should be subbed
        """
        return [s.replace("{TABLENAME}", self.tablename) for s in lst]

    def workload_path(self):
        return os.path.join(os.getcwd(), self.workload),

    def construct_ycsb_load(self):
        """build_ycsb_load

        Creates the YCSB load command as a list that may be passed to Popen
        """
        return [
            "ycsb",
            "load",
            self.dbname,
            "-P",
            self.workload_path(),
            "-s",
            "-threads",
            "1",
        ]

    def construct_ycsb_run(self, mpl):
        """build_ycsb_run

        Creates the YCSB run command as a list that may be passed to Popen
        """
        return [
            "ycsb",
            "run",
            self.dbname,
            "-P",
            self.workload_path(),
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
