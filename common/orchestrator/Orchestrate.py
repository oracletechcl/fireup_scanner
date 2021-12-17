# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Orchestrate.py
# Description:  This file represents the main orchestrator for the FireUp project. 
#               Usage: 
#              - Import the package as classes.group.action.Class as Class. 
#              - Via constructor, initialize the dictionary entry as it applies to the excel spreadsheet
#              - Per each class, implemented in the corresponding abstract class, call the object and then call analyze_entity()

from classes.securitycompliance.InstancePrincipal import InstancePrincipal
from classes.securitycompliance.SecurityList import SecurityList
from classes.securitycompliance.ApiKeys import ApiKeys
from classes.securitycompliance.CompartmentsAndPolicies import CompartmentsAndPolicies
from classes.securitycompliance.Mfa import Mfa
from classes.securitycompliance.Admin import Admin
from classes.securitycompliance.AdminAbility import AdminAbility
from classes.securitycompliance.PolicyAdmins import PolicyAdmins
from classes.securitycompliance.FederatedUsers import FederatedUsers
from classes.securitycompliance.DBSystemControl import DBSystemControl
from classes.securitycompliance.DBPermissions import DBPermissions
from classes.securitycompliance.MaxSecurityZone import MaxSecurityZone
from classes.securitycompliance.Rbac import Rbac
from classes.reliabilityresilience.SeparateCIDRBlocks import SeparateCIDRBlocks
from classes.reliabilityresilience.CIDRSize import CIDRSize

from classes.reliabilityresilience.CompartmentQuotas import CompartmentQuotas
from classes.reliabilityresilience.LBaaSBackends import LBaaSBackends
from classes.reliabilityresilience.LBaaSHealthChecks import LBaaSHealthChecks
from classes.reliabilityresilience.CheckBackupPolicies import CheckBackupPolicies
from classes.reliabilityresilience.BackupDatabases import BackupDatabases
from classes.reliabilityresilience.ReplicateData import ReplicateData

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
    __call_1_7(config, signer, report_directory)
    __call_1_8(config, signer, report_directory)
    __call_1_9(config, signer, report_directory)
    __call_1_10(config, signer, report_directory)
    __call_1_11(config, signer, report_directory)
    __call_1_12(config, signer, report_directory)
    __call_1_13(config, signer, report_directory)
    
    __call_2_5(config, signer, report_directory)
    __call_2_8(config, signer, report_directory)
    __call_2_9(config, signer, report_directory)
    __call_2_10(config, signer, report_directory)
    __call_2_13(config, signer, report_directory)
    __call_2_14(config, signer, report_directory)
    __call_2_15(config, signer, report_directory)
    __call_2_17(config, signer, report_directory)


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


