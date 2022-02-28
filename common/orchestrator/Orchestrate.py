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
from classes.securitycompliance.BucketPermissions import BucketPermissions
from classes.securitycompliance.StoragePermissions import StoragePermissions
from classes.securitycompliance.BucketEncryption import BucketEncryption
from classes.securitycompliance.MaxSecurityZone import MaxSecurityZone
from classes.securitycompliance.Rbac import Rbac
from classes.securitycompliance.SecureFileStorage import SecureFileStorage
from classes.securitycompliance.DBKeys import DBKeys
from classes.securitycompliance.DBSystemPatch import DBSystemPatch
from classes.securitycompliance.ADBSystemAccess import ADBSystemAccess
from classes.securitycompliance.CloudGuardMonitor import CloudGuardMonitor
from classes.securitycompliance.NetworkSources import NetworkSources
from classes.securitycompliance.AuditConfiguration import AuditConfiguration
from classes.securitycompliance.SecureLoadBalancers import SecureLoadBalancers
from classes.securitycompliance.SecureDNS import SecureDNS
from classes.securitycompliance.OptimizationMonitor import OptimizationMonitor
from classes.securitycompliance.EnableDataSafe import EnableDataSafe
from classes.securitycompliance.DuplicatePolicies import DuplicatePolicies

from classes.reliabilityresilience.ServiceLimits import ServiceLimits
from classes.reliabilityresilience.CompartmentQuotas import CompartmentQuotas
from classes.reliabilityresilience.BusyLimits import BusyLimits
from classes.reliabilityresilience.LowLimits import LowLimits
from classes.reliabilityresilience.RedundantConnections import RedundantConnections
from classes.reliabilityresilience.SeparateCIDRBlocks import SeparateCIDRBlocks
from classes.reliabilityresilience.CIDRSize import CIDRSize
from classes.reliabilityresilience.LBaaSBackends import LBaaSBackends
from classes.reliabilityresilience.LBaaSHealthChecks import LBaaSHealthChecks
from classes.reliabilityresilience.CheckBackupPolicies import CheckBackupPolicies
from classes.reliabilityresilience.CheckGateways import CheckGateways
from classes.reliabilityresilience.BackupDatabases import BackupDatabases
from classes.reliabilityresilience.DataSecurity import DataSecurity
from classes.reliabilityresilience.ReplicateData import ReplicateData
from classes.reliabilityresilience.CheckAutoscaling import CheckAutoscaling
from classes.reliabilityresilience.DistributeTraffic import DistributeTraffic
from classes.reliabilityresilience.TransitRouting import TransitRouting

from classes.performancecost.TenancyQuotas import TenancyQuotas
from classes.performancecost.CheckAutoTuning import CheckAutoTuning
from classes.performancecost.ComputeLimits import ComputeLimits
from classes.performancecost.TrafficSteering import TrafficSteering
from classes.performancecost.CompartmentWorkload import CompartmentWorkload
from classes.performancecost.LBaaSEncryption import LBaaSEncryption
from classes.performancecost.CheckBudgets import CheckBudgets
from classes.performancecost.OneRegionPerVCN import OneRegionPerVCN
from classes.performancecost.CompartmentQuotaPolicy import CompartmentQuotaPolicy
from classes.performancecost.LifecycleManagement import LifecycleManagement
from classes.performancecost.ImplementCostTrackingTags import ImplementCostTrackingTags

from classes.opsefficiency.MetricAlarms import MetricAlarms
from classes.opsefficiency.OperationsInsights import OperationsInsights
from classes.opsefficiency.ConfigureAuditing import ConfigureAuditing
from classes.opsefficiency.ServiceLogs import ServiceLogs
from classes.opsefficiency.CloudGuardEnabled import CloudGuardEnabled
from classes.opsefficiency.ResourceMonitoring import ResourceMonitoring
from classes.opsefficiency.PatchesAndUpdates import PatchesAndUpdates

from common.utils.reporter.report import *
from common.utils.statics import Statics
from tqdm import tqdm

def main_orchestrator(config, signer, report_directory):
    print_header("FireUp Scanner "+Statics.__version__)
    print_report_sub_header()

    orchestrated_list = [
                            # __call_1_1,
                            # __call_1_2,
                            # __call_1_3,
                            # __call_1_4,
                            # __call_1_5,
                            # __call_1_6,
                            # __call_1_7,
                            # __call_1_8,
                            # __call_1_9,
                            # __call_1_10,
                            # __call_1_11,
                            # __call_1_12,
                            # __call_1_13,
                            # __call_1_14,
                            # __call_1_15,
                            # __call_1_16,
                            # __call_1_17,
                            # __call_1_18,
                            # __call_1_19,
                            # __call_1_20,
                            # __call_1_21,
                            # __call_1_22,
                            # __call_1_23,
                            # __call_1_24,
                            # __call_1_25,
                            # __call_1_26,
                            # __call_1_27,
                            __call_1_32,
                            # __call_2_1,
                            # __call_2_2,
                            # __call_2_3,
                            # __call_2_4,
                            # __call_2_5,
                            # __call_2_6,
                            # __call_2_7,
                            # __call_2_8,
                            # __call_2_9,
                            # __call_2_10,
                            # __call_2_11,
                            # __call_2_12,
                            # __call_2_13,
                            # __call_2_14,
                            # __call_2_15,
                            # __call_2_16,
                            # __call_2_17,
                            # __call_3_1,
                            # __call_3_2,
                            # __call_3_3,
                            # __call_3_4,
                            # __call_3_5,
                            # __call_3_6,
                            # __call_3_7,
                            # __call_3_8,
                            # __call_3_9,
                            # __call_3_10,
                            # __call_3_11,
                            # __call_4_1,
                            # __call_4_2,
                            # __call_4_3,
                            # __call_4_4,
                            # __call_4_5,
                            # __call_4_6,
                            # __call_4_7,
                        ]

    for i in tqdm(range(len(orchestrated_list)), bar_format='{l_bar}{bar} | {n_fmt}/{total_fmt} ', initial=1, colour='green', position=0, leave=False):
        orchestrated_list[i](config,signer, report_directory)


