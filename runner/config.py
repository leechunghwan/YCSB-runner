import os
import re
import configparser

from .          import constants as const
from .dbsystem  import DbSystem

class RunnerConfig:
    """RunnerConfig: Reads and parses a YCSB Runner config file
    (INI-compliant format)"""

    def __init__(self, configfile):
        """__init__

        :param configfile: Path to the runner configuration file
        """
        # Check that the configfile exists before reading it
        if not os.path.exists(configfile):
            raise IOError("Runner config file '%s' does not exist" % configfile)
        # Read the config with Python's ConfigParser first
        self.config = configparser.ConfigParser(defaults=const.OPTION_DEFAULTS)
        self.config.read(configfile)
        # Now, process the config further, extracting DBMS names, options
        self.dbs = self.__process_sections()

    def __process_sections(self):
        """__process_sections

        Processes each section in the config file,
        populating this object with corresponding DbSystem instances
        """
        dbs = []
        for section in self.config.sections():
            config = self.__process_config_keys(section)
            dbs += self.__process_dbs(section, config)
        return dbs

    def __process_config_keys(self, section):
        """__process_config_keys

        :param section: Name of section from runner config file for which
        k=v options should be processed
        """
        config = {}
        for k, t in const.OPTION_KEYS.items():
            # Handle integer-valued keys
            if type(t) is int:
                config[k] = self.config.getint(section, k)
            # Handle boolean-valued keys
            elif type(t) is bool:
                config[k] = self.config.getboolean(section, k)
            # Handle string-valued keys
            elif type(t) is str:
                config[k] = self.config.get(section, k)
            elif callable(t):
                config[k] = t(self.config.get(section, k))
            else:
                print("Warning: skipping key %s with invalid type" % k)
        return config

    def __process_dbs(self, section, config):
        """__process_dbs

        Creates DbSystem instances with their corresponding configurations for
        each DBMS in the runner config

        :param section:
        :param config:
        """
        # Section headings may contain multiple DB names, CSV format
        section = [s.strip() for s in section.split(',')]
        db_instances = []
        for db in section:
            # Extract and remove the DBMS label
            label = const.RE_DBNAME_LABEL.search(db)
            if label is not None:
                label, = label.groups(0)
                db = const.RE_DBNAME_LABEL.sub("", db)
            else:
                label = ""
            # Validate DBMS name
            if db.lower() not in const.SUPPORTED_DBS:
                print("Invalid database found: %s. Only (%s) are supported. Skipping..." %
                        (db, ','.join(const.SUPPORTED_DBS)))
                continue

            # Get the tablename, or use default
            # TODO: Maybe grab this from the workload config file instead of
            # the runner config?
            tablename = self.config.get(db+label, "tablename", fallback=const.DEFAULT_TABLENAME)
            # Build the DbSystem object
            db_instances.append(DbSystem(db, config, label=label,
                tablename=tablename))
        return db_instances
