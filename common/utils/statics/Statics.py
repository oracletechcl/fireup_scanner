# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# statics.py 
#
# Purpose: Static methods and variables for FireUp

__version__ = 'v1.0.1'
__lenght_print__ = "230"


# Declare statics that are used more than one time on the code and have functional usage

__dbpatch_webscrapping_url__="https://docs.oracle.com/en-us/iaas/dbcs/doc/patch-db-system.html"
__dbpatch_webscrapping_id__="GUID-6D2A010B-2FDB-470D-B74A-015A11613CA6__GUID-118F3E93-D99C-4989-8B12-0D6BF485667F"


# declare dictionary with name of the review_point and entries for each entry on spreadsheet
__rp_1_1 = {
    'entry': '1.1',
    'area': 'Security and Compliance',
    'sub_area': 'Manage Identities and Authorization Policies',
    'review_point': 'Enforce the Use of Multi-Factor Authentication (MFA)',
    'success_criteria': 'Check if user has MFA enabled. Enforce with policy allow group GroupA to manage instance-family in tenancy where request.user.mfaTotpVerified=\'true\'',   
    'fireup_items': ["Fireup Tasks: 1 - Do you have MFA configured for any of your user accounts and restrictions on any resources? (e.g. must have MFA to access a DB resource)"]
}

__rp_1_2 = {
    'entry': '1.2',
    'area': 'Security and Compliance',
    'sub_area': 'Manage Identities and Authorization Policies',
    'review_point': 'Don\'t Use the Tenancy Administrator Account for Day-to-Day Operations',    
    'success_criteria': 'Check if there are policies that manage families of resources in tenancy',
    'fireup_items': ['Fireup Task: 2 - Are you logging/using same username/Password as admin for your day-day operations as well?']
}

__rp_1_3 = {
    'entry': '1.3',
    'area': 'Security and Compliance',
    'sub_area': 'Manage Identities and Authorization Policies',
    'review_point': 'Restrict the Admin Abilities of a Tenancy Administrators Group',
    'success_criteria': 'Check if the following policy is in place: Allow group UserAdmins to inspect groups in tenancy',    
    'fireup_items': ['Fireup Task: 2 - Are you logging/using same username/Password as admin for your day-day operations as well?']
}

__rp_1_4 = {
    'entry': '1.4',
    'area': 'Security and Compliance',
    'sub_area': 'Manage Identities and Authorization Policies',
    'review_point': 'Prevent Accidental or Malicious Deletion of (and Changes to) Access Policies',
    'success_criteria':'Check if the following policy is in place: Allow group PolicyAdmins to manage policies in tenancy where request.permission=\'POLICY_CREATE\'',    
    'fireup_items': ['Fireup Task: 2 - Are you logging/using same username/Password as admin for your day-day operations as well?']
}

__rp_1_5 = {
    'entry': '1.5',
    'area': 'Security and Compliance',
    'sub_area': 'Manage Identities and Authorization Policies',
    'review_point': 'Federate Oracle Cloud Infrastructure Identity and Access Management',
    'success_criteria': 'Check if user federation is in place and gross majority of users are federated (90 percent or more)',    
    'fireup_items': ['Fireup Task: 5 - Do you have a large user base', 'Fireup Task: 8 - Do all users have individual IAM Accounts?']
}

__rp_1_6 = {
    'entry': '1.6',
    'area': 'Security and Compliance',
    'sub_area': 'Manage Identities and Authorization Policies',
    'review_point': 'Monitor and Manage the Activities and Status of All Users',    
    'success_criteria': 'Check API Keys and if they are 90 days or more old, fail., Check that at least 5 users are created for tenancy',
    'fireup_items': ['Fireup Task: 3 - Do you have password rotation policy on schedule for all users and API Keys', 'Fireup Task: 4 - Is your user base larger than 5 users']
}

