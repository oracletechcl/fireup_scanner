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

security_lists = []
steering_policies = []
vcns_in_multiple_regions = []

### CIDRSize.py Global Variables
# VCN list for use with parallel_executor
vcns = []

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
users_with_api_keys = []

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
mysql_dbsystems = []
db_systems_with_no_backups = []
mysql_dbs_with_no_backups = []

### InstancePrincipal.py Global Variables
# Instance list for use with parallel_executor
instances = []


### DBSystemContro.py Global Variables
# Subnet list for use with parallel_executor
subnets = []
oracle_dbsystems = []
mysql_full_data = []
### ReplicateData.py Global Variables
# Lists for use with parallel_executor
block_volume_replicas = []
boot_volume_replicas = []
buckets = []
autonomous_databases = []
adb_nsgs = []

def executor(dependent_clients:list, independent_iterator:list, fuction_to_execute, threads:int, data_variable):
    if threads == 0:
        return []

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
    mysql_dbsystems = item[1:]

    backups = []
    backup_window = 10

    # Checks that each MySQL DB has a backup within the last `backup_window` days
    for mysql_database in mysql_dbsystems:
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


def get_user_with_api_keys(item):
    indentity_client = item[0]
    users = item[1:]

    user_data = []

    for user in users:
        api_key_data = get_api_key_data(indentity_client, user.id)
        user_api_keys = []
        for api_key in api_key_data:
            user_api_keys.append(api_key) 
        
        user_data.append( (user, user_api_keys) )

    return user_data


def get_policies_per_compartment(item):
    identity_client = item[0]
    compartments = item[1:]

    policies_per_compartment = []

    for compartment in compartments:
        policies = []
        policy_data = get_policies_data(identity_client, compartment.id)
        for policy in policy_data:
            policies.append(policy)
        policies_per_compartment.append(policies)

    return policies_per_compartment


def get_instances(item):
        compute_client = item[0]
        compartments = item[1:]

        instances = []

        for compartment in compartments:
            instance_data = get_instance_data(compute_client, compartment.id)
            for instance in instance_data:
                if "TERMINATED" not in instance.lifecycle_state:
                    instances.append(instance)

        return instances


def get_security_lists(item):
    network_client = item[0]
    compartments = item[1:]

    sec_lists = []

    for compartment in compartments:
        sec_list_data = get_security_list_data(network_client, compartment.id)
        for sec_list in sec_list_data:
            sec_lists.append(sec_list)

    return sec_lists


def get_subnets_in_compartments(item):
    network_client = item[0]
    compartments = item[1:]

    subnets = []
    for compartment in compartments:
        subnet_list_data = get_subnets_per_compartment_data(network_client, compartment.id)
        for snet in subnet_list_data:
            subnets.append(snet)
        
    return subnets

def get_nsgs(item):
    # Executor will get all nsgs that are associated to an Autonomous Database
    network_client = item[0]
    adbs = item[1:]

    adb_nsgs = []
    for adb in adbs:        
        region = adb.id.split('.')[3]
        if network_client[1] in region or network_client[2] in region:                                        
            nsg_id = adb.nsg_ids
            if nsg_id != None:
                for id in nsg_id:                    
                    nsg_list_data = get_nsg_rules_data(network_client[0], id)
                    adb_nsgs.append( (nsg_list_data, adb) )
        
    return adb_nsgs


def get_oracle_dbsystem(item):
    database_client = item[0]
    compartments = item[1:]

    oracle_dbsystem = []
    for compartment in compartments:
        dbdata = get_db_system_data(database_client, compartment.id)
        for db in dbdata:
            if db.lifecycle_state != "DELETED":
                oracle_dbsystem.append(db)
    
    return oracle_dbsystem


def get_mysql_dbsystem_full_info(item):
    database_client = item[0]
    mysql_dbs = item[1:]

    mysql_full_data = []
    for mysql_db in mysql_dbs:
        region = mysql_db.id.split('.')[3]
        if database_client[1] in region or database_client[2] in region:
            db = database_client[0].get_db_system(mysql_db.id).data
            if db.lifecycle_state != "DELETED":
                mysql_full_data.append(db)

    return mysql_full_data
def get_block_volume_replicas(item):
    block_storage_client = item[0][0]
    availability_domain = item[0][1]
    compartments = item[1:]

    block_volume_replicas = []

    for compartment in compartments:
        block_volume_replica_data = get_block_volume_replica_data(block_storage_client, availability_domain, compartment.id)
        for block_volume_replica in block_volume_replica_data:
            if "TERMINATED" not in block_volume_replica.lifecycle_state:
                block_volume_replicas.append(block_volume_replica)

    return block_volume_replicas


def get_boot_volume_replicas(item):
    block_storage_client = item[0][0]
    availability_domain = item[0][1]
    compartments = item[1:]

    boot_volume_replicas = []

    for compartment in compartments:
        boot_volume_replica_data = get_boot_volume_replica_data(block_storage_client, availability_domain, compartment.id)
        for boot_volume_replica in boot_volume_replica_data:
            if "TERMINATED" not in boot_volume_replica.lifecycle_state:
                boot_volume_replicas.append(boot_volume_replica)

    return boot_volume_replicas


def get_buckets(item):
    object_storage_client = item[0][0]
    namespace = item[0][1]
    compartments = item[1:]

    buckets = []

    for compartment in compartments:
        bucket_data = get_bucket_data(object_storage_client, namespace, compartment.id)
        for bucket in bucket_data:
            extended_bucket_data = object_storage_client.get_bucket(namespace, bucket.name).data
            buckets.append(extended_bucket_data)

    return buckets


def get_autonomous_databases(item):
    database_client = item[0]
    compartments = item[1:]

    autonomous_databases = []

    for compartment in compartments:
        autonomous_databases_data = get_auto_db_data(database_client, compartment.id)
        for autonomous_database in autonomous_databases_data:
            if autonomous_database.lifecycle_state != "TERMINATED":
                autonomous_databases.append(autonomous_database)

    return autonomous_databases


def get_steering_policies(item):
    dns_client = item[0]
    compartments = item[1:]

    steering_policies = []
    # debug_with_color_date('thread started', 'green')
    for compartment in compartments:
        steering_policy_data = get_steering_policy_data(dns_client, compartment.id)
        for steering_policy in steering_policy_data:
            # if steering_policy.lifecycle_state != "TERMINATED":
            steering_policies.append(steering_policy)
    # debug_with_color_date('thread stopped', 'red')
    return steering_policies


def check_vcns_in_multiple_regions(network_clients, regions, compartments, data_variable):

    workload_status = data_variable

    if len(workload_status) > 0:
        return workload_status[0]

    vcn_objects = executor(network_clients, compartments, get_vcns_in_compartments, len(compartments), vcns)

    vcn_regions = []

    for region in regions:
        for vcn in vcn_objects:
            vcn_region = vcn.id.split('.')[3]
            if region.region_name in vcn_region or region.region_key in vcn_region:
                if region not in vcn_regions:
                    vcn_regions.append(region)

    if len(vcn_regions) > 1:
        workload_status.append(True)
    else:
        workload_status.append(False)

    return workload_status[0]
