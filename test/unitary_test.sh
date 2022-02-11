# Copyright (c) 2021 Oracle and/or its affiliates.
# !/usr/bin/env bash
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# fireup.sh 
#
# Purpose: Main test suite executor

trap "kill 0" EXIT

if [ ! -d "venv" ] 
then
    echo "venv not present. Creating" 
    bash ../common/bash/dependencies.sh
    chmod -R 775 venv
fi

source "venv/bin/activate"
echo "Unit Test Started at: $(date)"

if [ ! -f "unitary_testing.out" ]
then
    echo "Creating Logfile"
    touch unitary_testing.out
else
    echo "Removing and Recreating Logfile" 
    rm unitary_testing.out > /dev/null
    touch unitary_testing.out
fi

tail -f unitary_testing.out &
python3 logger.py
sed -i 's/\x1b\[[0-9;]*[mGKH]//g' ./unitary_testing.out