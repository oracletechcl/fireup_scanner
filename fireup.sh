# Copyright (c) 2021 Oracle and/or its affiliates.
# !/usr/bin/env bash
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# fireup.sh 
#
# Purpose: Main module which starts the application

if [ ! -d "venv" ] 
then
    echo "venv not present. Creating" 
    sh common/utils/bash/dependencies.sh
    chmod -R 775 venv
fi

source "./venv/bin/activate"


python3 fireup.py 



