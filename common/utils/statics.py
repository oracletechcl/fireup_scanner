# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# statics.py 
#
# Purpose: Static methods and variables for FireUp

__version__ = 'v1.0.0'
__lenght_print__ = "200"

# declare dictionary with name of the review_point and entries for each entry on spreadsheet
__rp_1_1 = {
    'entry': '1.1',
    'area': 'Security and Compliance',
    'sub_area': 'Manage Identities and Authorization Policies',
    'review_point': 'Enforce the Use of Multi-Factor Authentication (MFA)',
    'success_criteria': 'Check if user has MFA enabled. Enforce with policy allow group GroupA to manage instance-family in tenancy where request.user.mfaTotpVerified=\'true\''   
}

__rp_1_2 = {
    'entry': '1.2',
    'area': 'Security and Compliance',
    'sub_area': 'Manage Identities and Authorization Policies',
    'review_point': 'Don\'t Use the Tenancy Administrator Account for Day-to-Day Operations',    
    'success_criteria': 'Check if there are policies that manage families of resources in tenancy',
}

__rp_1_3 = {
    'entry': '1.3',
    'area': 'Security and Compliance',
    'sub_area': 'Manage Identities and Authorization Policies',
    'review_point': 'Restrict the Admin Abilities of a Tenancy Administrators Group',
    'success_criteria': 'Check if the following policy is in place: Allow group UserAdmins to inspect groups in tenancy',    
}

__rp_1_4 = {
    'entry': '1.4',
    'area': 'Security and Compliance',
    'sub_area': 'Manage Identities and Authorization Policies',
    'review_point': 'Prevent Accidental or Malicious Deletion of (and Changes to) Access Policies',
    'success_criteria':'Check if the following policy is in place: Allow group PolicyAdmins to manage policies in tenancy where request.permission=\'POLICY_CREATE\'',    
}

__rp_1_6 = {
    'entry': '1.5',
    'area': 'Security and Compliance',
    'sub_area': 'Manage Identities and Authorization Policies',
    'review_point': 'Federate Oracle Cloud Infrastructure Identity and Access Management',
    'success_criteria': 'Check if user federation is in place and gross majority of users are federated (90 percent or more)',    
}

__rp_1_6 = {
    'entry': '1.6',
    'area': 'Security and Compliance',
    'sub_area': 'Manage Identities and Authorization Policies',
    'review_point': 'Monitor and Manage the Activities and Status of All Users',    
    'success_criteria': 'Check API Keys and if they are 90 days or more old, fail., Check that at least 5 users are created for tenancy',
}

__rp_1_7 = {
    'entry': '1.7',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_8 = {
    'entry': '1.8',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '', 
    'success_criteria': '',   
}

__rp_1_9 = {
    'entry': '1.9',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',  
    'success_criteria': '',  
}

__rp_1_10 = {
    'entry': '1.10',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '', 
    'success_criteria': '',   
}

__rp_1_11 = {
    'entry': '1.11',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_12 = {
    'entry': '1.12',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_13 = {
    'entry': '1.13',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_14 = {
    'entry': '1.14',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_15 = {
    'entry': '1.15',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_16 = {
    'entry': '1.16',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_17 = {
    'entry': '1.17',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_18 = {
    'entry': '1.18',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_19 = {
    'entry': '1.19',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_20 = {
    'entry': '1.20',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_21 = {
    'entry': '1.21',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_22 = {
    'entry': '1.22',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_23 = {
    'entry': '1.23',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_24 = {
    'entry': '1.24',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_25 = {
    'entry': '1.25',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_1_26 = {
    'entry': '1.26',
    'area': 'Security and Compliance',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}


__rp_2_1 = {
    'entry': '2.1',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_2 = {
    'entry': '2.2',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_3 = {
    'entry': '2.3',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_4 = {
    'entry': '2.4',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_5 = {
    'entry': '2.5',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_6 = {
    'entry': '2.6',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_7 = {
    'entry': '2.7',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_8 = {
    'entry': '2.8',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_9 = {
    'entry': '2.9',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_10 = {
    'entry': '2.10',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_11 = {
    'entry': '2.11',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_12 = {
    'entry': '2.12',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_13 = {
    'entry': '2.13',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_14 = {
    'entry': '2.14',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_15 = {
    'entry': '2.15',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_16 = {
    'entry': '2.16',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_2_17 = {
    'entry': '2.17',
    'area': 'Reliability and Resilience',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_3_1 = {
    'entry': '3.1',
    'area': 'Performance and Cost Optimization',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_3_2 = {
    'entry': '3.2',
    'area': 'Performance and Cost Optimization',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_3_3 = {
    'entry': '3.3',
    'area': 'Performance and Cost Optimization',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_3_4 = {
    'entry': '3.4',
    'area': 'Performance and Cost Optimization',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_3_5 = {
    'entry': '3.5',
    'area': 'Performance and Cost Optimization',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_3_6 = {
    'entry': '3.6',
    'area': 'Performance and Cost Optimization',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_3_7 = {
    'entry': '3.7',
    'area': 'Performance and Cost Optimization',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_3_8 = {
    'entry': '3.8',
    'area': 'Performance and Cost Optimization',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_3_9 = {
    'entry': '3.9',
    'area': 'Performance and Cost Optimization',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_3_10 = {
    'entry': '3.10',
    'area': 'Performance and Cost Optimization',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_3_11 = {
    'entry': '3.11',
    'area': 'Performance and Cost Optimization',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_4_1 = {
    'entry': '4.1',
    'area': 'Operational Efficiency',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_4_2 = {
    'entry': '4.2',
    'area': 'Operational Efficiency',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_4_3 = {
    'entry': '4.3',
    'area': 'Operational Efficiency',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_4_4 = {
    'entry': '4.4',
    'area': 'Operational Efficiency',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_4_5 = {
    'entry': '4.5',
    'area': 'Operational Efficiency',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_4_6 = {
    'entry': '4.6',
    'area': 'Operational Efficiency',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}

__rp_4_7 = {
    'entry': '4.7',
    'area': 'Operational Efficiency',
    'sub_area': '',
    'review_point': '',    
    'success_criteria': '',
}