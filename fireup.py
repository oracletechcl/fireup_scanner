# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# fireup.py
# Description: Main python wrapper of fireup review tool
# Dependencies: 


import argparse
from common.utils.formatter.printer import *
from common.utils.tokenizer.signer import *
from classes.orchestrator.Orchestrate import main_orchestrator

def __exec_orchestrator():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', default="", dest='config_profile',
                        help='Config file section to use (tenancy profile)')
    parser.add_argument('--output-to-bucket', default="", dest='output_bucket',
                        help='Set Output bucket name (i.e. my-reporting-bucket) ')
    parser.add_argument('--report-directory', default=None, dest='report_directory',
                        help='Set Output report directory by default it is the current date (i.e. reports-date) ')
    parser.add_argument('--print-to-screen', default='True', dest='print_to_screen',
                        help='Set to False if you want to see only non-compliant findings (i.e. False) ')
    parser.add_argument('-ip', action='store_true', default=False,
                        dest='is_instance_principals', help='Use Instance Principals for Authentication')
    parser.add_argument('-dt', action='store_true', default=False,
                        dest='is_delegation_token', help='Use Delegation Token for Authentication')
    cmd = parser.parse_args() 


    config, signer = create_signer(cmd.config_profile, cmd.is_instance_principals, cmd.is_delegation_token)

    main_orchestrator(config, signer)



def __main__():
    __exec_orchestrator()   


__main__()