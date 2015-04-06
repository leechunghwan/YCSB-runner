#!/usr/bin/env python3
# Simple utility for plotting CSV outputs from YCSB-runner
import os
import sys

import matplotlib
matplotlib.use('Agg')
matplotlib.rc('font', family='sans-serif')

from pandas     import read_csv, concat
from matplotlib import pyplot as plt

# TODO: Make these configurable using command-line args
PLOT_FIELDS = ["anomaly_score"]
INDEX_FIELD = "mpl"
GROUP_FIELD = "trial"
PLOT_STYLE  = "o-"

def plot(fname):
    g = read_csv(fname).groupby(GROUP_FIELD)
    dfs = [g.get_group(x) for x in g.groups]
    for i, f in enumerate(dfs):
        # Drop fields which we don't want to plot (i.e. anything other than
        # PLOT_FIELDS)
        dfs[i] = f.set_index(INDEX_FIELD).drop([k for k,v in f.iteritems() if
            k not in PLOT_FIELDS and k != INDEX_FIELD], axis=1)
    concat(dfs, axis=1).mean(axis=1).plot(style=PLOT_STYLE)

# Print usage info and exit
def usage():
    print("Usage: %s FILE [FILE]..." % sys.argv[0])
    sys.exit(1)

# Validate command-line args passed to script
if len(sys.argv) < 2:
    usage()

# Read each file and produce a pretty graph...
for fname in sys.argv[1:]:
    plot(fname)

plt.savefig('/tmp/tmp.pdf')
