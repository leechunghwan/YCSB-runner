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
 - Simple extensibility

# License

Copyright 2015 Benjamin Brent

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
