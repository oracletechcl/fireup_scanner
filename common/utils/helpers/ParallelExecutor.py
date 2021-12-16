# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# paraexecvars.py
# Description: Parallel executor variables for use with helper.py

from concurrent import futures
from common.utils.helpers.helper import *

from datetime import datetime, timedelta

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
file_systems_with_no_snapshots = []


### BackupDatabases.py Global Variables
# Database list for use with parallel_executor
db_system_homes = []
mysql_databases = []
db_systems_with_no_backups = []
mysql_dbs_with_no_backups = []

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

def get_availability_domains(identity_clients, tenancy_id):
    """
    Get all availability domains in a region using an identity client from each region
    """
    values = availability_domains

    # Return if function has already been run
    if len(values) > 0:
        return values

    with futures.ThreadPoolExecutor(len(identity_clients)) as executor:
        processes = [
            executor.submit(identity_client.list_availability_domains, tenancy_id)
            for identity_client in identity_clients
        ]

        futures.wait(processes)

        for p in processes:
            for value in p.result().data:
                values.append(value.name)
        
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
            if "TERMINATED" not in vcn.lifecycle_state:
                vcns.append(vcn)

    return vcns


def get_load_balancers(item):
    load_balancer_client = item[0]
    compartments = item[1:]

    load_balancers = []

    for compartment in compartments:
        load_balancer_data = get_load_balancer_data(load_balancer_client, compartment.id)
        for load_balancer in load_balancer_data:
            if "TERMINATED" not in load_balancer.lifecycle_state:
                load_balancers.append(load_balancer)

    return load_balancers


def get_network_load_balancers(item):
    network_load_balancer_client = item[0]
    compartments = item[1:]

    network_load_balancers = []

    for compartment in compartments:
        network_load_balancer_data = get_network_load_balancer_data(network_load_balancer_client, compartment.id)
        for network_load_balancer in network_load_balancer_data:
            if "TERMINATED" not in network_load_balancer.lifecycle_state:
                network_load_balancers.append(network_load_balancer)

    return network_load_balancers


def get_load_balancer_healths(item):
    """
    Takes a list of tuples in the form (load_balancer_client, region.name, region.key) as well as a list of load balancer dictionaries
    """
    client = item[0]
    load_balancers = item[1:]

    healths = []

    for load_balancer in load_balancers:
        debug_with_color_date('here', 'red')
        id = load_balancer.id
        if "networkloadbalancer" in id:
            if client[1] in id or client[2] in id:
                healths.append( (load_balancer, client[0].get_network_load_balancer_health(id).data) )
        else:
            if client[1] in id or client[2] in id:
                healths.append( (load_balancer, client[0].get_load_balancer_health(id).data) )

    return healths


def get_block_volumes(item):
    block_storage_client = item[0]
    compartments = item[1:]

    block_volumes = []

    for compartment in compartments:
        block_volume_data = get_block_volume_data(block_storage_client, compartment.id)
        for block_volume in block_volume_data:
            if "TERMINATED" not in block_volume.lifecycle_state:
                block_volumes.append(block_volume)

    return block_volumes


def get_boot_volumes(item):
    block_storage_client = item[0][0]
    availability_domain = item[0][1]
    compartments = item[1:]

    boot_volumes = []

    for compartment in compartments:
        boot_volume_data = get_boot_volume_data(block_storage_client, availability_domain, compartment.id)
        for boot_volume in boot_volume_data:
            if "TERMINATED" not in boot_volume.lifecycle_state:
                boot_volumes.append(boot_volume)

    return boot_volumes


def get_block_storages_with_no_policy(item):
    client = item[0]
    block_storages = item[1:]

    findings = []

    for block_storage in block_storages:
        id = block_storage.id
        region = id.split('.')[3]
        if "TERMINATED" not in block_storage.lifecycle_state:
            if client[1] in region or client[2] in region:
                if len(client[0].get_volume_backup_policy_asset_assignment(id).data) == 0:
                    findings.append(block_storage)

    return findings


