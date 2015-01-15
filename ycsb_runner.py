#!/usr/bin/env python3

import os
import re
import sys
import subprocess
import configparser
import csv

# Supported database systems
SUPPORTED_DBS = [
    'jdbc',
    'mongodb',
    'redis',
    'cassandra',
]

# Commands for truncating each DBMS
# NOTE: PostgreSQL requires the database user password to be specified in a
# .pgpass file in the user's home directory
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

# Gets the first match group, cast to a float(), by running the given regex on
# the given string, or returns 0 if no matches were found
def getReMatch(regex, string):
    res = regex.search(string)
    if res != None and len(res.groups()) > 0:
        return float(res.group(1))
    else:
        return float()

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
    # Number of times to run the workload for each MPL for the given adapter
    trials   = config.getint(db, "trials" )
    # Starting MPL (min number of YCSB threads)
    min_mpl  = config.getint(db, "min_mpl")
    # Ending MPL (maximum number of YCSB threads)
    max_mpl  = config.getint(db, "max_mpl")
    # Number by which MPL is increased for each successive trial
    inc_mpl  = config.getint(db, "inc_mpl")
    # Output format
    output   = config.get(db, "output").lower()
    # YCSB workload file to be used
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

    # Regex precompilation, and Variables to hold stats data
    regexps = {
        'totalcash'  : re.compile(r"TOTAL CASH], ([0-9]+)$"),
        'countcash'  : re.compile(r"COUNTED CASH], ([0-9]+)$"),
        'opcount'    : re.compile(r"ACTUAL OPERATIONS], ([0-9]+)$"),
        'runtime'    : re.compile(r"OVERALL], RunTime.+?, ([0-9.]+)$"),
        'throughput' : re.compile(r"OVERALL], Throughput.+?, ([0-9.]+)$"),
    }
    run_stats = []

    # Run YCSB job trials number of times, and collect average statistics
    for trial in range(trials):
        print("Starting trial %i" % trial)
        # Track the MPL
        mpl = min_mpl
        while mpl + inc_mpl <= max_mpl:
            # Clean the database
            print("Cleaning the database...")
            db = db.lower()
            clean(db)
            # Load the data
            print("Loading YCSB data...")
            subprocess.call(ycsb_load)
            print("Running with MPL %i" % mpl)
            # Build the YCSB run command
            ycsb_run = [
                "ycsb",
                "run",
                db,
                "-P",
                os.path.join(os.getcwd(), workload),
                "-s",
                "-threads",
                str(mpl),
            ]
            # Store strings from regex matches
            stats = {
                'totalcash': float(),
                'countcash': float(),
                'opcount': float(),
                'runtime': float(),
                'throughput': float(),
                'mpl': int(),
                'trial': int(),
            }
            # Execute YCSB workload
            proc = subprocess.Popen(ycsb_run, stdout=subprocess.PIPE)
            for line in proc.stdout:
                line = line.decode("utf_8")
                sys.stdout.write(line)
                # Extract statistics from output
                # Everybody stand back! I know regular expressions!
                for stat, regex in regexps.items():
                    m = getReMatch(regex, line)
                    if m > 0:
                        stats[stat] = m
            if stats['runtime'] > 0:
                stats['mpl'] = mpl
                stats['trial'] = trial
                run_stats.append(stats)
            mpl += inc_mpl # increment the MPL by the configured amount
        print("Done!")
        print("Writing output...")

        if output == "csv":
            with open('output.csv', 'w') as f:
                fieldnames = run_stats[0].keys()
                writer = csv.DictWriter(f, fieldnames)
                writer.writeheader()
                for stat in run_stats:
                    writer.writerow(stat)
