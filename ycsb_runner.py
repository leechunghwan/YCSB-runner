#!/usr/bin/env python3
import sys

from runner import Runner

# Print usage info and exit
def usage():
    print("Usage: %s configfile" % sys.argv[0])
    sys.exit(1)

# Validate command-line args passed to script
if len(sys.argv) < 2:
    usage()

# Read and parse the given config file, instantiate Runner, and run workloads
ini_path = sys.argv[1]

runner = Runner(ini_path)
runner.run()