def __call_1_1(config, signer, report_directory):
    mfa = Mfa(
    Statics.__rp_1_1['entry'], 
    Statics.__rp_1_1['area'], 
    Statics.__rp_1_1['sub_area'], 
    Statics.__rp_1_1['review_point'],     
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_1['entry']+"_"+Statics.__rp_1_1['area']+"_"+Statics.__rp_1_1['sub_area']+"_mitigations"
    __dictionary = mfa.analyze_entity(Statics.__rp_1_1['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_1['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_1['fireup_items'])


def __call_1_2(config, signer, report_directory):    
    admin = Admin(
    Statics.__rp_1_2['entry'], 
    Statics.__rp_1_2['area'], 
    Statics.__rp_1_2['sub_area'], 
    Statics.__rp_1_2['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_2['entry']+"_"+Statics.__rp_1_2['area']+"_"+Statics.__rp_1_2['sub_area']+"_mitigations"
    __dictionary = admin.analyze_entity(Statics.__rp_1_2['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_2['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_2['fireup_items'])


def __call_1_3(config, signer, report_directory):    
    adminAbility = AdminAbility(
    Statics.__rp_1_3['entry'], 
    Statics.__rp_1_3['area'], 
    Statics.__rp_1_3['sub_area'], 
    Statics.__rp_1_3['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_3['entry']+"_"+Statics.__rp_1_3['area']+"_"+Statics.__rp_1_3['sub_area']+"_mitigations"
    __dictionary = adminAbility.analyze_entity(Statics.__rp_1_3['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_3['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_3['fireup_items'])


def __call_1_4(config, signer, report_directory):    
    policyAdmin = PolicyAdmins(
    Statics.__rp_1_4['entry'], 
    Statics.__rp_1_4['area'], 
    Statics.__rp_1_4['sub_area'], 
    Statics.__rp_1_4['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_4['entry']+"_"+Statics.__rp_1_4['area']+"_"+Statics.__rp_1_4['sub_area']+"_mitigations"
    __dictionary = policyAdmin.analyze_entity(Statics.__rp_1_4['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_4['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_4['fireup_items'])


def __call_1_5(config, signer, report_directory):    
    federatedUsers = FederatedUsers(
    Statics.__rp_1_5['entry'], 
    Statics.__rp_1_5['area'], 
    Statics.__rp_1_5['sub_area'], 
    Statics.__rp_1_5['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_5['entry']+"_"+Statics.__rp_1_5['area']+"_"+Statics.__rp_1_5['sub_area']+"_mitigations"
    __dictionary = federatedUsers.analyze_entity(Statics.__rp_1_5['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_5['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_5['fireup_items'])


def __call_1_6(config, signer, report_directory):
    apiKeys = ApiKeys(
    Statics.__rp_1_6['entry'], 
    Statics.__rp_1_6['area'], 
    Statics.__rp_1_6['sub_area'], 
    Statics.__rp_1_6['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_6['entry']+"_"+Statics.__rp_1_6['area']+"_"+Statics.__rp_1_6['sub_area']+"_mitigations"
    __dictionary = apiKeys.analyze_entity(Statics.__rp_1_6['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_6['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_6['fireup_items'])


def __call_1_7(config, signer, report_directory):
    compPolicies = CompartmentsAndPolicies(
    Statics.__rp_1_7['entry'], 
    Statics.__rp_1_7['area'], 
    Statics.__rp_1_7['sub_area'], 
    Statics.__rp_1_7['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_7['entry']+"_"+Statics.__rp_1_7['area']+"_"+Statics.__rp_1_7['sub_area']+"_mitigations"
    __dictionary = compPolicies.analyze_entity(Statics.__rp_1_7['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_7['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_7['fireup_items'])


def __call_1_8(config, signer, report_directory):
    Rbacobject = Rbac(
    Statics.__rp_1_8['entry'], 
    Statics.__rp_1_8['area'], 
    Statics.__rp_1_8['sub_area'], 
    Statics.__rp_1_8['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_8['entry']+"_"+Statics.__rp_1_8['area']+"_"+Statics.__rp_1_8['sub_area']+"_mitigations"
    __dictionary = Rbacobject.analyze_entity(Statics.__rp_1_8['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_8['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_8['fireup_items'])


def __call_1_9(config, signer, report_directory):
    instancePrincipal = InstancePrincipal(
    Statics.__rp_1_9['entry'], 
    Statics.__rp_1_9['area'], 
    Statics.__rp_1_9['sub_area'], 
    Statics.__rp_1_9['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_9['entry']+"_"+Statics.__rp_1_9['area']+"_"+Statics.__rp_1_9['sub_area']+"_mitigations"
    __dictionary = instancePrincipal.analyze_entity(Statics.__rp_1_9['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_9['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_9['fireup_items'])


def __call_1_10(config, signer, report_directory):
    secList = SecurityList(
    Statics.__rp_1_10['entry'], 
    Statics.__rp_1_10['area'], 
    Statics.__rp_1_10['sub_area'], 
    Statics.__rp_1_10['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_10['entry']+"_"+Statics.__rp_1_10['area']+"_"+Statics.__rp_1_10['sub_area']+"_mitigations"
    __dictionary = secList.analyze_entity(Statics.__rp_1_10['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_10['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_10['fireup_items'])


def __call_1_11(config, signer, report_directory):
    secZone = MaxSecurityZone(
    Statics.__rp_1_11['entry'], 
    Statics.__rp_1_11['area'], 
    Statics.__rp_1_11['sub_area'], 
    Statics.__rp_1_11['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_11['entry']+"_"+Statics.__rp_1_11['area']+"_"+Statics.__rp_1_11['sub_area']+"_mitigations"
    __dictionary = secZone.analyze_entity(Statics.__rp_1_11['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_11['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_11['fireup_items'])


def __call_1_12(config, signer, report_directory):
    dbSystem = DBSystemControl(
    Statics.__rp_1_12['entry'], 
    Statics.__rp_1_12['area'], 
    Statics.__rp_1_12['sub_area'], 
    Statics.__rp_1_12['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_12['entry']+"_"+Statics.__rp_1_12['area']+"_"+Statics.__rp_1_12['sub_area']+"_mitigations"
    __dictionary = dbSystem.analyze_entity(Statics.__rp_1_12['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_12['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_12['fireup_items'])


def __call_1_13(config, signer, report_directory):
    dbPerms = DBPermissions(
    Statics.__rp_1_13['entry'], 
    Statics.__rp_1_13['area'], 
    Statics.__rp_1_13['sub_area'], 
    Statics.__rp_1_13['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_13['entry']+"_"+Statics.__rp_1_13['area']+"_"+Statics.__rp_1_13['sub_area']+"_mitigations"
    __dictionary = dbPerms.analyze_entity(Statics.__rp_1_13['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_13['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_13['fireup_items'])


def __call_1_14(config, signer, report_directory):
    dbKeys = DBKeys(
    Statics.__rp_1_14['entry'], 
    Statics.__rp_1_14['area'], 
    Statics.__rp_1_14['sub_area'], 
    Statics.__rp_1_14['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_14['entry']+"_"+Statics.__rp_1_14['area']+"_"+Statics.__rp_1_14['sub_area']+"_mitigations"
    __dictionary = dbKeys.analyze_entity(Statics.__rp_1_14['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_14['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_14['fireup_items'])


def __call_1_15(config, signer, report_directory):
    dbSystemPatch = DBSystemPatch(
    Statics.__rp_1_15['entry'], 
    Statics.__rp_1_15['area'], 
    Statics.__rp_1_15['sub_area'], 
    Statics.__rp_1_15['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_15['entry']+"_"+Statics.__rp_1_15['area']+"_"+Statics.__rp_1_15['sub_area']+"_mitigations"
    __dictionary = dbSystemPatch.analyze_entity(Statics.__rp_1_15['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_15['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_15['fireup_items'])


def __call_1_16(config, signer, report_directory):
    adbPermission = ADBSystemAccess(
    Statics.__rp_1_16['entry'], 
    Statics.__rp_1_16['area'], 
    Statics.__rp_1_16['sub_area'], 
    Statics.__rp_1_16['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_16['entry']+"_"+Statics.__rp_1_16['area']+"_"+Statics.__rp_1_16['sub_area']+"_mitigations"
    __dictionary = adbPermission.analyze_entity(Statics.__rp_1_16['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_16['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_16['fireup_items'])


def __call_1_17(config, signer, report_directory):
    storagePerms = StoragePermissions(
    Statics.__rp_1_17['entry'], 
    Statics.__rp_1_17['area'], 
    Statics.__rp_1_17['sub_area'], 
    Statics.__rp_1_17['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_17['entry']+"_"+Statics.__rp_1_17['area']+"_"+Statics.__rp_1_17['sub_area']+"_mitigations"
    __dictionary = storagePerms.analyze_entity(Statics.__rp_1_17['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_17['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_17['fireup_items'])



def __call_1_18(config, signer, report_directory):
    secureFileStorage = SecureFileStorage(
    Statics.__rp_1_18['entry'],
    Statics.__rp_1_18['area'],
    Statics.__rp_1_18['sub_area'],
    Statics.__rp_1_18['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_18['entry']+"_"+Statics.__rp_1_18['area']+"_"+Statics.__rp_1_18['sub_area']+"_mitigations"
    __dictionary = secureFileStorage.analyze_entity(Statics.__rp_1_18['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_18['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_18['fireup_items'])


def __call_1_19(config, signer, report_directory):
    bucket = BucketPermissions(
    Statics.__rp_1_19['entry'], 
    Statics.__rp_1_19['area'], 
    Statics.__rp_1_19['sub_area'], 
    Statics.__rp_1_19['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_19['entry']+"_"+Statics.__rp_1_19['area']+"_"+Statics.__rp_1_19['sub_area']+"_mitigations"
    __dictionary = bucket.analyze_entity(Statics.__rp_1_19['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_19['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_19['fireup_items'])


def __call_1_20(config, signer, report_directory):
    bucket = BucketEncryption(
    Statics.__rp_1_20['entry'], 
    Statics.__rp_1_20['area'], 
    Statics.__rp_1_20['sub_area'], 
    Statics.__rp_1_20['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_20['entry']+"_"+Statics.__rp_1_20['area']+"_"+Statics.__rp_1_20['sub_area']+"_mitigations"
    __dictionary = bucket.analyze_entity(Statics.__rp_1_20['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_20['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_20['fireup_items'])


def __call_1_21(config, signer, report_directory):
    secureLoadBalancers = SecureLoadBalancers(
    Statics.__rp_1_21['entry'],
    Statics.__rp_1_21['area'],
    Statics.__rp_1_21['sub_area'],
    Statics.__rp_1_21['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_21['entry']+"_"+Statics.__rp_1_21['area']+"_"+Statics.__rp_1_21['sub_area']+"_mitigations"
    __dictionary = secureLoadBalancers.analyze_entity(Statics.__rp_1_21['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_21['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_21['fireup_items'])


def __call_1_22(config, signer, report_directory):
    networkSources = NetworkSources(
    Statics.__rp_1_22['entry'], 
    Statics.__rp_1_22['area'], 
    Statics.__rp_1_22['sub_area'], 
    Statics.__rp_1_22['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_22['entry']+"_"+Statics.__rp_1_22['area']+"_"+Statics.__rp_1_22['sub_area']+"_mitigations"
    __dictionary = networkSources.analyze_entity(Statics.__rp_1_22['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_22['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_22['fireup_items'])


def __call_1_23(config, signer, report_directory):
    secureDNS = SecureDNS(
    Statics.__rp_1_23['entry'],
    Statics.__rp_1_23['area'],
    Statics.__rp_1_23['sub_area'],
    Statics.__rp_1_23['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_23['entry']+"_"+Statics.__rp_1_23['area']+"_"+Statics.__rp_1_23['sub_area']+"_mitigations"
    __dictionary = secureDNS.analyze_entity(Statics.__rp_1_23['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_23['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_23['fireup_items'])


def __call_1_24(config, signer, report_directory):
    cloudGuardEnable = CloudGuardMonitor(
    Statics.__rp_1_24['entry'],
    Statics.__rp_1_24['area'],
    Statics.__rp_1_24['sub_area'],
    Statics.__rp_1_24['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_24['entry']+"_"+Statics.__rp_1_24['area']+"_"+Statics.__rp_1_24['sub_area']+"_mitigations"
    __dictionary = cloudGuardEnable.analyze_entity(Statics.__rp_1_24['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_24['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_24['fireup_items'])


def __call_1_25(config, signer, report_directory):
    AuditEnable = AuditConfiguration(
    Statics.__rp_1_25['entry'], 
    Statics.__rp_1_25['area'], 
    Statics.__rp_1_25['sub_area'], 
    Statics.__rp_1_25['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_25['entry']+"_"+Statics.__rp_1_25['area']+"_"+Statics.__rp_1_25['sub_area']+"_mitigations"
    __dictionary = AuditEnable.analyze_entity(Statics.__rp_1_25['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_25['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_25['fireup_items'])


def __call_1_26(config, signer, report_directory):
    optimizationMonitor = OptimizationMonitor(
    Statics.__rp_1_26['entry'], 
    Statics.__rp_1_26['area'], 
    Statics.__rp_1_26['sub_area'], 
    Statics.__rp_1_26['review_point'], 
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_26['entry']+"_"+Statics.__rp_1_26['area']+"_"+Statics.__rp_1_26['sub_area']+"_mitigations"
    __dictionary = optimizationMonitor.analyze_entity(Statics.__rp_1_26['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_26['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_26['fireup_items'])


def __call_1_27(config, signer, report_directory):
    enableDataSafe = EnableDataSafe(
    Statics.__rp_1_27['entry'],
    Statics.__rp_1_27['area'],
    Statics.__rp_1_27['sub_area'],
    Statics.__rp_1_27['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_27['entry']+"_"+Statics.__rp_1_27['area']+"_"+Statics.__rp_1_27['sub_area']+"_mitigations"
    __dictionary = enableDataSafe.analyze_entity(Statics.__rp_1_27['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_27['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_27['fireup_items'])


def __call_1_32(config, signer, report_directory):
    duplicatePolicies = DuplicatePolicies(
    Statics.__rp_1_32['entry'],
    Statics.__rp_1_32['area'],
    Statics.__rp_1_32['sub_area'],
    Statics.__rp_1_32['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_1_32['entry']+"_"+Statics.__rp_1_32['area']+"_"+Statics.__rp_1_32['sub_area']+"_mitigations"
    __dictionary = duplicatePolicies.analyze_entity(Statics.__rp_1_32['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_1_32['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_1_32['fireup_items'])


def __call_2_1(config, signer, report_directory):
    autoscaling = CheckAutoscaling(
    Statics.__rp_2_1['entry'],
    Statics.__rp_2_1['area'],
    Statics.__rp_2_1['sub_area'],
    Statics.__rp_2_1['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_1['entry']+"_"+Statics.__rp_2_1['area']+"_"+Statics.__rp_2_1['sub_area']+"_mitigations"
    __dictionary = autoscaling.analyze_entity(Statics.__rp_2_1['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_1['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_1['fireup_items'])

def __call_2_2(config, signer, report_directory):
    distributeTraffic = DistributeTraffic(
    Statics.__rp_2_2['entry'],
    Statics.__rp_2_2['area'],
    Statics.__rp_2_2['sub_area'],
    Statics.__rp_2_2['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_2['entry']+"_"+Statics.__rp_2_2['area']+"_"+Statics.__rp_2_2['sub_area']+"_mitigations"
    __dictionary = distributeTraffic.analyze_entity(Statics.__rp_2_2['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_2['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_2['fireup_items'])


def __call_2_3(config, signer, report_directory):    
    serviceLimits = ServiceLimits(
    Statics.__rp_2_3['entry'],
    Statics.__rp_2_3['area'],
    Statics.__rp_2_3['sub_area'],
    Statics.__rp_2_3['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_3['entry']+"_"+Statics.__rp_2_3['area']+"_"+Statics.__rp_2_3['sub_area']+"_mitigations"
    __dictionary = serviceLimits.analyze_entity(Statics.__rp_2_3['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_3['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_3['fireup_items'])


def __call_2_4(config, signer, report_directory):    
    busyLimits = BusyLimits(
    Statics.__rp_2_4['entry'],
    Statics.__rp_2_4['area'],
    Statics.__rp_2_4['sub_area'],
    Statics.__rp_2_4['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_4['entry']+"_"+Statics.__rp_2_4['area']+"_"+Statics.__rp_2_4['sub_area']+"_mitigations"
    __dictionary = busyLimits.analyze_entity(Statics.__rp_2_4['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_4['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_4['fireup_items'])


def __call_2_5(config, signer, report_directory):    
    compQuotas = CompartmentQuotas(
    Statics.__rp_2_5['entry'],
    Statics.__rp_2_5['area'],
    Statics.__rp_2_5['sub_area'],
    Statics.__rp_2_5['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_5['entry']+"_"+Statics.__rp_2_5['area']+"_"+Statics.__rp_2_5['sub_area']+"_mitigations"
    __dictionary = compQuotas.analyze_entity(Statics.__rp_2_5['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_5['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_5['fireup_items'])


def __call_2_6(config, signer, report_directory):    
    lowLimits = LowLimits(
    Statics.__rp_2_6['entry'],
    Statics.__rp_2_6['area'],
    Statics.__rp_2_6['sub_area'],
    Statics.__rp_2_6['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_6['entry']+"_"+Statics.__rp_2_6['area']+"_"+Statics.__rp_2_6['sub_area']+"_mitigations"
    __dictionary = lowLimits.analyze_entity(Statics.__rp_2_6['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_6['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_6['fireup_items'])


def __call_2_7(config, signer, report_directory):    
    redundantConnections = RedundantConnections(
    Statics.__rp_2_7['entry'],
    Statics.__rp_2_7['area'],
    Statics.__rp_2_7['sub_area'],
    Statics.__rp_2_7['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_7['entry']+"_"+Statics.__rp_2_7['area']+"_"+Statics.__rp_2_7['sub_area']+"_mitigations"
    __dictionary = redundantConnections.analyze_entity(Statics.__rp_2_7['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_7['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_7['fireup_items'])


def __call_2_8(config, signer, report_directory):    
    separateCIDRBlocks = SeparateCIDRBlocks(
    Statics.__rp_2_8['entry'],
    Statics.__rp_2_8['area'],
    Statics.__rp_2_8['sub_area'],
    Statics.__rp_2_8['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_8['entry']+"_"+Statics.__rp_2_8['area']+"_"+Statics.__rp_2_8['sub_area']+"_mitigations"
    __dictionary = separateCIDRBlocks.analyze_entity(Statics.__rp_2_8['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_8['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_8['fireup_items'])


def __call_2_9(config, signer, report_directory):    
    cidrSize = CIDRSize(
    Statics.__rp_2_9['entry'],
    Statics.__rp_2_9['area'],
    Statics.__rp_2_9['sub_area'],
    Statics.__rp_2_9['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_9['entry']+"_"+Statics.__rp_2_9['area']+"_"+Statics.__rp_2_9['sub_area']+"_mitigations"
    __dictionary = cidrSize.analyze_entity(Statics.__rp_2_9['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_9['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_9['fireup_items'])


def __call_2_10(config, signer, report_directory):    
    lbaasBackends = LBaaSBackends(
    Statics.__rp_2_10['entry'],
    Statics.__rp_2_10['area'],
    Statics.__rp_2_10['sub_area'],
    Statics.__rp_2_10['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_10['entry']+"_"+Statics.__rp_2_10['area']+"_"+Statics.__rp_2_10['sub_area']+"_mitigations"
    __dictionary = lbaasBackends.analyze_entity(Statics.__rp_2_10['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_10['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_10['fireup_items'])


def __call_2_11(config, signer, report_directory):    
    checkGateways = CheckGateways(
    Statics.__rp_2_11['entry'],
    Statics.__rp_2_11['area'],
    Statics.__rp_2_11['sub_area'],
    Statics.__rp_2_11['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_11['entry']+"_"+Statics.__rp_2_11['area']+"_"+Statics.__rp_2_11['sub_area']+"_mitigations"
    __dictionary = checkGateways.analyze_entity(Statics.__rp_2_11['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_11['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_11['fireup_items'])


def __call_2_12(config, signer, report_directory):    
    transitRouting = TransitRouting(
    Statics.__rp_2_12['entry'],
    Statics.__rp_2_12['area'],
    Statics.__rp_2_12['sub_area'],
    Statics.__rp_2_12['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_12['entry']+"_"+Statics.__rp_2_12['area']+"_"+Statics.__rp_2_12['sub_area']+"_mitigations"
    __dictionary = transitRouting.analyze_entity(Statics.__rp_2_12['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_12['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_12['fireup_items'])


def __call_2_13(config, signer, report_directory):    
    lbaasHealthChecks = LBaaSHealthChecks(
    Statics.__rp_2_13['entry'],
    Statics.__rp_2_13['area'],
    Statics.__rp_2_13['sub_area'],
    Statics.__rp_2_13['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_13['entry']+"_"+Statics.__rp_2_13['area']+"_"+Statics.__rp_2_13['sub_area']+"_mitigations"
    __dictionary = lbaasHealthChecks.analyze_entity(Statics.__rp_2_13['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_13['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_13['fireup_items'])


def __call_2_14(config, signer, report_directory):    
    checkBackupPolicies = CheckBackupPolicies(
    Statics.__rp_2_14['entry'],
    Statics.__rp_2_14['area'],
    Statics.__rp_2_14['sub_area'],
    Statics.__rp_2_14['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_14['entry']+"_"+Statics.__rp_2_14['area']+"_"+Statics.__rp_2_14['sub_area']+"_mitigations"
    __dictionary = checkBackupPolicies.analyze_entity(Statics.__rp_2_14['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_14['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_14['fireup_items'])


def __call_2_15(config, signer, report_directory):    
    backupDatabases = BackupDatabases(
    Statics.__rp_2_15['entry'],
    Statics.__rp_2_15['area'],
    Statics.__rp_2_15['sub_area'],
    Statics.__rp_2_15['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_15['entry']+"_"+Statics.__rp_2_15['area']+"_"+Statics.__rp_2_15['sub_area']+"_mitigations"
    __dictionary = backupDatabases.analyze_entity(Statics.__rp_2_15['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_15['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_15['fireup_items'])


def __call_2_16(config, signer, report_directory):    
    dataSecurity = DataSecurity(
    Statics.__rp_2_16['entry'],
    Statics.__rp_2_16['area'],
    Statics.__rp_2_16['sub_area'],
    Statics.__rp_2_16['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_16['entry']+"_"+Statics.__rp_2_16['area']+"_"+Statics.__rp_2_16['sub_area']+"_mitigations"
    __dictionary = dataSecurity.analyze_entity(Statics.__rp_2_16['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_16['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_16['fireup_items'])


def __call_2_17(config, signer, report_directory):    
    replicateData = ReplicateData(
    Statics.__rp_2_17['entry'],
    Statics.__rp_2_17['area'],
    Statics.__rp_2_17['sub_area'],
    Statics.__rp_2_17['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_2_17['entry']+"_"+Statics.__rp_2_17['area']+"_"+Statics.__rp_2_17['sub_area']+"_mitigations"
    __dictionary = replicateData.analyze_entity(Statics.__rp_2_17['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_2_17['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_2_17['fireup_items'])


def __call_3_1(config, signer, report_directory):    
    tenancyQuotas = TenancyQuotas(
    Statics.__rp_3_1['entry'],
    Statics.__rp_3_1['area'],
    Statics.__rp_3_1['sub_area'],
    Statics.__rp_3_1['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_3_1['entry']+"_"+Statics.__rp_3_1['area']+"_"+Statics.__rp_3_1['sub_area']+"_mitigations"
    __dictionary = tenancyQuotas.analyze_entity(Statics.__rp_3_1['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_3_1['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_3_1['fireup_items'])

   
def __call_3_2(config, signer, report_directory):    
    computeLimits = ComputeLimits(
    Statics.__rp_3_2['entry'],
    Statics.__rp_3_2['area'],
    Statics.__rp_3_2['sub_area'],
    Statics.__rp_3_2['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_3_2['entry']+"_"+Statics.__rp_3_2['area']+"_"+Statics.__rp_3_2['sub_area']+"_mitigations"
    __dictionary = computeLimits.analyze_entity(Statics.__rp_3_2['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_3_2['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_3_2['fireup_items'])


def __call_3_3(config, signer, report_directory):    
    lbaasEncryption = LBaaSEncryption(
    Statics.__rp_3_3['entry'],
    Statics.__rp_3_3['area'],
    Statics.__rp_3_3['sub_area'],
    Statics.__rp_3_3['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_3_3['entry']+"_"+Statics.__rp_3_3['area']+"_"+Statics.__rp_3_3['sub_area']+"_mitigations"
    __dictionary = lbaasEncryption.analyze_entity(Statics.__rp_3_3['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_3_3['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_3_3['fireup_items'])

def __call_3_4(config, signer, report_directory):
    oneRegionPerVCN = OneRegionPerVCN(
    Statics.__rp_3_4['entry'],
    Statics.__rp_3_4['area'],
    Statics.__rp_3_4['sub_area'],
    Statics.__rp_3_4['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_3_4['entry']+"_"+Statics.__rp_3_4['area']+"_"+Statics.__rp_3_4['sub_area']+"_mitigations"
    __dictionary = oneRegionPerVCN.analyze_entity(Statics.__rp_3_4['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_3_4['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_3_4['fireup_items'])


def __call_3_5(config, signer, report_directory):    
    trafficSteering = TrafficSteering(
    Statics.__rp_3_5['entry'],
    Statics.__rp_3_5['area'],
    Statics.__rp_3_5['sub_area'],
    Statics.__rp_3_5['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_3_5['entry']+"_"+Statics.__rp_3_5['area']+"_"+Statics.__rp_3_5['sub_area']+"_mitigations"
    __dictionary = trafficSteering.analyze_entity(Statics.__rp_3_5['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_3_5['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_3_5['fireup_items'])


def __call_3_6(config, signer, report_directory):    
    compartmentWorkload = CompartmentWorkload(
    Statics.__rp_3_6['entry'],
    Statics.__rp_3_6['area'],
    Statics.__rp_3_6['sub_area'],
    Statics.__rp_3_6['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_3_6['entry']+"_"+Statics.__rp_3_6['area']+"_"+Statics.__rp_3_6['sub_area']+"_mitigations"
    __dictionary = compartmentWorkload.analyze_entity(Statics.__rp_3_6['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_3_6['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_3_6['fireup_items'])

def __call_3_7(config, signer, report_directory):    
    compartmentQuotaPolicy = CompartmentQuotaPolicy(
    Statics.__rp_3_7['entry'],
    Statics.__rp_3_7['area'],
    Statics.__rp_3_7['sub_area'],
    Statics.__rp_3_7['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_3_7['entry']+"_"+Statics.__rp_3_7['area']+"_"+Statics.__rp_3_7['sub_area']+"_mitigations"
    _dictionary = compartmentQuotaPolicy.analyze_entity(Statics.__rp_3_7['entry'])
    generate_on_screen_report(_dictionary, report_directory, Statics.__rp_3_7['entry'])
    generate_mitigation_report(_dictionary, report_directory, mitigation_report_name, Statics.__rp_3_7['fireup_items'])

def __call_3_8(config, signer, report_directory):
    implementCostTrackingTags = ImplementCostTrackingTags(
    Statics.__rp_3_8['entry'],
    Statics.__rp_3_8['area'],
    Statics.__rp_3_8['sub_area'],
    Statics.__rp_3_8['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_3_8['entry']+"_"+Statics.__rp_3_8['area']+"_"+Statics.__rp_3_8['sub_area']+"_mitigations"
    __dictionary = implementCostTrackingTags.analyze_entity(Statics.__rp_3_8['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_3_8['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_3_8['fireup_items'])


def __call_3_9(config, signer, report_directory):
    checkBudgets = CheckBudgets(
    Statics.__rp_3_9['entry'],
    Statics.__rp_3_9['area'],
    Statics.__rp_3_9['sub_area'],
    Statics.__rp_3_9['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_3_9['entry']+"_"+Statics.__rp_3_9['area']+"_"+Statics.__rp_3_9['sub_area']+"_mitigations"
    __dictionary = checkBudgets.analyze_entity(Statics.__rp_3_9['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_3_9['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_3_9['fireup_items'])


def __call_3_10(config, signer, report_directory):
    checkAutoTuning = CheckAutoTuning(
    Statics.__rp_3_10['entry'],
    Statics.__rp_3_10['area'],
    Statics.__rp_3_10['sub_area'],
    Statics.__rp_3_10['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_3_10['entry']+"_"+Statics.__rp_3_10['area']+"_"+Statics.__rp_3_10['sub_area']+"_mitigations"
    __dictionary = checkAutoTuning.analyze_entity(Statics.__rp_3_10['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_3_10['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_3_10['fireup_items'])


def __call_3_11(config, signer, report_directory):
    lifecycleManagement = LifecycleManagement(
    Statics.__rp_3_11['entry'],
    Statics.__rp_3_11['area'],
    Statics.__rp_3_11['sub_area'],
    Statics.__rp_3_11['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_3_11['entry']+"_"+Statics.__rp_3_11['area']+"_"+Statics.__rp_3_11['sub_area']+"_mitigations"
    __dictionary = lifecycleManagement.analyze_entity(Statics.__rp_3_11['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_3_11['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_3_11['fireup_items'])


def __call_4_1(config, signer, report_directory):    
    resourceMonitoring = ResourceMonitoring(
    Statics.__rp_4_1['entry'],
    Statics.__rp_4_1['area'],
    Statics.__rp_4_1['sub_area'],
    Statics.__rp_4_1['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_4_1['entry']+"_"+Statics.__rp_4_1['area']+"_"+Statics.__rp_4_1['sub_area']+"_mitigations"
    __dictionary = resourceMonitoring.analyze_entity(Statics.__rp_4_1['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_4_1['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_4_1['fireup_items'])


def __call_4_2(config, signer, report_directory):
    metricAlarms = MetricAlarms(
    Statics.__rp_4_2['entry'],
    Statics.__rp_4_2['area'],
    Statics.__rp_4_2['sub_area'],
    Statics.__rp_4_2['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_4_2['entry']+"_"+Statics.__rp_4_2['area']+"_"+Statics.__rp_4_2['sub_area']+"_mitigations"
    __dictionary = metricAlarms.analyze_entity(Statics.__rp_4_2['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_4_2['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_4_2['fireup_items'])


def __call_4_3(config, signer, report_directory):
    serviceLogs = ServiceLogs(
    Statics.__rp_4_3['entry'],
    Statics.__rp_4_3['area'],
    Statics.__rp_4_3['sub_area'],
    Statics.__rp_4_3['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_4_3['entry']+"_"+Statics.__rp_4_3['area']+"_"+Statics.__rp_4_3['sub_area']+"_mitigations"
    __dictionary = serviceLogs.analyze_entity(Statics.__rp_4_3['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_4_3['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_4_3['fireup_items'])


def __call_4_4(config, signer, report_directory):
    operationsInsights = OperationsInsights(
    Statics.__rp_4_4['entry'],
    Statics.__rp_4_4['area'],
    Statics.__rp_4_4['sub_area'],
    Statics.__rp_4_4['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_4_4['entry']+"_"+Statics.__rp_4_4['area']+"_"+Statics.__rp_4_4['sub_area']+"_mitigations"
    __dictionary = operationsInsights.analyze_entity(Statics.__rp_4_4['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_4_4['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_4_4['fireup_items'])


def __call_4_5(config, signer, report_directory):
    cloudGuardEnabled = CloudGuardEnabled(
    Statics.__rp_4_5['entry'],
    Statics.__rp_4_5['area'],
    Statics.__rp_4_5['sub_area'],
    Statics.__rp_4_5['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_4_5['entry']+"_"+Statics.__rp_4_5['area']+"_"+Statics.__rp_4_5['sub_area']+"_mitigations"
    __dictionary = cloudGuardEnabled.analyze_entity(Statics.__rp_4_5['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_4_5['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_4_5['fireup_items'])


def __call_4_6(config, signer, report_directory):
    configureAuditing = ConfigureAuditing(
    Statics.__rp_4_6['entry'],
    Statics.__rp_4_6['area'],
    Statics.__rp_4_6['sub_area'],
    Statics.__rp_4_6['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_4_6['entry']+"_"+Statics.__rp_4_6['area']+"_"+Statics.__rp_4_6['sub_area']+"_mitigations"
    __dictionary = configureAuditing.analyze_entity(Statics.__rp_4_6['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_4_6['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_4_6['fireup_items'])


def __call_4_7(config, signer, report_directory):
    patchesUpdates = PatchesAndUpdates(
    Statics.__rp_4_7['entry'],
    Statics.__rp_4_7['area'],
    Statics.__rp_4_7['sub_area'],
    Statics.__rp_4_7['review_point'],
    True, [], [], [], [], config, signer)
    mitigation_report_name = Statics.__rp_4_7['entry']+"_"+Statics.__rp_4_7['area']+"_"+Statics.__rp_4_7['sub_area']+"_mitigations"
    __dictionary = patchesUpdates.analyze_entity(Statics.__rp_4_7['entry'])
    generate_on_screen_report(__dictionary, report_directory, Statics.__rp_4_7['entry'])
    generate_mitigation_report(__dictionary, report_directory, mitigation_report_name, Statics.__rp_4_7['fireup_items'])
