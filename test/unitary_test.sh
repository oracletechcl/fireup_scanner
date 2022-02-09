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

if [ ! -f "test_status.log" ]
then
    echo "Creating Logfile"
    touch test_status.log
else
    echo "Removing and Recreating Logfile" 
    rm test_status.log > /dev/null
    touch test_status.log
fi

tail -f test_status.log &
python3 logger.py
sed -i 's/\x1b\[[0-9;]*[mGKH]//g' ./test_status.log 