def __call_1_7(config, signer, report_directory):
    compPolicies = CompartmentsAndPolicies(
    Statics.__rp_1_7['entry'], 
    Statics.__rp_1_7['area'], 
    Statics.__rp_1_7['sub_area'], 
    Statics.__rp_1_7['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_7['entry']+"_"+Statics.__rp_1_7['area']+"_"+Statics.__rp_1_7['sub_area']+"_mitigations"
    __compPolicies_dictionary = compPolicies.analyze_entity(Statics.__rp_1_7['entry'])
    generate_on_screen_report(__compPolicies_dictionary, report_directory, Statics.__rp_1_7['entry'])
    generate_mitigation_report(__compPolicies_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_7['fireup_items'])


def __call_1_8(config, signer, report_directory):
    Rbacobject = Rbac(
    Statics.__rp_1_8['entry'], 
    Statics.__rp_1_8['area'], 
    Statics.__rp_1_8['sub_area'], 
    Statics.__rp_1_8['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_8['entry']+"_"+Statics.__rp_1_8['area']+"_"+Statics.__rp_1_8['sub_area']+"_mitigations"
    __Rbacobject_dictionary = Rbacobject.analyze_entity(Statics.__rp_1_8['entry'])
    generate_on_screen_report(__Rbacobject_dictionary, report_directory, Statics.__rp_1_8['entry'])
    generate_mitigation_report(__Rbacobject_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_8['fireup_items'])

def __call_1_9(config, signer, report_directory):
    instancePrincipal = InstancePrincipal(
    Statics.__rp_1_9['entry'], 
    Statics.__rp_1_9['area'], 
    Statics.__rp_1_9['sub_area'], 
    Statics.__rp_1_9['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_9['entry']+"_"+Statics.__rp_1_9['area']+"_"+Statics.__rp_1_9['sub_area']+"_mitigations"
    __instancePrincipal_dictionary = instancePrincipal.analyze_entity(Statics.__rp_1_9['entry'])
    generate_on_screen_report(__instancePrincipal_dictionary, report_directory, Statics.__rp_1_9['entry'])
    generate_mitigation_report(__instancePrincipal_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_9['fireup_items'])

def __call_1_10(config, signer, report_directory):
    secList = SecurityList(
    Statics.__rp_1_10['entry'], 
    Statics.__rp_1_10['area'], 
    Statics.__rp_1_10['sub_area'], 
    Statics.__rp_1_10['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_10['entry']+"_"+Statics.__rp_1_10['area']+"_"+Statics.__rp_1_10['sub_area']+"_mitigations"
    __instancePrincipal_dictionary = secList.analyze_entity(Statics.__rp_1_10['entry'])
    generate_on_screen_report(__instancePrincipal_dictionary, report_directory, Statics.__rp_1_10['entry'])
    generate_mitigation_report(__instancePrincipal_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_10['fireup_items'])

def __call_1_11(config, signer, report_directory):
    secZone = MaxSecurityZone(
    Statics.__rp_1_11['entry'], 
    Statics.__rp_1_11['area'], 
    Statics.__rp_1_11['sub_area'], 
    Statics.__rp_1_11['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_11['entry']+"_"+Statics.__rp_1_11['area']+"_"+Statics.__rp_1_11['sub_area']+"_mitigations"
    __instancePrincipal_dictionary = secZone.analyze_entity(Statics.__rp_1_11['entry'])
    generate_on_screen_report(__instancePrincipal_dictionary, report_directory, Statics.__rp_1_11['entry'])
    generate_mitigation_report(__instancePrincipal_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_11['fireup_items'])

def __call_1_13(config, signer, report_directory):
    dbPerms = DBPermissions(
    Statics.__rp_1_13['entry'], 
    Statics.__rp_1_13['area'], 
    Statics.__rp_1_13['sub_area'], 
    Statics.__rp_1_13['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_13['entry']+"_"+Statics.__rp_1_13['area']+"_"+Statics.__rp_1_13['sub_area']+"_mitigations"
    __instancePrincipal_dictionary = dbPerms.analyze_entity(Statics.__rp_1_13['entry'])
    generate_on_screen_report(__instancePrincipal_dictionary, report_directory, Statics.__rp_1_13['entry'])
    generate_mitigation_report(__instancePrincipal_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_13['fireup_items'])


def __call_1_12(config, signer, report_directory):
    dbSystem = DBSystemControl(
    Statics.__rp_1_12['entry'], 
    Statics.__rp_1_12['area'], 
    Statics.__rp_1_12['sub_area'], 
    Statics.__rp_1_12['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_12['entry']+"_"+Statics.__rp_1_12['area']+"_"+Statics.__rp_1_12['sub_area']+"_mitigations"
    __instancePrincipal_dictionary = dbSystem.analyze_entity(Statics.__rp_1_12['entry'])
    generate_on_screen_report(__instancePrincipal_dictionary, report_directory, Statics.__rp_1_12['entry'])
    generate_mitigation_report(__instancePrincipal_dictionary, report_directory, mitigation_report_name, Statics.__rp_1_12['fireup_items'])


def __call_2_5(config, signer, report_directory):    
    compQuotas = CompartmentQuotas(
    Statics.__rp_2_5['entry'],
    Statics.__rp_2_5['area'],
    Statics.__rp_2_5['sub_area'],
    Statics.__rp_2_5['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_5['entry']+"_"+Statics.__rp_2_5['area']+"_"+Statics.__rp_2_5['sub_area']+"_mitigations"
    __compQuotas_dictionary = compQuotas.analyze_entity(Statics.__rp_2_5['entry'])
    generate_on_screen_report(__compQuotas_dictionary, report_directory, Statics.__rp_2_5['entry'])
    generate_mitigation_report(__compQuotas_dictionary, report_directory, mitigation_report_name, Statics.__rp_2_5['fireup_items'])


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


def __call_2_10(config, signer, report_directory):    
    lbaasBackends = LBaaSBackends(
    Statics.__rp_2_10['entry'],
    Statics.__rp_2_10['area'],
    Statics.__rp_2_10['sub_area'],
    Statics.__rp_2_10['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_10['entry']+"_"+Statics.__rp_2_10['area']+"_"+Statics.__rp_2_10['sub_area']+"_mitigations"
    __lbaasBackends_dictionary = lbaasBackends.analyze_entity(Statics.__rp_2_10['entry'])
    generate_on_screen_report(__lbaasBackends_dictionary, report_directory, Statics.__rp_2_10['entry'])
    generate_mitigation_report(__lbaasBackends_dictionary, report_directory, mitigation_report_name, Statics.__rp_2_10['fireup_items'])


def __call_2_13(config, signer, report_directory):    
    lbaasHealthChecks = LBaaSHealthChecks(
    Statics.__rp_2_13['entry'],
    Statics.__rp_2_13['area'],
    Statics.__rp_2_13['sub_area'],
    Statics.__rp_2_13['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_13['entry']+"_"+Statics.__rp_2_13['area']+"_"+Statics.__rp_2_13['sub_area']+"_mitigations"
    __lbaasHealthChecks_dictionary = lbaasHealthChecks.analyze_entity(Statics.__rp_2_13['entry'])
    generate_on_screen_report(__lbaasHealthChecks_dictionary, report_directory, Statics.__rp_2_13['entry'])
    generate_mitigation_report(__lbaasHealthChecks_dictionary, report_directory, mitigation_report_name, Statics.__rp_2_13['fireup_items'])


def __call_2_14(config, signer, report_directory):    
    checkBackupPolicies = CheckBackupPolicies(
    Statics.__rp_2_14['entry'],
    Statics.__rp_2_14['area'],
    Statics.__rp_2_14['sub_area'],
    Statics.__rp_2_14['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_14['entry']+"_"+Statics.__rp_2_14['area']+"_"+Statics.__rp_2_14['sub_area']+"_mitigations"
    __checkBackupPolicies_dictionary = checkBackupPolicies.analyze_entity(Statics.__rp_2_14['entry'])
    generate_on_screen_report(__checkBackupPolicies_dictionary, report_directory, Statics.__rp_2_14['entry'])
    generate_mitigation_report(__checkBackupPolicies_dictionary, report_directory, mitigation_report_name, Statics.__rp_2_14['fireup_items'])


def __call_2_15(config, signer, report_directory):    
    backupDatabases = BackupDatabases(
    Statics.__rp_2_15['entry'],
    Statics.__rp_2_15['area'],
    Statics.__rp_2_15['sub_area'],
    Statics.__rp_2_15['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_15['entry']+"_"+Statics.__rp_2_15['area']+"_"+Statics.__rp_2_15['sub_area']+"_mitigations"
    __backupDatabases_dictionary = backupDatabases.analyze_entity(Statics.__rp_2_15['entry'])
    generate_on_screen_report(__backupDatabases_dictionary, report_directory, Statics.__rp_2_15['entry'])
    generate_mitigation_report(__backupDatabases_dictionary, report_directory, mitigation_report_name, Statics.__rp_2_15['fireup_items'])


def __call_2_17(config, signer, report_directory):    
    replicateData = ReplicateData(
    Statics.__rp_2_17['entry'],
    Statics.__rp_2_17['area'],
    Statics.__rp_2_17['sub_area'],
    Statics.__rp_2_17['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_17['entry']+"_"+Statics.__rp_2_17['area']+"_"+Statics.__rp_2_17['sub_area']+"_mitigations"
    __replicateData_dictionary = replicateData.analyze_entity(Statics.__rp_2_17['entry'])
    generate_on_screen_report(__replicateData_dictionary, report_directory, Statics.__rp_2_17['entry'])
    generate_mitigation_report(__replicateData_dictionary, report_directory, mitigation_report_name, Statics.__rp_2_17['fireup_items'])