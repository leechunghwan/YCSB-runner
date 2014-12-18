#!/usr/bin/env python3

import os
import sys
import subprocess
import configparser

# Supported database systems
SUPPORTED_DBS = [
    'jdbc',
    'mongodb',
    'redis',
    'cassandra',
]

# Clean database commands
CLEAN_COMMANDS = {
    'mysql'     : ["mysql", "-u", "ycsb", "-pycsb", "-e", "TRUNCATE TABLE usertable;", "ycsb"],
    'psql'      : ["psql", "--host", "localhost", "-d", "ycsb", "-U", "ycsb", "-c", "TRUNCATE TABLE usertable;"],
    'mongodb'   : ["mongo", "--host", "localhost", "--eval", "db.dropDatabase();", "ycsb"],
    'redis'     : ["redis-cli", "-r", "1", "FLUSHALL"],
    'cassandra' : ["cqlsh", "-k", "usertable", "-e", "TRUNCATE data;"],
}

def usage():
    print("Usage: %s configfile" % sys.argv[0])
    sys.exit(1)

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
for db in config.sections():
    # Validate names
    if db.lower() not in SUPPORTED_DBS:
        print("Invalid database found: %s. Skipping..." % db)
        continue

    # Load config values
    trials   = config.getint(db, "trials" )
    min_mpl  = config.getint(db, "min_mpl")
    max_mpl  = config.getint(db, "max_mpl")
    inc_mpl  = config.getint(db, "inc_mpl")
    output   = config.get(db, "output").lower()
    workload = config.get(db, "workload")

    # Only CSV output is supported for now
    if output != "csv":
        print("Output type %s not supported. Only CSV is supported." % output)
        sys.exit(1)

    # Build the YCSB load command
    ycsb_load = [
        "ycsb",
        "load",
        db,
        "-P",
        os.path.join(os.getcwd(), workload),
        "-s",
        "-threads",
        "1",
    ]

    # Variables to hold stats data
    # TODO

    # Run YCSB job trials number of times, and collect average statistics
    for i in range(trials):
        # Clean the database
        db = db.lower()
        clean(db)
        # Load the data
        subprocess.call(ycsb_load)
        # Track the MPL
        i = min_mpl
        while i <= max_mpl:
            # Build the YCSB run command
            ycsb_run = [
                "ycsb",
                "run",
                db,
                "-P",
                os.path.join(os.getcwd(), workload),
                "-s",
                "-threads",
                str(i),
            ]
            i += inc_mpl
            # Execute YCSB workload
            proc = subprocess.Popen(ycsb_run, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            # Extract statistics from output
            # Everybody stand back! I know regular expressions!