__rp_1_7 = {
    'entry': '1.7',
    'area': 'Security and Compliance',
    'sub_area': 'Isolate Resources and Control Access',
    'review_point': 'Organize Resources Using Compartments and Tags',    
    'success_criteria': 'Check that multiple compartments (and nested) are created. Check for Environment keywords such as PRD, Production, etc. Check if there are policies applied to the name of these compartments. Check if policies are created at root level and fail. Check if namespaces and tags are present and being used',
    'fireup_items': ['Fireup Task: 12 - Do you have a designated compartment for specific categories of resources for easier management', 'Fireup Task: 13 - Do you enforce policies or rules on who can move / migrate compartments', 'Fireup Task: 14 - Do you want to set a limit on number of resrouces on each compartment?', 'Fireup Task: 15 - Are there any IAM policies written at root level?']
}

__rp_1_8 = {
    'entry': '1.8',
    'area': 'Security and Compliance',
    'sub_area': 'Isolate Resources and Control Access',
    'review_point': 'Implement Role-Based Access Control', 
    'success_criteria': 'Check that policies are in place for compartment names for RBAC access',   
    'fireup_items': ['Fireup Task: 12 - Do you have a designated compartment for specific categories of resources for easier management', 'Fireup Task: 13 - Do you enforce policies or rules on who can move / migrate compartments', 'Fireup Task: 14 - Do you want to set a limit on number of resrouces on each compartment?', 'Fireup Task: 15 - Are there any IAM policies written at root level?']
}

__rp_1_9 = {
    'entry': '1.9',
    'area': 'Security and Compliance',
    'sub_area': 'Isolate Resources and Control Access',
    'review_point': 'Secure Cross-Resource Access', 
    'success_criteria': 'Check if instance principals are defined for users',   
    'fireup_items': ['Fireup Task: 17 - Are you using instance principals instead of storing credentials'],
}

__rp_1_10 = {
    'entry': '1.10',
    'area': 'Security and Compliance',
    'sub_area': 'Isolate Resources and Control Access',
    'review_point': 'Isolate Resources at the Network Layer', 
    'success_criteria': 'Check for Security List implementation without open permissions and/or NSGs for microsegmentation',   
    'fireup_items': ['Fireup Task: 18 - Do you have a proper security list, route tables, VCN, firewalls in place?', 'Fireup Task: 39 - Are you aware of some of the fixed service limits such as security lists/subnet?'],
}

__rp_1_11 = {
    'entry': '1.11',
    'area': 'Security and Compliance',
    'sub_area': 'Isolate Resources and Control Access',
    'review_point': 'Define Maximum Security Zones',    
    'success_criteria': 'Check if Maximum Security Zone is enabled for compartments that holster production workdload. Check Public and Private subnets are in place',
    'fireup_items': ['Fireup Task: 24 - Do you check the OCI Cloud Guard on your console for Security Recommendations?'],
}

__rp_1_12 = {
    'entry': '1.12',
    'area': 'Security and Compliance',
    'sub_area': 'Secure Your Databases',
    'review_point': 'Control User and Network Access',    
    'success_criteria': 'Check if DBSystems are in private subnets or not. Use NSG into DBSystems',
    'fireup_items': ['Fireup Task: 21 - Who has permissions to delete resources?', 'Fireup Task: 23 - Are databases and other confidential resources locked down in private subnets?'],
}

__rp_1_13 = {
    'entry': '1.13',
    'area': 'Security and Compliance',
    'sub_area': 'Secure Your Databases',
    'review_point': 'Restrict Permissions for Deleting Database Resources',    
    'success_criteria': '"Check that there is a DBA group and the following policies are applied: Allow group DBUsers to manage db-systems in tenancy where request.permission!=\'DB_SYSTEM_DELETE\' Allow group DBUsers to manage databases in tenancy where request.permission!=\'DATABASE_DELETE\' Allow group DBUsers to manage db-homes in tenancy where request.permission!=\'DB_HOME_DELETE\'',
    'fireup_items': ['Fireup Task: 21 - Who has permissions to delete resources?'],
}

__rp_1_14 = {
    'entry': '1.14',
    'area': 'Security and Compliance',
    'sub_area': 'Secure your Databases',
    'review_point': 'Encrypt Data',    
    'success_criteria': 'Check that Oracle Database created has a TDE Master Key rotated each 90 days',
    'fireup_items': ['Fireup Task: None'],
}

