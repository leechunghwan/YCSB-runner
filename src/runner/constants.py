import re

from .             import const_helpers as helpers
from .csv_exporter import CsvExporter

### OUTPUTS ########################################################

# Supported output formats
SUPPORTED_OUTPUTS = {
    'csv': CsvExporter,
}
####################################################################

### DATABASES: #####################################################

# Supported database systems
# The runner can use different names to YCSB, provided this mapping correctly
# maps the name used by the runner to the name used by YCSB. This might be
# desirable, for example, to distinguish two different DBMSes using the same
# YCSB implementation (e.g. MySQL and PostgreSQL, which both use JDBC)
SUPPORTED_DBS = {
    'jdbc-mysql'    : 'jdbc',
    'jdbc-postgres' : 'jdbc',
    'mongodb'       :  None,
    'redis'         :  None,
    'cassandra-10'  :  None,
}

# The default table name to use if not specified in runner config file
DEFAULT_TABLENAME = "usertable"

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
    'jdbc-mysql': [
        "mysql",
        "-u",
        "ycsb",
        "-pycsb",
        "-e",
        "TRUNCATE TABLE {TABLENAME};",
        "ycsb"
    ],
    'jdbc-postgres': [
        "psql",
        "--host",
        "localhost",
        "-d",
        "ycsb",
        "-U",
        "ycsb",
        "-c",
        "TRUNCATE TABLE {TABLENAME};"
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
        "{TABLENAME}",
        "-e",
        "TRUNCATE data;"
    ],
}

####################################################################

### CONFIGURATION: #################################################

# This defines the option keys available in each section of the Runner
# configuration file
# trials        =   Number of times to run workload for each MPL
# min_mpl       =   min YCSB threads
# max_mpl       =   max YCSB threads
# inc_mpl       =   YCSB thread increase increment
# output        =   output format
# workload      =   workload file path
# output_plots  =   whether to generate plots
# avgkey        =   key to use as index column in output data
# avgfields     =   fields to include in the averages data output (e.g. CSV cols)
# plotkey       =   key to plot values against in output plot
# plotfields    =   fields to include in the output plot
# exportfields  =   fields to include in the raw data output (e.g. CSV cols)
# clean_data    =   whether or not the DBMS data should be wiped prior to each YCSB run
OPTION_KEYS = {
    'trials'       : int,
    'min_mpl'      : int,
    'max_mpl'      : int,
    'inc_mpl'      : int,
    'output'       : lambda s: str(s).lower().strip(),
    'output_dir'   : str,
    'workload'     : str,
    'output_plots' : bool,
    'avgkey'       : str,
    'avgfields'    : helpers.csv2list,
    'plotkey'      : str,
    'plotfields'   : helpers.csv2list,
    'exportfields' : helpers.csv2list,
    'clean_data'   : bool,
}

# Specifies default values for options in the Runner configuration file
OPTION_DEFAULTS = {
    'trials'       : 1,
    'min_mpl'      : 1,
    'max_mpl'      : 25,
    'inc_mpl'      : 4,
    'output'       : 'csv',
    'output_dir'   : 'output',
    'output_plots' : 'true',
    'avgkey'       : 'mpl',
    'avgfields'    : 'anomaly_score, runtime',
    'plotkey'      : 'mpl',
    'plotfields'   : 'anomaly_score',
    'exportfields' : 'mpl,runtime,throughput,trial',
    'clean_data'   : 'true',
}
####################################################################

### STATS COLLECTION: ##############################################

# Regex precompilation for statistics extraction
# The first match group is extracted for each statistic
# The keys in this dict should match to keys in TRACKED_STATS
STAT_REGEXPS = {
    'totalcash'  : re.compile(r"TOTAL CASH], ([0-9]+)"),
    'countcash'  : re.compile(r"COUNTED CASH], ([0-9]+)"),
    'opcount'    : re.compile(r"ACTUAL OPERATIONS], ([0-9]+)"),
    'runtime'    : re.compile(r"OVERALL], RunTime.+?, ([0-9.]+)"),
    'throughput' : re.compile(r"OVERALL], Throughput.+?, ([0-9.]+)"),
}

# Mappings of tracked statistics to their Python types
# These Python types should be numerical, i.e. float, int, long
# Note: Only statistics listed here will be stored by the Statistics class
TRACKED_STATS = {
    'totalcash'  : float, # From YCSB output
    'countcash'  : float, # From YCSB output
    'opcount'    : float, # From YCSB output
    'runtime'    : float, # From YCSB output
    'throughput' : float, # From YCSB output
    'mpl'        : int  , # Multiprogramming level (# threads)
    'trial'      : int  , # Trial number
}

####################################################################

### OUTPUT LOGGING: ################################################

LOG_LINE_PREFIX = "<<YCSB Runner>>: %s"
####################################################################
