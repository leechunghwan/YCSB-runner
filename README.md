# YCSB Runner

YCSB Runner is a Python application for automatically running the Yahoo! Cloud
System Benchmark (YCSB) tool.

### Project Status

This project is currently under active development and is not stable nor ready
for general use.

## YCSB Version Support

This tool is currently designed to work with a [specific
variant](https://github.com/benjaminbrent/YCSB/tree/mi-mo-anomalies-project) of
YCSB+T, but eventually YCSB+T should be
[merged](https://github.com/brianfrankcooper/YCSB/pull/169) into the core YCSB
project.

## Features

 - Statistics collection from YCSB tool output
 - CSV output
 - Data plotting
 - Configure YCSB run options, including varying the thread count (MPL)
 - Run a configurable number of trials with each set of YCSB run options
