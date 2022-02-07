# Copyright (c) 2021 Oracle and/or its affiliates.
# !/usr/bin/env bash
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# fireup.sh 
#
# Purpose: Main module which starts the application

# if OS user is opc or ubuntu then return true. Else return false
__is_cloud_shell(){
  #if whoami command result is different from opc then return true. Else return false
    if [ "$(whoami)" != "opc" ] && [ "$(whoami)" != "ubuntu" ] ; then
        return 0
    else
        return 1
    fi
}


# Calling OS pre-requisites script
bash common/bash/prereqs.sh

if [ ! -d "venv" ] 
then
    echo "venv not present. Creating" 
    bash common/bash/dependencies.sh
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

if ! __is_cloud_shell; then
    python3 fireup.py 2>&1 | tee ./reports/fireup_color.log 
    sed 's/\x1b\[[0-9;]*[mGKH]//g' ./reports/fireup_color.log > ./reports/fireup.log
    sed -i '$d' ./reports/fireup.log
    rm ./reports/fireup_color.log

    tar -cvf reports.tar.gz ./reports &>/dev/null
    rm -rf reports
else
    python3 fireup.py -dt 2>&1 | tee ./reports/fireup_color.log 
    sed 's/\x1b\[[0-9;]*[mGKH]//g' ./reports/fireup_color.log > ./reports/fireup.log
    sed -i '$d' ./reports/fireup.log
    rm ./reports/fireup_color.log

    tar -cvf reports.tar.gz ./reports &>/dev/null
    rm -rf reports
fi