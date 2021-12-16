# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# paraexecvars.py
# Description: Parallel executor variables for use with helper.py

from concurrent import futures
from os import devnull
from common.utils.helpers.helper import *

identity_client = None
network_client = None

compartment_id = None
compartments = None

availability_domains = []

vcns = []
security_lists = []

### LBaasBackends.py + LBaaSHealthChecks.py Global Variables
# LBaas Clients
load_balancer_client = None
network_load_balancer_client = None
# LBaas lists for use with parallel_executor
load_balancers = []
network_load_balancers = []
load_balancer_healths = []
network_load_balancer_healths = []

### Rbac.py Global Variables
policies = []

### ApiKeys.py Global Variables
# Api Key list for use with parallel_executor
api_keys = []

### InstancePrincipal.py
instancePrincipal_dictionary = []
dyn_groups_per_compartment = []

### CheckBackupPolicies.py Global Variables
# Block storage lists for use with parallel_executor
block_volumes = []
boot_volumes = []
storages_with_no_policy = []
file_systems = []
file_system_snapshots = []


### BackupDatabases.py Global Variables
# Database list for use with parallel_executor
db_system_homes = []
mysql_databases = []
db_system_backups = []
mysql_backups = []

### InstancePrincipal.py Global Variables
# Instance list for use with parallel_executor
instances = []


def executor(dependent_clients:list, independent_iterator:list, fuction_to_execute, threads:int, data_variable):

    values = data_variable

    if len(values) > 0:
        return values

    items = []

    for client in dependent_clients:
        item = [client]
        for i, independent in enumerate(independent_iterator):
            item.append(independent)
            if i > 0 and i % 20 == 0:
                items.append(item)
                item = [client]
        items.append(item)

    with futures.ThreadPoolExecutor(threads) as executor:

        processes = [
            executor.submit(fuction_to_execute, item) 
            for item in items
        ]

        futures.wait(processes)

        for p in processes:
            for value in p.result():
                values.append(value)

    return values


def get_user_for_api_keys(item):
    indentity_client = item[0]
    users = item[1:]

    user_data = []

    for user in users:
        api_key_data = get_api_key_data(indentity_client, user['id'])
        for api_key in api_key_data:
            user['api_key'].append(api_key)

        user_data.append(user)

    return user_data


def get_vcns_in_compartments(item):
    network_client = item[0]
    compartments = item[1:]

    vcns = []

    for compartment in compartments:
        vcn_data = get_vcn_data(network_client, compartment.id)
        for vcn in vcn_data:
            vcns.append(vcn)

    return vcns