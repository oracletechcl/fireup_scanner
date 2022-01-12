# Copyright (c) 2021 Oracle and/or its affiliates.
# !/usr/bin/env bash
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# fireup.sh 
#
# Purpose: Main module which starts the application

# Check if Python3 is installed. If not, install it
if ! [ -x "$(command -v python3)" ]; then
  echo 'Error: Python3 is not installed.' >&2
  echo 'Installing Python3...'
  
  #Check if this is a redhat based system. if So install python3 from yum else check if this is a debian based system. if so install python3 from apt
    if [ -f /etc/redhat-release ]; then
        sudo yum install python3
    elif [ -f /etc/debian_version ]; then
        sudo apt-get install python3
    else
        echo 'Error: This is not a supported system.' >&2
        exit 1
    fi  
fi

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
fi
# save the output to a file but also show in console

python3 fireup.py 2>&1 | tee ./reports/fireup.log 

tar -cvf reports.tar.gz ./reports &>/dev/null
rm -rf reports