def get_file_systems(item):
    file_storage_client = item[0][0]
    availability_domain = item[0][1]
    compartments = item[1:]

    file_systems = []

    for compartment in compartments:
        file_system_data = get_file_system_data(file_storage_client, compartment.id, availability_domain)
        for file_system in file_system_data:
            if "TERMINATED" not in file_system.lifecycle_state:
                file_systems.append(file_system)

    return file_systems


def get_file_systems_with_no_snapshots(item):
    client = item[0]
    file_systems = item[1:]

    findings = []

    for file_system in file_systems:
        id = file_system.id
        region = id.split('.')[3]
        # Replace added here as file systems use underscores in regions OCID
        if "TERMINATED" not in file_system.lifecycle_state:
            if client[1] in region or client[1].replace('-', '_') in region or client[2] in region:
                # Gets latest snapshot of each file system and checks its date is recent
                snapshots = client[0].list_snapshots(id).data
                if len(snapshots) > 0:
                    latest = snapshots[0].time_created.replace(tzinfo=None)
                    if datetime.now() > (latest + timedelta(days=10)):
                        findings.append(file_system)
                else:
                    findings.append(file_system)

    return findings


def get_database_homes(item):
    database_client = item[0]
    compartments = item[1:]

    db_homes = []

    for compartment in compartments:
        database_home_data = get_db_system_home_data(database_client, compartment.id)
        for db_home in database_home_data:
            if "DELETED" not in db_home.lifecycle_state:
                db_homes.append(db_home)

    return db_homes


def get_mysql_dbs(item):
    mysql_client = item[0]
    compartments = item[1:]

    databases = []

    for compartment in compartments:
        mysql_data = get_db_system_data(mysql_client, compartment.id)
        for mysql_db in mysql_data:
            if "DELETED" not in mysql_db.lifecycle_state:
                databases.append(mysql_db)

    return databases


def get_mysql_dbs_with_no_backups(item):
    mysql_backup_client = item[0]
    mysql_databases = item[1:]

    backups = []
    backup_window = 10

    # Checks that each MySQL DB has a backup within the last `backup_window` days
    for mysql_database in mysql_databases:
        region = mysql_database.id.split('.')[3]
        if mysql_backup_client[1] in region or mysql_backup_client[2] in region:
            backup_data = get_mysql_backup_data(mysql_backup_client[0], mysql_database.compartment_id)
            # Checks if there are any backups, the newest isn't deleted, 
            # matches to the current db, and is within the last `backup_window` days
            if len(backup_data) > 0: 
                if ("DELETED" not in backup_data[0].lifecycle_state and
                mysql_database.id == backup_data[0].db_system_id and
                datetime.now() > (backup_data[0].time_created.replace(tzinfo=None) + timedelta(days=backup_window))):
                    backups.append(mysql_database)
            else:
                backups.append(mysql_database)

    return backups


def get_db_systems_with_no_backups(item):
    database_client = item[0]
    db_system_homes = item[1:]

    disabled_backups = []

    for db_home in db_system_homes:
        region = db_home.id.split('.')[3]
        if database_client[1] in region or database_client[2] in region:
            databases = database_client[0].list_databases(db_home_id=db_home.id, system_id=db_home.db_system_id, compartment_id=db_home.compartment_id).data
            for db in databases:
                if "TERMINATED" not in db.lifecycle_state:
                    if not db.db_backup_config.auto_backup_enabled:
                        disabled_backups.append( (db, db_home) )

    return disabled_backups


def __search_user_for_api_keys(self, item):
    indentity_client = item[0]
    users = item[1:]

    user_data = []

    for user in users:
        api_key_data = get_api_key_data(indentity_client, user['id'])
        for api_key in api_key_data:
            api_key_record = {
                'fingerprint': api_key.fingerprint,
                'inactive_status': api_key.inactive_status,
                'lifecycle_state': api_key.lifecycle_state,
                'user_id': api_key.user_id,
                'time_created': api_key.time_created,  
            }
            user['api_key'].append(api_key_record) 
        
        user_data.append(user)

    return user_data