__rp_1_15 = {
    'entry': '1.15',
    'area': 'Security and Compliance',
    'sub_area': 'Secure your Databases',
    'review_point': 'Apply Security Patches',    
    'success_criteria': 'If Oracle Database is in place, make sure that its in the lastest patch set update available',
    'fireup_items': ['Fireup Task: 20 - Do you have an update / patching schedule on OS, Applications, etc?'],
}

__rp_1_16 = {
    'entry': '1.16',
    'area': 'Security and Compliance',
    'sub_area': 'Secure Your Databases',
    'review_point': 'Enable Private Endpoints for Autonomous Databases',    
    'success_criteria': 'If ATP is in place, make sure that a dedicated private subnet is allocated for it. For the private endpoint, define stateless security ingress rule and stateless egress rule. Restrict traffic only to subnets that will consume the service',
    'fireup_items': ['Fireup Task: 23 - Are databases and other confidential resources locked down in private subnets?'],
}

__rp_1_17 = {
    'entry': '1.17',
    'area': 'Security and Compliance',
    'sub_area': 'Protect Data at Rest',
    'review_point': 'Restrict Permissions for Deleting Storage Resources',    
    'success_criteria': 'If any type of storage is in place, make sure that the permissions listed on link are restricted',
    'fireup_items': ['Fireup Task: 21 - Who has permissions to delete resources?'],
}

__rp_1_18 = {
    'entry': '1.18',
    'area': 'Security and Compliance',
    'sub_area': 'Protect Data at Rest',
    'review_point': 'Ensure Secure Access to File Storage',
    'success_criteria': 'Mounting must be restricted only to consumers IP CIDR Blocks.',
    'fireup_items': ['Fireup Task: 25 - Are permissions for authorizing deletion of sensitive data locked down to certain users?'],
}

__rp_1_19 = {
    'entry': '1.19',
    'area': 'Security and Compliance',
    'sub_area': 'Protect Data at Rest',
    'review_point': 'Ensure Secure Access to Object Storage',    
    'success_criteria': 'Ensure that BUCKET_UPDATE is granted to minimal to none amount of users (less than 5%)',
    'fireup_items': ['Fireup Task: None'],
}

__rp_1_20 = {
    'entry': '1.20',
    'area': 'Security and Compliance',
    'sub_area': 'Protect Data at Rest',
    'review_point': 'Encrypt Data in Object Storage',    
    'success_criteria': 'Ensure that Bucket uses encryption using a master encryption key assigned to each bucket. Configure a single key per each bucket',
    'fireup_items': ['Fireup Task: None'],
}

__rp_1_21 = {
    'entry': '1.21',
    'area': 'Security and Compliance',
    'sub_area': 'Ensure Secure Network Access',
    'review_point': 'Secure the Load Balancers',
    'success_criteria': 'Ensure that LBaaS if exists, have TLS Certificates associated to them if in public subnets',
    'fireup_items': ['Fireup Task: 15 - Are there any IAM policies written at root level?'],
}

__rp_1_22 = {
    'entry': '1.22',
    'area': 'Security and Compliance',
    'sub_area': 'Ensure Secure Network Access',
    'review_point': 'Restrict Access Using Network Sources',    
    'success_criteria': 'Specify the network source in an IAM policy to restrict access to resources. Specify the network source in your tenancy\'s authentication settings to restrict sign in to the Console.',
    'fireup_items': ['Fireup Task: 18 - Do you have a proper security list, route tables, VCN, firewalls in place?'],
}

__rp_1_23 = {
    'entry': '1.23',
    'area': 'Security and Compliance',
    'sub_area': 'Ensure Secure Network Access',
    'review_point': 'Secure DNS Zones and Records',
    'success_criteria': 'If DNS Zone in place, define that IAM policy is in place to restrict modifications of records to a secluded group',
    'fireup_items': ['Fireup Task: 22 - Do you have a mechanism to prevent accidental deletion or change of policies?'],
}

__rp_1_24 = {
    'entry': '1.24',
    'area': 'Security and Compliance',
    'sub_area': 'Monitor and Audit Your Environment',
    'review_point': 'Enable Cloud Guard for Monitoring',    
    'success_criteria': 'Check if Cloud Guard is enabled',
    'fireup_items': ['Fireup Task: 24 - Do you check the OCI Cloud Guard on your console for Security Recommendations?'],
}

