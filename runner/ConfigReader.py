import re
import configparser

from .DbSystem import DbSystem

# Supported output formats
SUPPORTED_OUTPUTS = ['csv']

# Supported database systems
SUPPORTED_DBS = [
    'jdbc',
    'mongodb',
    'redis',
    'cassandra-10',
]

# Matches labels (bits after : in dbname config sections)
# Database names may be labelled for reference, and so that the same DBMS can
# be configured twice in two different sections. Labels are ignored by the
# runner script under all circumstances; they are merely for differentiation
# and reference purposes.
# labels may look like this:
#     [foodb:labelhere_blah]
# where after : is the label, which may contain A-Z, a-z, 0-9, _, and -
RE_DBNAME_LABEL = re.compile(r"(:[A-Za-z0-9_-]+$)")

# Commands for truncating each DBMS
# NOTE: PostgreSQL requires the database user password to be specified in a
# .pgpass file in the user's home directory
CLEAN_COMMANDS = {
    'mysql': [
        "mysql",
        "-u",
        "ycsb",
        "-pycsb",
        "-e",
        "TRUNCATE TABLE usertable;",
        "ycsb"
    ],
    'psql': [
        "psql",
        "--host",
        "localhost",
        "-d",
        "ycsb",
        "-U",
        "ycsb",
        "-c",
        "TRUNCATE TABLE usertable;"
    ],
    'mongodb': [
        "mongo",
        "--host",
        "localhost",
        "--eval",
        "db.dropDatabase();",
        "ycsb"
    ],
    'redis': [
        "redis-cli",
        "-r",
        "1",
        "FLUSHALL"
    ],
    'cassandra-10': [
        "cqlsh",
        "-k",
        "usertable",
        "-e",
        "TRUNCATE data;"
    ],
}

# Regex precompilation
REGEXPS = {
    'totalcash'    : re.compile(r"TOTAL CASH], ([0-9]+)"),
    'countcash'    : re.compile(r"COUNTED CASH], ([0-9]+)"),
    'opcount'      : re.compile(r"ACTUAL OPERATIONS], ([0-9]+)"),
    'runtime'      : re.compile(r"OVERALL], RunTime.+?, ([0-9.]+)"),
    'throughput'   : re.compile(r"OVERALL], Throughput.+?, ([0-9.]+)"),
}

class RunnerConfiguration:
    """RunnerConfiguration: Reads and parses a YCSB Runner config file
    (INI-compliant format)"""
    # trials        =   Number of times to run workload for each MPL
    # min_mpl       =   min YCSB threads
    # max_mpl       =   max YCSB threads
    # inc_mpl       =   YCSB thread increase increment
    # output        =   output format
    # workload      =   workload file path
    # output_plots  =   whether to generate plots
    OPTION_KEYS = {
        'trials'      : int(),
        'min_mpl'     : int(),
        'max_mpl'     : int(),
        'inc_mpl'     : int(),
        'output'      : lambda s: str(s).lower(),
        'workload'    : str(),
        'output_plots': bool(),
    }

    def __init__(self, configfile):
        """__init__

        :param configfile: Path to the runner configuration file
        """
        # Read the config with Python's ConfigParser first
        self.config = configparser.ConfigParser()
        self.config.read(configfile)
        # Now, process the config further, extracting DBMS names, options
        self.dbs = self.__process_sections()

    def __process_sections(self):
        """__process_sections
        Processes each section in the config file,
        populating this object with corresponding DbSystem instances"""
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
        for k, t in self.OPTION_KEYS.items():
            # Handle integer-valued keys
            if type(t) is type(int()):
                config[k] = self.config.getint(section, k)
            # Handle boolean-valued keys
            elif type(t) is type(bool()):
                config[k] = self.config.getboolean(section, k)
            # Handle string-valued keys
            elif type(t) is type(str()):
                config[k] = self.config.get(section, k)
            elif callable(t):
                config[k] = t(self.config.get(section, k))
            else:
                print("Warning: skipping key %s with invalid type" % k)
        return config

    def __process_dbs(self, section, config):
        # Section headings may contain multiple DB names, CSV format
        section = [s.strip() for s in section.split(',')]
        db_instances = []
        for db in section:
            # Extract and remove the DBMS label
            label = RE_DBNAME_LABEL.search(db)
            if label is not None:
                label, = label.groups(0)
                db = RE_DBNAME_LABEL.sub("", db)
            else:
                label = ""
            # Validate DBMS name
            if db.lower() not in SUPPORTED_DBS:
                print("Invalid database found: %s. Only (%s) are supported. Skipping..." %
                        (db, ','.join(SUPPORTED_DBS)))
                continue
            # Build the DbSystem object
            db_instances.append(DbSystem(db, config, label=label))
        return db_instances
