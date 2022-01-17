# Copyright (c) 2021 Oracle and/or its affiliates.
# !/usr/bin/env bash
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# fireup.sh 
#
# Purpose: Main test suite executor

export PYTEST_ADDOPTS="--color=yes"

if [ ! -d "venv" ] 
then
    echo "venv not present. Creating" 
    sh ../common/bash/dependencies.sh
    chmod -R 775 venv
fi

source "venv/bin/activate"
echo "Unit Test Started at: $(date)"
python3 -m pytest --durations=0 -v 2>&1 | tee output.out

# Removes all colour codes from written file
sed -i "s,\x1B\[[0-9;]*[a-zA-Z],,g" output.out