__rp_1_25 = {
    'entry': '1.25',
    'area': 'Security and Compliance',
    'sub_area': 'Monitor and Audit Your Environment',
    'review_point': 'Configure Auditing',    
    'success_criteria': 'Enable Auditing',
    'fireup_items': ['Fireup Task: None'],
}

__rp_1_26 = {
    'entry': '1.26',
    'area': 'Security and Compliance',
    'sub_area': 'Optimize the Security Posture of Your Environment',
    'review_point': 'Enable Oracle Cloud Guard for Optimization',    
    'success_criteria': 'Check if Cloud Guard is enabled',
    'fireup_items': ['Fireup Task: 24 - Do you check the OCI Cloud Guard on your console for Security Recommendations?'],
}

__rp_1_27 = {
    'entry': '1.27',
    'area': 'Security and Compliance',
    'sub_area': 'Secure Your Databases',
    'review_point': 'Enable Data Safe',
    'success_criteria': 'Check if databases are registered in Data Safe',
    'fireup_items': ['Fireup Task: 25 - Are permissions for authorizing deletion of sensitive data locked down to certain users?'],
}
__rp_1_28 = {
    'entry': '1.28',
    'area': 'Security and Compliance',
    'sub_area': 'Protect Data at Rest',
    'review_point': 'Encrypt Data in Block Volumes',    
    'success_criteria': 'Ensure that Block Volume uses encryption using user-created encryption key assigned to it. Configure a single key per Block Volume.',
    'fireup_items': ['Fireup Task: - None']
}

__rp_1_29 = {
    'entry': '1.29',
    'area': 'Security and Compliance',
    'sub_area': 'Protect Data at Rest',
    'review_point': 'Encrypt Data in File Storage',    
    'success_criteria': 'Ensure that File Storage uses encryption using user-created encryption key assigned to it. Configure a single key per each File System.',
    'fireup_items': ['Fireup Task: None'],
}

__rp_1_31 = {
    'entry': '1.31',
    'area': 'Security and Compliance',
    'sub_area': 'Ensure Secure Network Access',
    'review_point': 'Implement Network Access Controls',
    'success_criteria': 'Check if Web Application Firewall is enabled for public-facing HTTP and HTTPS services.',
    'fireup_items': ['Fireup Task: 31 - Are you leveraging traffic management, web firewall and load balancing for public resources?'],
}

__rp_1_30 = {
    'entry': '1.30',
    'area': 'Security and Compliance',
    'sub_area': 'Protect Data at Rest',
    'review_point': 'Maintain Application Secrets in Oracle Cloud Infrastructure Vault',
    'success_criteria': 'Check if Secret Reuse Rule and Secret Expiry Rule is defined per each Secret.',
    'fireup_items': ['Fireup Task: 30 - None'],
}

__rp_1_32 = {
    'entry': '1.32',
    'area': 'Security and Compliance',
    'sub_area': 'Monitor and Audit Your Environment',
    'review_point': 'Audit Your Policies',
    'success_criteria': 'Check if there are any duplicate Policy Statements.',
    'fireup_items': ['Fireup Task: 9 - 	Who is responsible for auditing logs for resources and activities?'],
}

__rp_1_33 = {
    'entry': '1.33',
    'area': 'Security and Compliance',
    'sub_area': 'Monitor and Audit Your Environment',
    'review_point': 'Continuously Scan for Vulnerabilities',
    'success_criteria': 'Check if the Vulnerability Scanning Service is working. Do it by checking if required IAM policies are created.',
    'fireup_items': ['Fireup Task: 9 - 	Who is responsible for auditing logs for resources and activities?'],
}

__rp_1_34 = {
    'entry': '1.34',
    'area': 'Security and Compliance',
    'sub_area': 'Isolate Resources and Control Access',
    'review_point': 'Harden Login Access to Compute Instances',
    'success_criteria': 'Check if Security Groups or Security Lists are created to restrict access to the instance based on the source IP address.',
    'fireup_items': ['Fireup Task: 18 - Do you have a proper security list, route tables, VCN, firewalls in place?'],
}

