# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Orchestrate.py
# Description:  This file represents the main orchestrator for the FireUp project. 
#               Usage: 
#              - Import the package as classes.group.action.Class as Class. 
#              - Via constructor, initialize the dictionary entry as it applies to the excel spreadsheet
#              - Per each class, implemented in the corresponding abstract class, call the object and then call analyze_entity()

from classes.securitycompliance.Mfa import Mfa
from classes.securitycompliance.Admin import Admin
from classes.securitycompliance.AdminAbility import AdminAbility
from classes.securitycompliance.PolicyAdmins import PolicyAdmins
from common.utils.reporter.report import *
from common.utils import statics



def main_orchestrator(config,signer, report_directory):
    print_header("Fireup "+statics.__version__)
    print_report_sub_header()
    __call_1_1(config, signer, report_directory)
    __call_1_2(config, signer, report_directory)
    __call_1_3(config, signer, report_directory)
    __call_1_4(config, signer, report_directory)


def __call_1_1(config,signer, report_directory):       
    mfa = Mfa(statics.__rp_1_1['entry'], statics.__rp_1_1['area'], statics.__rp_1_1['sub_area'], statics.__rp_1_1['review_point'], True, [], config, signer)
    __mfa_dictionary = mfa.analyze_entity(statics.__rp_1_1['entry'])   
    generate_on_screen_report(__mfa_dictionary, report_directory, statics.__rp_1_1['entry'])


def __call_1_2(config, signer, report_directory):    
    admin = Admin(statics.__rp_1_2['entry'], statics.__rp_1_2['area'], statics.__rp_1_2['sub_area'], statics.__rp_1_2['review_point'], True, [], config, signer)
    __admin_dictionary = admin.analyze_entity(statics.__rp_1_2['entry'])
    generate_on_screen_report(__admin_dictionary, report_directory, statics.__rp_1_2['entry'])

def __call_1_3(config, signer, report_directory):    
    adminAbility = AdminAbility(statics.__rp_1_3['entry'], statics.__rp_1_3['area'], statics.__rp_1_3['sub_area'], statics.__rp_1_3['review_point'], True, [], config, signer)
    __adminAbility_dictionary = adminAbility.analyze_entity(statics.__rp_1_3['entry'])
    generate_on_screen_report(__adminAbility_dictionary, report_directory, statics.__rp_1_3['entry'])

def __call_1_4(config, signer, report_directory):    
    policyAdmin = PolicyAdmins(statics.__rp_1_4['entry'], statics.__rp_1_4['area'], statics.__rp_1_4['sub_area'], statics.__rp_1_4['review_point'], True, [], config, signer)
    __policyAdmin_dictionary = policyAdmin.analyze_entity(statics.__rp_1_4['entry'])
    generate_on_screen_report(__policyAdmin_dictionary, report_directory, statics.__rp_1_3['entry'])

