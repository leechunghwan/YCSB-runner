#!/usr/bin/env python3
import os
import sys

from runner import Runner

# Import hooks.py if it exists
if os.path.exists('hooks.py'):
    try:
        from hooks import HOOKS
    except ImportError:
        raise ImportError("You must define a HOOKS dictionary in hooks.py")
else:
    HOOKS = {}

# Print usage info and exit
def usage():
    print("Usage: %s configfile" % sys.argv[0])
    sys.exit(1)

# Validate command-line args passed to script
if len(sys.argv) < 2:
    usage()

# Read and parse the given config file, instantiate Runner, and run workloads
ini_path = sys.argv[1]

runner = Runner(ini_path, hooks=HOOKS)
runner.run()