__rp_1_35 = {
    'entry': '1.35',
    'area': 'Security and Compliance',
    'sub_area': 'Ensure Secure Network Access',
    'review_point': 'Leverage Maximum Security Zones in Oracle Cloud Infrastructure',    
    'success_criteria': 'Check if Security Zones are created.',
    'fireup_items': ['Fireup Task: 24 - Do you check the OCI Cloud Guard on your console for Security Recommendations?'],
}

__rp_2_1 = {
    'entry': '2.1',
    'area': 'Reliability and Resilience',
    'sub_area': 'Design for Scalability',
    'review_point': 'Scale Cloud Resources to Meet Your Workload Requirements',    
    'success_criteria': 'Check if any autoscaling pool or kubernetes autoscaling is implemented',
    'fireup_items': ['Fireup task: 37 - Do you have procedures or designs in place to handle changes in demand? (Autoscaling)'],
}

__rp_2_2 = {
    'entry': '2.2',
    'area': 'Reliability and Resilience',
    'sub_area': 'Design for Scalability',
    'review_point': 'Distribute Your Traffic Across Availability Domains and Regions',
    'success_criteria': 'Check if solution is spread across more than one region',
    'fireup_items': ['Fireup task: 31 - Are you leveraging traffic management, web firewall and load balancing for public resources?'],
}

__rp_2_3 = {
    'entry': '2.3',
    'area': 'Reliability and Resilience',
    'sub_area': 'Manage Your Service Limits',
    'review_point': 'Understand the Default Service Limits of Your Tenancy',    
    'success_criteria': 'Check common limits and if those are in default values',
    'fireup_items': ['Fireup Task: 38 - Are you aware of default service limits to avoid any future loss of service'],
}

__rp_2_4 = {
    'entry': '2.4',
    'area': 'Reliability and Resilience',
    'sub_area': 'Manage Your Service Limits',
    'review_point': 'Monitor and Manage Your Service Limits',    
    'success_criteria': 'Check the current limits of the services and check if they are busy by 90% or more',
    'fireup_items': ['Fireup Task 40: - Do you have any policy/procedure in place for managing & monitoring service limits'],
}

__rp_2_5 = {
    'entry': '2.5',
    'area': 'Reliability and Resilience',
    'sub_area': 'Manage Your Service Limits',
    'review_point': 'Set Compartment Quotas',    
    'success_criteria': 'Check if Quotas are enabled',
    'fireup_items': ['Fireup Task: 14 - Do you want to set a limit on number of resources on each compartment?']
}

__rp_2_6 = {
    'entry': '2.6',
    'area': 'Reliability and Resilience',
    'sub_area': 'Manage Your Service Limits',
    'review_point': 'Factor Failover Usage in Your Service Limits',    
    'success_criteria': 'Check limits for most used artifacts and see if they are low (still on default or if usage vs available gap is 90% above, then fail)',
    'fireup_items': ['Fireup Task 40: - Do you have any policy/procedure in place for managing & monitoring service limits'],
}

__rp_2_7 = {
    'entry': '2.7',
    'area': 'Reliability and Resilience',
    'sub_area': 'Define Your Network and Connectivity Architecture',
    'review_point': 'Use Redundant Connections for Your On-Premises Environments and Private Resources',    
    'success_criteria': 'If VPN or fast connect exists, check for redundance (More than one)',
    'fireup_items': ['Fireup Task: 33 - Do you anticipate failure and have a recovery procedure in place'],
}

__rp_2_8 = {
    'entry': '2.8',
    'area': 'Reliability and Resilience',
    'sub_area': 'Define Your Network and Connectivity Architecture',
    'review_point': 'Establish Non-Overlapping Private Network Ranges Across Private Environments',    
    'success_criteria': 'Check if CIDR Blocks are overlapping in VCNs',
    'fireup_items': ['Fireup Task: 29 - Can you ensure that are no overlapping private IP spaces?']
}

__rp_2_9 = {
    'entry': '2.9',
    'area': 'Reliability and Resilience',
    'sub_area': 'Define Your Network and Connectivity Architecture',
    'review_point': 'Size Your Virtual Cloud Network to Allow for Expansion',    
    'success_criteria': 'Check CIDR Block size on VCN. Anything lower than /24 will fail',
    'fireup_items': ['Fireup Task: 30 - Do you have enough CIDR range for future expansions? (Make sure CIDRs are greater than /24)']
}

