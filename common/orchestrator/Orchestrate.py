# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Orchestrate.py
# Description:  This file represents the main orchestrator for the FireUp project. 
#               Usage: 
#              - Import the package as classes.group.action.Class as Class. 
#              - Via constructor, initialize the dictionary entry as it applies to the excel spreadsheet
#              - Per each class, implemented in the corresponding abstract class, call the object and then call analyze_entity()

from classes.securitycompliance.ApiKeys import ApiKeys
from classes.securitycompliance.Mfa import Mfa
from classes.securitycompliance.Admin import Admin
from classes.securitycompliance.AdminAbility import AdminAbility
from classes.securitycompliance.PolicyAdmins import PolicyAdmins
from classes.securitycompliance.FederatedUsers import FederatedUsers

from classes.reliabilityresilience.SeparateCIDRBlocks import SeparateCIDRBlocks
from classes.reliabilityresilience.CIDRSize import CIDRSize
from common.utils.reporter.report import *
from common.utils.statics import Statics



def main_orchestrator(config,signer, report_directory):
    print_header("Fireup "+Statics.__version__)
    print_report_sub_header()
    __call_1_1(config, signer, report_directory)
    __call_1_2(config, signer, report_directory)
    __call_1_3(config, signer, report_directory)
    __call_1_4(config, signer, report_directory)
    __call_1_5(config, signer, report_directory)
    __call_1_6(config, signer, report_directory)

    __call_2_8(config, signer, report_directory)
    __call_2_9(config, signer, report_directory)



def __call_1_1(config, signer, report_directory):       
    mfa = Mfa(
    Statics.__rp_1_1['entry'], 
    Statics.__rp_1_1['area'], 
    Statics.__rp_1_1['sub_area'], 
    Statics.__rp_1_1['review_point'],     
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_1['entry']+"_"+Statics.__rp_1_1['area']+"_"+Statics.__rp_1_1['sub_area']+"_mitigations"
    __mfa_dictionary = mfa.analyze_entity(Statics.__rp_1_1['entry'])       
    generate_on_screen_report(__mfa_dictionary, report_directory, Statics.__rp_1_1['entry'])    
    generate_mitigation_report(__mfa_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_1['fireup_items'])


def __call_1_2(config, signer, report_directory):    
    admin = Admin(
    Statics.__rp_1_2['entry'], 
    Statics.__rp_1_2['area'], 
    Statics.__rp_1_2['sub_area'], 
    Statics.__rp_1_2['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_2['entry']+"_"+Statics.__rp_1_2['area']+"_"+Statics.__rp_1_2['sub_area']+"_mitigations"
    __admin_dictionary = admin.analyze_entity(Statics.__rp_1_2['entry'])
    generate_on_screen_report(__admin_dictionary, report_directory, Statics.__rp_1_2['entry'])
    generate_mitigation_report(__admin_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_2['fireup_items'])

def __call_1_3(config, signer, report_directory):    
    adminAbility = AdminAbility(
    Statics.__rp_1_3['entry'], 
    Statics.__rp_1_3['area'], 
    Statics.__rp_1_3['sub_area'], 
    Statics.__rp_1_3['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_3['entry']+"_"+Statics.__rp_1_3['area']+"_"+Statics.__rp_1_3['sub_area']+"_mitigations"
    __adminAbility_dictionary = adminAbility.analyze_entity(Statics.__rp_1_3['entry'])
    generate_on_screen_report(__adminAbility_dictionary, report_directory, Statics.__rp_1_3['entry'])
    generate_mitigation_report(__adminAbility_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_3['fireup_items'])

def __call_1_4(config, signer, report_directory):    
    policyAdmin = PolicyAdmins(
    Statics.__rp_1_4['entry'], 
    Statics.__rp_1_4['area'], 
    Statics.__rp_1_4['sub_area'], 
    Statics.__rp_1_4['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_4['entry']+"_"+Statics.__rp_1_4['area']+"_"+Statics.__rp_1_4['sub_area']+"_mitigations"
    __policyAdmin_dictionary = policyAdmin.analyze_entity(Statics.__rp_1_4['entry'])
    generate_on_screen_report(__policyAdmin_dictionary, report_directory, Statics.__rp_1_4['entry'])
    generate_mitigation_report(__policyAdmin_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_4['fireup_items'])

def __call_1_5(config, signer, report_directory):    
    federatedUsers = FederatedUsers(
    Statics.__rp_1_5['entry'], 
    Statics.__rp_1_5['area'], 
    Statics.__rp_1_5['sub_area'], 
    Statics.__rp_1_5['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_5['entry']+"_"+Statics.__rp_1_5['area']+"_"+Statics.__rp_1_5['sub_area']+"_mitigations"
    __federatedUsers_dictionary = federatedUsers.analyze_entity(Statics.__rp_1_5['entry'])
    generate_on_screen_report(__federatedUsers_dictionary, report_directory, Statics.__rp_1_5['entry'])
    generate_mitigation_report(__federatedUsers_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_5['fireup_items'])

def __call_1_6(config, signer, report_directory):
    apiKeys = ApiKeys(
    Statics.__rp_1_6['entry'], 
    Statics.__rp_1_6['area'], 
    Statics.__rp_1_6['sub_area'], 
    Statics.__rp_1_6['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_6['entry']+"_"+Statics.__rp_1_6['area']+"_"+Statics.__rp_1_6['sub_area']+"_mitigations"
    __apiKeys_dictionary = apiKeys.analyze_entity(Statics.__rp_1_6['entry'])
    generate_on_screen_report(__apiKeys_dictionary, report_directory, Statics.__rp_1_6['entry'])
    generate_mitigation_report(__apiKeys_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_6['fireup_items'])

def __call_2_8(config, signer, report_directory):    
    separateCIDRBlocks = SeparateCIDRBlocks(
    Statics.__rp_2_8['entry'],
    Statics.__rp_2_8['area'],
    Statics.__rp_2_8['sub_area'],
    Statics.__rp_2_8['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_8['entry']+"_"+Statics.__rp_2_8['area']+"_"+Statics.__rp_2_8['sub_area']+"_mitigations"
    __separateCIDRBlocks_dictionary = separateCIDRBlocks.analyze_entity(Statics.__rp_2_8['entry'])
    generate_on_screen_report(__separateCIDRBlocks_dictionary, report_directory, Statics.__rp_2_8['entry'])
    generate_mitigation_report(__separateCIDRBlocks_dictionary, report_directory, mitigation_report_name, Statics.__rp_2_8['fireup_items'])


def __call_2_9(config, signer, report_directory):    
    cidrSize = CIDRSize(
    Statics.__rp_2_9['entry'],
    Statics.__rp_2_9['area'],
    Statics.__rp_2_9['sub_area'],
    Statics.__rp_2_9['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_9['entry']+"_"+Statics.__rp_2_9['area']+"_"+Statics.__rp_2_9['sub_area']+"_mitigations"
    __cidrSize_dictionary = cidrSize.analyze_entity(Statics.__rp_2_9['entry'])
    generate_on_screen_report(__cidrSize_dictionary, report_directory, Statics.__rp_2_9['entry'])
    generate_mitigation_report(__cidrSize_dictionary, report_directory, mitigation_report_name, Statics.__rp_2_9['fireup_items'])
