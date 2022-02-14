# Copyright (c) 2021 Oracle and/or its affiliates.
# !/usr/bin/env bash
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# fireup.sh 
#
# Purpose: Main module which starts the application

__is_cloud_shell(){
  #if whoami command result is different from opc then return true. Else return false
    if [ "$(whoami)" != "opc" ] && [ "$(whoami)" != "ubuntu" ] ; then
        return 0
    else
        return 1
    fi
}


__install_os_prereqs(){
    echo "====== INSTALING OS PRE-REQUISITES ======"
    bash common/bash/prereqs.sh
}




__create_venv(){
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
}

__call_fireup(){
    python3 fireup.py 2>&1 | tee ./reports/fireup_color.log 
    sed 's/\x1b\[[0-9;]*[mGKH]//g' ./reports/fireup_color.log > ./reports/fireup.log
    sed -i '$d' ./reports/fireup.log
    rm ./reports/fireup_color.log

    tar -cvf reports.tar.gz ./reports &>/dev/null
    rm -rf reports
}

__call_fireup_with_dt(){
    python3 fireup.py -dt 2>&1 | tee ./reports/fireup_color.log 
    sed 's/\x1b\[[0-9;]*[mGKH]//g' ./reports/fireup_color.log > ./reports/fireup.log
    sed -i '$d' ./reports/fireup.log
    rm ./reports/fireup_color.log

    tar -cvf reports.tar.gz ./reports &>/dev/null
    rm -rf reports &>/dev/null
    rm -rf ~/reports.tar.gz
    mv reports.tar.gz ~/
}

__start_fireup(){
    if ! __is_cloud_shell; then
    __call_fireup
    else
    __call_fireup_with_dt
    fi
}



__main__(){ 
    __install_os_prereqs
    __create_venv
    __start_fireup
}


__main__