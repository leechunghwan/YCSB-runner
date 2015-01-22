import re

# Supported output formats
SUPPORTED_OUTPUTS = ['csv']

# Supported database systems
SUPPORTED_DBS = [
    'jdbc',
    'mongodb',
    'redis',
    'cassandra-10',
]

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
    'mysql': [
        "mysql",
        "-u",
        "ycsb",
        "-pycsb",
        "-e",
        "TRUNCATE TABLE {TABLENAME};",
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

# Regex precompilation
REGEXPS = {
    'totalcash'    : re.compile(r"TOTAL CASH], ([0-9]+)"),
    'countcash'    : re.compile(r"COUNTED CASH], ([0-9]+)"),
    'opcount'      : re.compile(r"ACTUAL OPERATIONS], ([0-9]+)"),
    'runtime'      : re.compile(r"OVERALL], RunTime.+?, ([0-9.]+)"),
    'throughput'   : re.compile(r"OVERALL], Throughput.+?, ([0-9.]+)"),
}