__rp_2_10 = {
    'entry': '2.10',
    'area': 'Reliability and Resilience',
    'sub_area': 'Define Your Network and Connectivity Architecture',
    'review_point': 'Establish Fault Tolerant and High Availability Connections for Your Public Workload',    
    'success_criteria': 'If LBaaS Exists check that it correctly uses distribution. See if DNS is implemented and if multiple regions are in place, check that Steering Policy are in place depending on region login',
    'fireup_items': ['Fireup Task: 31 - Are you leveraging traffic management, web firewall and load balancing for public resources?']
}

__rp_2_11 = {
    'entry': '2.11',
    'area': 'Reliability and Resilience',
    'sub_area': 'Define Your Network and Connectivity Architecture',
    'review_point': 'Bypass the Internet When Connecting to Public Resources',    
    'success_criteria': 'Depending on the subnet, check that correct Gateway is in place to access the internet properly',
    'fireup_items': ['Fireup Task: 31 - Are you leveraging traffic management, web firewall and load balancing for public resources?'],
}

__rp_2_12 = {
    'entry': '2.12',
    'area': 'Reliability and Resilience',
    'sub_area': 'Define Your Network and Connectivity Architecture',
    'review_point': 'Transit Routing',    
    'success_criteria': 'Check if HUB-and-Spoke pattern is in place',
    'fireup_items': ['Fireup Task: 33 -  Do you anticipate failure and have a recovery procedure in place'],
}

__rp_2_13 = {
    'entry': '2.13',
    'area': 'Reliability and Resilience',
    'sub_area': 'Understand the Health of Your Workload',
    'review_point': 'Implement Health Checks',    
    'success_criteria': 'If LBaaS exists, check that health checks are properly implemented and responding correctly',
    'fireup_items': ['Fireup Task: 33 - Do you anticipate failure and have a recovery procedure in place']
}

__rp_2_14 = {
    'entry': '2.14',
    'area': 'Reliability and Resilience',
    'sub_area': 'Back Up Your Data',
    'review_point': 'Backup Data in Storage Services',    
    'success_criteria': 'Check for backup policies on block volumes and snapshots are enabled for file storage systems',
    'fireup_items': ['Fireup Task: 34 - Have backups for failure (VMs, Block Storage, Object Storage, SSD, Database, have appropriate RPO/RTO).'],
}

__rp_2_15 = {
    'entry': '2.15',
    'area': 'Reliability and Resilience',
    'sub_area': 'Back Up Your Data',
    'review_point': 'Backup Data in Your Databases',    
    'success_criteria': 'If Oracle DB or MySQL is in place, check if backup strategy is in place',
    'fireup_items': ['Fireup Task: 34 - Have backups for failure (VMs, Block Storage, Object Storage, SSD, Database, have appropriate RPO/RTO).'],
}

__rp_2_16 = {
    'entry': '2.16',
    'area': 'Reliability and Resilience',
    'sub_area': 'Back Up Your Data',
    'review_point': 'Validate Backup Security and Encryption',    
    'success_criteria': 'Check policies are in place to provide access control for data and its backups. Check block volume in-transit encryption is enabled.',
    'fireup_items': ['Fireup Task: 34 - Have backups for failure (VMs, Block Storage, Object Storage, SSD, Database, have appropriate RPO/RTO).'],
}

__rp_2_17 = {
    'entry': '2.17',
    'area': 'Reliability and Resilience',
    'sub_area': 'Back Up Your Data',
    'review_point': 'Replicate Your Data for Disaster Recovery',    
    'success_criteria': 'If block storage in place, make sure that there is regional backup enabled. If Object storage, make sure to copy objects into another region. If Oracle DB In place, make sure to create a regional DR Dataguard.',
    'fireup_items': ['Fireup Task: 34 - Have backups for failure (VMs, Block Storage, Object Storage, SSD, Database, have appropriate RPO/RTO).'],
}

