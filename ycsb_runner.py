#!/usr/bin/env python3

import os
import re
import csv
import sys
import subprocess
import configparser

from datetime    import datetime
from itertools   import count
from collections import defaultdict
from collections import OrderedDict

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

# Regex precompilation
REGEXPS = {
    'totalcash'    : re.compile(r"TOTAL CASH], ([0-9]+)"),
    'countcash'    : re.compile(r"COUNTED CASH], ([0-9]+)"),
    'opcount'      : re.compile(r"ACTUAL OPERATIONS], ([0-9]+)"),
    'runtime'      : re.compile(r"OVERALL], RunTime.+?, ([0-9.]+)"),
    'throughput'   : re.compile(r"OVERALL], Throughput.+?, ([0-9.]+)"),
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
        return None

# Validate command-line args passed to script
if len(sys.argv) < 2:
    usage()

# Read and parse the given config file
config = configparser.ConfigParser()
config.read(sys.argv[1])

#############################################################################

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

    # To hold stats data dicts
    run_stats = []

#############################################################################

    # Run YCSB job trials number of times, and collect average statistics
    for trial in range(trials):
        print("Starting trial %i" % trial)
        # Track the MPL
        for mpl in count(start = min_mpl, step = inc_mpl):
            if mpl > max_mpl:
                break
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
                'totalcash'  : float(), # From YCSB output
                'countcash'  : float(), # From YCSB output
                'opcount'    : float(), # From YCSB output
                'runtime'    : float(), # From YCSB output
                'throughput' : float(), # From YCSB output
                'mpl'        : int()  , # Multiprogramming level (# threads)
                'trial'      : int()  , # Trial number
                'score'      : float(), # Simple anomaly score (SAS)
            }
            # Execute YCSB workload
            with subprocess.Popen(ycsb_run, stdout=subprocess.PIPE) as proc:
                stdout = proc.stdout.read().decode("utf_8")
                sys.stdout.write(stdout)
                # Extract statistics from output
                # /Everybody stand back/ I know regular expressions!
                #
                # NOTE in the case that validation succeeds, YCSB+T doesn't
                #   output these stats, so total cash, counted cash, and op
                #   count will all be zero
                for stat, regex in REGEXPS.items():
                    m = getReMatch(regex, stdout)
                    if m is not None:
                        stats[stat] = m

            if stats['runtime'] > 0:
                stats['mpl'] = mpl
                stats['trial'] = trial
                # If we have the right values, calculate the simple anomaly
                #   score here, otherwise leave as 0
                if (stats['opcount'] != 0 and stats['totalcash'] != 0 and
                      stats['countcash'] != 0):
                    stats['score'] = abs(stats['totalcash'] -
                      stats['countcash']) / stats['opcount']
                run_stats.append(stats)

        print("Completed trial number %s" % (trial))

#############################################################################

    print("Writing output...")

    # CSV output
    if output == "csv":
        # Make output dir if not exists
        CSV_OUT_DIR = "csv"
        if not os.path.exists(CSV_OUT_DIR):
            os.makedirs(CSV_OUT_DIR)

        # Write all collected stats
        # Date and time to be included in output filename
        datestr = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        filename = "output-{}-{}.csv".format(db, datestr)
        filepath = os.path.join(".", CSV_OUT_DIR, filename)
        with open(filepath, 'w') as f:
            # If this doesn't hold then something is very wrong (i.e. YCSB
            # isn't running properly, or there's some major bug in this runner
            # script)
            assert len(run_stats) > 1
            fieldnames = sorted(run_stats[0].keys())
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            for stat in run_stats:
                writer.writerow(stat)

        # Calculate and write average simple anomaly scores for each MPL
        filename = "averages-{}-{}.csv".format(db, datestr)
        filepath = os.path.join(".", CSV_OUT_DIR, filename)
        with open(filepath, 'w') as f:
            fieldnames = ['db', 'mpl', 'avg_score', 'num_trials']
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            scores = defaultdict(float)
            # Map MPL to sum of simple anomaly scores
            for stat in run_stats:
                scores[stat['mpl']] += stat['score']
            # Finally, write CSV rows, sorted by MPL
            for mpl, total in sorted(scores.items()):
                writer.writerow({
                    'db'        : db,
                    'mpl'       : mpl,
                    'avg_score' : total / trials, # average for this MPL
                    'num_trials': trials,
                })
