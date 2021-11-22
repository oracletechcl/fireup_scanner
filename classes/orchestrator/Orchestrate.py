# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Orchestrate.py
# Description:  This file represents the main orchestrator for the FireUp project. 
#               Usage: 
#              - Import the package as classes.group.action.Class as Class. 
#              - Via constructor, initialize the dictionary entry as it applies to the excel spreadsheet
#              - Per each class, implemented in the corresponding abstract class, call the object and then call analyze_entity()

from classes.securitycompliance.Mfa import Mfa
from common.utils.reporter.Report import *

__mfa_dictionary = []




def main_orchestrator(config,signer, report_directory):
    print_header("Fireup v0.0.1")
    print_report_sub_header()
    __call_mfa(config, signer, report_directory)


def __call_mfa(config,signer, report_directory):
    entry = "1.1"
    mfa = Mfa(entry, "Security and Compliance", "Manage Identities and Authorization Policies", "Enforce the Use of Multi-Factor Authentication (MFA)", True, [], config, signer)
    __mfa_dictionary = mfa.analyze_entity(entry)   
    generate_on_screen_report(__mfa_dictionary, report_directory, "mfa_report")



