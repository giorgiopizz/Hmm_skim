#!/bin/bash

source /cvmfs/sft.cern.ch/lcg/views/LCG_108/x86_64-el9-gcc15-opt/setup.sh
export X509_USER_PROXY=my_cert

python3 runner.py

if [ ! -f output.json ]; then
    touch output.json
fi