__rp_3_1 = {
    'entry': '3.1',
    'area': 'Performance and Cost Optimization',
    'sub_area': 'Performance Efficiency and Cost Optimization Practices',
    'review_point': 'Understand and Optimize Your Spending',    
    'success_criteria': 'Introduce Quotas on Compartments',
    'fireup_items': ['Fireup Task: 51 - How do you monitor usage and cost?'],
}

__rp_3_2 = {
    'entry': '3.2',
    'area': 'Performance and Cost Optimization',
    'sub_area': 'Plan the Compute Resources',
    'review_point': 'Learn About the Available Compute Instance Shapes',    
    'success_criteria': 'Check if default quotas are still implemented for compute shapes',
    'fireup_items': ['Fireup Task: 42 - How do you select your compute solution?'],
}

__rp_3_3 = {
    'entry': '3.3',
    'area': 'Performance and Cost Optimization',
    'sub_area': 'Tune and Monitor Network',
    'review_point': 'Learn About and Leverage SSL Termination Features',    
    'success_criteria': 'If Lbaas exists, check that SSL is implemented on it',
    'fireup_items': ['Fireup Task: 48 - Are you using load balancers? If so, where would you like to terminate SSL.'],
}

__rp_3_4 = {
    'entry': '3.4',
    'area': 'Performance and Cost Optimization',
    'sub_area': 'Tune and Monitor Network',
    'review_point': 'Choose a Region Location Based On Networking Requirements',
    'success_criteria': 'Check if VCN is implemented in more than one region',
    'fireup_items': ['Fireup Task: 29: Can you ensure that there are no overlapping private IP spaces?'],
}

__rp_3_5 = {
    'entry': '3.5',
    'area': 'Performance and Cost Optimization',
    'sub_area': 'Tune and Monitor Network',
    'review_point': 'Use Traffic Steering When Serving a Global Audience',    
    'success_criteria': 'If workload is in more than one region, check if traffic steering policy is in place',
    'fireup_items': ['Fireup Task: 33 - Do you anticipate failure and have a recovery procedure in place'],
}

__rp_3_6 = {
    'entry': '3.6',
    'area': 'Performance and Cost Optimization',
    'sub_area': 'Track and Manage Usage and Cost',
    'review_point': 'Implement a Compartment Structure That Fits Your Organization',    
    'success_criteria': 'Check if there is compartments beyond root, holstering the workload',
    'fireup_items': ['Fireup Task: 51 - How do you monitor usage and cost?'],
}

__rp_3_7 = {
    'entry': '3.7',
    'area': 'Performance and Cost Optimization',
    'sub_area': 'Track and Manage Usage and Cost',
    'review_point': 'Set Up Compartment Quota Policies to Control Resource Usage',    
    'success_criteria': 'Check if quotas are enabled for compartments',
    'fireup_items': ['Fireup Task: 14- Do you want to set a limit on number of resrouces on each compartment?'],
}

__rp_3_8 = {
    'entry': '3.8',
    'area': 'Performance and Cost Optimization',
    'sub_area': 'Track and Manage Usage and Cost',
    'review_point': 'Implement Cost Tracking Tags for Flexible Cost Tracking',
    'success_criteria': 'Check if Cost Tracking tags are in place',
    'fireup_items': ['Fireup Task: 66 - Do you use any configuration or infrastructure management tools?'],
}

__rp_3_9 = {
    'entry': '3.9',
    'area': 'Performance and Cost Optimization',
    'sub_area': 'Track and Manage Usage and Cost',
    'review_point': 'Define Budgets',    
    'success_criteria': 'Check if budgets are implemented on tenant',
    'fireup_items': ['Fireup Task: 52 - Have you implemented budgets and spending thresholds ', 'Fireup Task 53 - Do you have budgets for specific resource types'],
}

__rp_3_10 = {
    'entry': '3.10',
    'area': 'Performance and Cost Optimization',
    'sub_area': 'Track and Manage Usage and Cost',
    'review_point': 'Enable Block Volume Performance Auto Tuning',    
    'success_criteria': 'If block storage is in place, check that performance auto-tuning is implemented',
    'fireup_items': ['Fireup Task: 56 - How do you optimize workload performance & requirement vs cost?'],
}

