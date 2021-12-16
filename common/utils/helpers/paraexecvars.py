# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# paraexecvars.py
# Description: Parallel executor variables for use with helper.py

__identity_client = None
__network_client = None

__compartment_id = None
__compartments = None

__availability_domains = []

__vcns = []
__security_lists = []

### LBaasBackends.py + LBaaSHealthChecks.py Global Variables
# LBaas Clients
__load_balancer_client = None
__network_load_balancer_client = None
# LBaas lists for use with parallel_executor
__load_balancers = []
__network_load_balancers = []
__load_balancer_healths = []
__network_load_balancer_healths = []

### Rbac.py Global Variables
__policies = []

### ApiKeys.py Global Variables
# Api Key list for use with parallel_executor
global __api_keys

### InstancePrincipal.py
__instancePrincipal_dictionary = []
__dyn_groups_per_compartment = []

### CheckBackupPolicies.py Global Variables
# Block storage lists for use with parallel_executor
__block_volumes = []
__boot_volumes = []
__storages_with_no_policy = []
__file_systems = []
__file_system_snapshots = []


### BackupDatabases.py Global Variables
# Database list for use with parallel_executor
__db_system_homes = []
__mysql_databases = []
__db_system_backups = []
__mysql_backups = []

### InstancePrincipal.py Global Variables
# Instance list for use with parallel_executor
__instances = []