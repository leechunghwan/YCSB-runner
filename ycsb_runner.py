#!/usr/bin/env python3

import sys
import subprocess
import configparser

# Clean database commands
CLEAN_COMMANDS = {
    'mysql'     : "mysql -u ycsb -pycsb ycsb -e 'TRUNCATE TABLE usertable;'",
    'psql'      : "psql --host localhost -d ycsb -U ycsb -c 'TRUNCATE TABLE usertable;'",
    'mongodb'   : "mongo --host localhost --eval 'db.dropDatabase();' ycsb",
    'redis'     : "redis-cli -r 1 'FLUSHALL'",
    'cassandra' : "cqlsh -k usertable -e 'TRUNCATE data;'",
}

def usage():
    print("Usage: %s configfile" % sys.argv[0])

def clean(db):
    if db.lower() == "jdbc":
        subprocess.call(CLEAN_COMMANDS['mysql'])
        subprocess.call(CLEAN_COMMANDS['psql'])
    else:
        subprocess.call(CLEAN_COMMANDS[db.lower()])

if len(sys.argv) < 2:
    usage()

# Read and parse the given config file
config = configparser.ConfigParser()
config.read(sys.argv[1])

# For each DBMS in the config, clean the system then run the workload
for db, settings in config.iteritems():
    trials = settings.getint("trials", 3)
    min_mpl = settings.getint("min_mpl", 1)
    max_mpl = settings.getint("max_mpl", 16)
    inc_mpl = settings.getint("inc_mpl", 1)
    output = settings["output"].lower()

    # Only CSV output is supported for now
    if output != "csv":
        print("Output type %s not supported. Only CSV is supported." % output)
        sys.exit(1)

    # Clean the database
    clean(output)

    # Build the YCSB load command
    ycsb_load = "ycsb load %s "

    # Build YCSB run command
    ycsb_run = "ycsb run %s "
