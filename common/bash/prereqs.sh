# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# prereqs.sh
# Description: Installs all the required OS pre-requisites to run FireUp Scanner
# Dependencies: none
#!/bin/bash

export KEY_FILE_REGEX_TODO="key_file=<path to your private keyfile> # TODO"
export CLI_CONFIG_FILE="/home/opc/.oci/config"

cli_documentation() {
    echo "Follow this documentation to finish the CLI configuration: https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#File_Entries"    
    echo ""
    echo "A correct configuration file at $CLI_CONFIG_FILE looks like this:"
    echo "[DEFAULT]"
    echo "region = us-ashburn-1"
    echo "tenancy = ocid1.tenancy.oc1..aaaaaaaaw7e6nkszrry6d5hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    echo "user = ocid1.user.oc1..aaaaaaaayblfepjieoxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    echo "fingerprint = 19:1d:7b:3a:17"
    echo "key_file = /home/opc/.oci/oci_api_key.pem"  
    echo ""  
    echo "Please finish the configuration of file $CLI_CONFIG_FILE and run ./fireup.sh script again."
}

source "/home/opc/.bashrc"

if ! [ -x "$(command -v python3)" ]; then
  echo '============== Python Installation Pre-Requisites =============='
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

if ! oci &>/dev/null ; then    
    echo '============== CLI Pre-Requisites =============='
    echo 'Installing OCI CLI...'

    sudo runuser -l opc -c 'mkdir -p /home/opc/oci_cli'
    sudo runuser -l opc -c 'wget https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh'
    sudo runuser -l opc -c 'chmod +x install.sh'
    sudo runuser -l opc -c '/home/opc/install.sh --install-dir /home/opc/oci_cli/lib/oracle-cli --exec-dir /home/opc/oci_cli/bin --accept-all-defaults'
    sudo runuser -l opc -c 'cp -rl /home/opc/bin /home/opc/oci_cli'
    sudo runuser -l opc -c 'rm -r /home/opc/bin'
    sudo runuser -l opc -c 'mkdir -p /home/opc/.oci'
    sudo runuser -l opc -c 'touch /home/opc/.oci/config'
    sudo runuser -l opc -c 'oci setup repair-file-permissions --file /home/opc/.oci/config'
fi
    source "/home/opc/.bashrc"
    [ -s /home/opc/.oci/config ]
    if [ $? -eq 0 ]; then  # This checks if the oci config file is emtpy
        if [[ $(grep "$KEY_FILE_REGEX_TODO" $CLI_CONFIG_FILE) ]] ; then
             echo "Checking key configuration on $CLI_CONFIG_FILE..."
             echo "Config file $CLI_CONFIG_FILE does not contain a valid key file path"     
             cli_documentation        
        fi
    else
            echo "Checking OCI CLI config file..."
            echo "Config file $CLI_CONFIG_FILE is empty"
            cli_documentation
    fi
