# Copyright (c) 2021 Oracle and/or its affiliates.
# !/usr/bin/env bash
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# fireup.sh 
#
# Purpose: Main module which starts the application


# Calling OS pre-requisites script
sh common/bash/prereqs.sh

if [ ! -d "venv" ] 
then
    echo "venv not present. Creating" 
    sh common/bash/dependencies.sh
    chmod -R 775 venv
fi

source "./venv/bin/activate"

if [ ! -d "reports" ] 
then
    mkdir reports
else
    rm -rf reports &>/dev/null
    mkdir reports
fi

# save the output to a file but also show in console

python3 fireup.py 2>&1 | tee ./reports/fireup_color.log 
sed 's/\x1b\[[0-9;]*[mGKH]//g' ./reports/fireup_color.log > ./reports/fireup.log
sed -i '$d' ./reports/fireup.log
rm ./reports/fireup_color.log

tar -cvf reports.tar.gz ./reports &>/dev/null
rm -rf reports