# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# dependencies.sh
# Description: Installs all the dependencies required for the project on virtual environment
# Dependencies: none
#!/bin/bash

echo '============== Virtual Environment Creation =============='
python3 -m venv venv
source venv/bin/activate

echo '============== Upgrading pip3 =============='
pip3 install --upgrade pip

echo '============== Installing testing dependencies =============='
pip3 install pytest
pip3 install pytest-runner

echo '============== Installing app dependencies =============='
pip3 install wheel
pip3 install setuptools
pip3 install twine
pip3 install oci
pip3 install ipaddr
pip3 install termcolor
pip3 install requests
pip3 install beautifulsoup4
pip3 install pandas