__rp_3_11 = {
    'entry': '3.11',
    'area': 'Performance and Cost Optimization',
    'sub_area': 'Track and Manage Usage and Cost',
    'review_point': 'Implement Object Storage, Object Lifecycle Management',    
    'success_criteria': 'If object storage is in place, check that automated lifecycle policy is in place',
    'fireup_items': ['Fireup Task: 55 - Do you have a process to regularly terminate or stop unused resources & do you encourage employees to stop unused resources?'],
}

__rp_4_1 = {
    'entry': '4.1',
    'area': 'Operational Efficiency',
    'sub_area': 'Monitor Your Workload',
    'review_point': 'Monitor Compute Services',    
    'success_criteria': 'Ensure that monitoring plugins are enabled for all resources in tenancy',
    'fireup_items': ['Fireup Task: 59 - Do you have insight into the state & health of your workload'],
}

__rp_4_2 = {
    'entry': '4.2',
    'area': 'Operational Efficiency',
    'sub_area': 'Monitor Your Workload',
    'review_point': 'Create a Set of Alarms for Each Metric',    
    'success_criteria': 'Check that OS Management is enabled to do monitoring',
    'fireup_items': ['Fireup Task: 59 - Do you have insight into the state & health of your workload'],
}

__rp_4_3 = {
    'entry': '4.3',
    'area': 'Operational Efficiency',
    'sub_area': 'Monitor Your Workload Enable Service Logging',
    'review_point': 'Enable Service Logging',    
    'success_criteria': 'Check that pertaining components (if created) have the service logging enabled. API Gateways, Events, Functions, LBaaS, Object Storage, VCN Flow Logs among others',
    'fireup_items': ['Fireup Task:  59 - Do you have insight into the state & health of your workload'],
}

__rp_4_4 = {
    'entry': '4.4',
    'area': 'Operational Efficiency',
    'sub_area': 'Monitor Your Workload',
    'review_point': 'Enable OCI Operations Insights',    
    'success_criteria': 'Check if OCI Operations insights is enabled',
    'fireup_items': ['Fireup Task: 59 - Do you have insight into the state & health of your workload'],
}

__rp_4_5 = {
    'entry': '4.5',
    'area': 'Operational Efficiency',
    'sub_area': 'Monitor Your Workload',
    'review_point': 'Enable Cloud Guard',    
    'success_criteria': 'Check if Cloud Guard is enabled at root level of the tenancy',
    'fireup_items': ['Fireup Task: 24 - Do you check the OCI Cloud Guard on your console for Security Recommendations?'],
}

__rp_4_6 = {
    'entry': '4.6',
    'area': 'Operational Efficiency',
    'sub_area': 'Monitor Your Workload',
    'review_point': 'Configure Auditing',
    'success_criteria': 'Check that auditing is enabled on tenancy. Ensure the items are described in documentation',
    'fireup_items': ['Fireup Task 66: Do you use any configuration or infrastructure management tools?'],
}

__rp_4_7 = {
    'entry': '4.7',
    'area': 'Operational Efficiency',
    'sub_area': 'Manage Your Operating Systems',
    'review_point': 'Stay Up-to-Date with Security Patches, Bug Fixes, and Enhancement Updates',    
    'success_criteria': 'Check infrastructure created and if it applies see if it has the latest and greatest patching set',
    'fireup_items': ['Fireup Task 20: Do you have an update / patching schedule on OS, Applications, etc?'],
}


__rp_4_8 = {
    'entry': '4.8',
    'area': 'Operational Efficiency',
    'sub_area': 'Plan Your Deployment Strategy',
    'review_point': 'Adopt Terraform to Implement Repeatable Workflows',    
    'success_criteria': 'Check if Resource manager is in use with Terraform',
    'fireup_items': ['Fireup Task 66: Do you use any configuration or infrastructure management tools? '],
}

__rp_4_9 = {
    'entry': '4.9',
    'area': 'Operational Efficiency',
    'sub_area': 'Manage Your Operating Systems',
    'review_point': 'Automate OS Management',    
    'success_criteria': 'Check if OS Management has any jobs scheduled.',
    'fireup_items': ['Fireup Task 66: Do you use any configuration or infrastructure management tools?'],
}

