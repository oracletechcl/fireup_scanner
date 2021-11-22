# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Orchestrate.py
# Description:  This file represents the main orchestrator for the FireUp project. 
#               Usage: 
#              - Import the package as classes.group.action.Class as Class. 
#              - Via constructor, initialize the dictionary entry as it applies to the excel spreadsheet
#              - Per each class, implemented in the corresponding abstract class, call the object and then call analyze_entity()

from classes.securitycompliance.Mfa import Mfa


def main_orchestrator(config,signer):
    __call_mfa(config, signer)


def __call_mfa(config,signer):
    mfa = Mfa("1.1", "Security and Compliance", "Manage Identities and Authorization Policies", "Enforce the Use of Multi-Factor Authentication (MFA)", True, [], config, signer)
    mfa.analyze_entity()
