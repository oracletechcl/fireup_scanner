# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# prereqs.sh
# Description: Installs all the required OS pre-requisites to run FireUp Scanner
# Dependencies: none
#!/bin/bash

export KEY_FILE_REGEX_TODO="key_file=<path to your private keyfile> # TODO"
export CLI_CONFIG_FILE=~/.oci/config

__is_ubuntu_or_debian() {
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$ID" = "ubuntu" -o "$ID" = "debian" ]; then
      return 0
    else
      return 1
    fi
  else
    return 1
  fi
}

__is_redhat_or_centos() {
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$ID" = "rhel" -o "$ID" = "centos" ]; then
      return 0
    else
      return 1
    fi
  else
    return 1
  fi
}

__source_bashrc(){
    if [ -f ~/.bashrc ]; then
        source ~/.bashrc
    fi
}

__cli_documentation() {
    echo "Follow this documentation to finish the CLI configuration: https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#File_Entries"    
    echo ""
    echo "A correct configuration file at $CLI_CONFIG_FILE looks like this:"
    echo "[DEFAULT]"
    echo "region = us-ashburn-1"
    echo "tenancy = ocid1.tenancy.oc1..aaaaaaaaw7e6nkszrry6d5hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    echo "user = ocid1.user.oc1..aaaaaaaayblfepjieoxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    echo "fingerprint = 19:1d:7b:3a:17"
    echo "key_file = ~/.oci/oci_api_key.pem"  
    echo ""  
    echo "Please finish the configuration of file $CLI_CONFIG_FILE and run ./fireup.sh script again."
}

__install_python3(){
if ! [ -x "$(command -v python3)" ]; then
    echo '============== Python Installation Pre-Requisites =============='
    echo 'Error: Python3 is not installed.' >&2
    echo 'Installing Python3...'

    #Check if this is a redhat based system. if So install python3 from yum else check if this is a debian based system. if so install python3 from apt
    if __is_redhat_or_centos; then
        sudo yum install python3
    elif __is_ubuntu_or_debian; then
        sudo apt-get install python3
        sudo apt-get install python3-pip
    else
        echo 'Error: This is not a supported system.' >&2
        exit 1
    fi
fi
}

__is_oci_cli_installed(){
    __source_bashrc    
    if __is_ubuntu_or_debian; then
        if [ -d /home/ubuntu/oci_cli ]; then
            return 0
        else
            return 1
        fi
    elif __is_redhat_or_centos; then
        if [ -d /home/opc/oci_cli ]; then
            return 0
        else
            return 1
        fi
    else
        echo 'Error: This is not a supported system.' >&2
        exit 1
    fi    
}

__install_os_dependencies(){
    if ! __is_oci_cli_installed; then
        if __is_ubuntu_or_debian; then
            sudo apt-get -y install python3.8-venv
        fi
    fi
        __install_python3

}


__install_oci_cli(){
__source_bashrc
if ! __is_oci_cli_installed ; then    
  echo '============== CLI Pre-Requisites =============='
    if __is_redhat_or_centos ; then      
        echo 'Installing OCI CLI in RedHat or CentOS...'
        sudo runuser -l opc -c 'mkdir -p /home/opc/oci_cli'
        sudo runuser -l opc -c 'wget https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh'
        sudo runuser -l opc -c 'chmod +x install.sh'
        sudo runuser -l opc -c '/home/opc/install.sh --install-dir /home/opc/oci_cli/lib/oracle-cli --exec-dir /home/opc/oci_cli/bin --accept-all-defaults'
        sudo runuser -l opc -c 'cp -rl /home/opc/bin /home/opc/oci_cli'
        sudo runuser -l opc -c 'rm -r /home/opc/bin'
        sudo runuser -l opc -c 'mkdir -p /home/opc/.oci'
        sudo runuser -l opc -c 'touch /home/opc/.oci/config'
        sudo runuser -l opc -c 'oci setup repair-file-permissions --file /home/opc/.oci/config'
    elif __is_ubuntu_or_debian ; then
        echo 'Installing OCI CLI in Ubuntu or Debian...'
        sudo runuser -l ubuntu -c 'mkdir -p /home/ubuntu/oci_cli'
        sudo runuser -l ubuntu -c 'wget https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh'
        sudo runuser -l ubuntu -c 'chmod +x install.sh'
        sudo runuser -l ubuntu -c '/home/ubuntu/install.sh --install-dir /home/ubuntu/oci_cli/lib/oracle-cli --exec-dir /home/ubuntu/oci_cli/bin --accept-all-defaults'
        sudo runuser -l ubuntu -c 'cp -rl /home/ubuntu/bin /home/ubuntu/oci_cli'
        sudo runuser -l ubuntu -c 'rm -r /home/ubuntu/bin'
        sudo runuser -l ubuntu -c 'mkdir -p /home/ubuntu/.oci'
        sudo runuser -l ubuntu -c 'touch /home/ubuntu/.oci/config'
        sudo runuser -l ubuntu -c 'oci setup repair-file-permissions --file /home/ubuntu/.oci/config'
    fi
fi

if [ -s $CLI_CONFIG_FILE ]; then  # This checks if the oci config file is not emtpy
    if [[ $(grep "$KEY_FILE_REGEX_TODO" $CLI_CONFIG_FILE) ]] ; then
        echo "Checking key configuration on $CLI_CONFIG_FILE..."
        echo "*************ERROR**************"
        echo "Config file $CLI_CONFIG_FILE does not contain a valid key file path"
        echo "*************ERROR**************"
        __cli_documentation
    fi
else
    echo "Checking OCI CLI config file..."
    echo "*************ERROR**************"
    echo "Config file $CLI_CONFIG_FILE is empty"
    echo "*************ERROR**************"
    __cli_documentation
fi
}





__main__(){    
    __source_bashrc
    __install_os_dependencies
    __install_oci_cli
}


__main__