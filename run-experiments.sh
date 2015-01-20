#!/bin/bash
export PATH=$PATH:~/Repos/YCSB/bin
for filename in configs/*.ini; do
    ./ycsb_runner.py "$filename"
done
