# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# paraexecvars.py
# Description: Parallel executor variables for use with helper.py

from concurrent import futures
from common.utils.helpers.helper import *
from datetime import datetime, timedelta

availability_domains = []
security_lists = []

steering_policies = []
vcns_in_multiple_regions = None
oke_clusters = []

drgs = []
drg_attachment_ids = []
drg_attachments = []

service_gateways = []
local_peering_gateways = []

virtual_circuits = []

bucket_lifecycle_policies = []

limit_values_with_regions = []
limit_availabilities_with_regions = []

alarms = []
metrics = []
notifications = []

dbs_from_db_homes = []

operations_insights_warehouses = []
awr_hubs = []

### CIDRSize.py Global Variables
# VCN list for use with parallel_executor
vcns = []

### LBaasBackends.py + LBaaSHealthChecks.py Global Variables
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

### CheckBackupPolicies.py Global Variables
# Block storage lists for use with parallel_executor
block_volumes = []
boot_volumes = []
storages_with_no_policy = []
file_systems = []
file_systems_with_no_snapshots = []
mount_targets = []
export_options = []
security_lists_from_mount_targets = []


### BackupDatabases.py Global Variables
# Database list for use with parallel_executor
db_system_homes = []
mysql_dbsystems = []
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
bucket_preauthenticated_requests = []


### DBSystemPatch.py Global Variables
# Lists for use with parallel_executor
oracle_dbsystems_applicable_patches = []
oracle_db_home_patch_history = []
oracle_db_system_patch_history = []

### ConfigureAuditing.py Global Variables
service_connectors = []
bucket_retention_rules = []

### ServiceLogs.py Global Variables
log_groups = []
logs = []
applications = []
functions = []
ip_sec_connections = []
ip_sec_connections_tunnels = []
events_rules = []
### CheckAutoscaling.py Global Variables
autoscaling_configurations = []
instance_pools = []

### CompartmentQuotaPolicy.py Global Variables
quotas = []

### DistributeTraffic.py Global Variables
dns_zones = []

### TransitRouting.py Global Variables
networking_topology = []
cross_connects = []
topologies_with_cpe_connections = []

## OptimizationMonitor.py
# List for use with parallel_executor
detector_recipes = []
responder_recipes = []
detector_recipes_with_rules = []
responder_recipes_with_rules = []

## PatchesAndUpdates.py
# List for use with the parallel_executor
compute_instances = []
compute_images = []

## BlockVolumeEncryption.py
# List for use with the parallel_executor
volume_attachments = []
block_volumes_without_policy = []
## EnableDataSafe.py Global Variables
database_target_summaries = []
database_targets = []



## AdoptTerraform.py Global Variables
jobs = []

## HardenLoginAccess.py Global Variables
nsgs = []
nsg_rules = []


## Secrets.py Global Variables
secrets = []

## WebApplicationFirewall.py Global Variables
waf_firewalls = []

## CheckOSJobs.py Global Variables
managed_instances = []



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
    Get all availability domains using an identity client from each region
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


def get_dns_zones(item):
    dns_client = item[0]
    compartments = item[1:]

    dns_zones = []

    for compartment in compartments:
        dns_zones_data = get_dns_zone_data(dns_client, compartment.id)
        for dns_zone in dns_zones_data:
            if "TERMINATED" not in dns_zone.lifecycle_state:
                dns_zones.append(dns_zone)

    return dns_zones


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
        region = id.split('.')[3]
        if "networkloadbalancer" in id:
            if client[1] in region or client[2] in region:
                healths.append( (load_balancer, get_network_load_balancer_health_data(client[0], id)) )
        else:
            if client[1] in region or client[2] in region:
                healths.append( (load_balancer, get_load_balancer_health_data(client[0], id)) )

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

def get_volume_attachements(item):
    compute_client = item[0]
    compartments = item[1:]

    volume_attachments = []

    for compartment in compartments:
        volume_attachments_data = get_volume_attachments_per_compartment(compute_client, compartment.id)
        for volume_attachment in volume_attachments_data:
                volume_attachments.append(volume_attachment)
    return volume_attachments


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

def get_mounts(item):
    file_storage_client = item[0][0]
    availability_domain = item[0][1]
    compartments = item[1:]


    mount_targets = []

    for compartment in compartments:
        mount_target_data = get_mount_target_data(file_storage_client, compartment_id=compartment.id, availability_domain=availability_domain)
        for mount_target in mount_target_data:
            if "TERMINATED" not in mount_target.lifecycle_state:
                mount_targets.append(mount_target)
    return mount_targets


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

    db_system_homes = []

    for compartment in compartments:
        database_home_data = get_db_system_home_data(database_client, compartment.id)
        for db_home in database_home_data:
            if "DELETED" not in db_home.lifecycle_state:
                db_system_homes.append(db_home)

    return db_system_homes

def get_service_connectors_info(item):
    service_client = item[0]
    compartments = item[1:]

    service_connectors = []

    for compartment in compartments:
        service_connectors_data = get_service_connectors(service_client, compartment.id)
        for service_connector in service_connectors_data:
            service_connectors.append(service_connector)

    return service_connectors

def get_bucket_retention_rules_info(item):
    object_storage_client = item[0]
    bucket_objects = item[1:]

    bucket_retention_rules = []

    for bucket_object in bucket_objects:
        region = bucket_object.id.split('.')[3]
        if object_storage_client[2] in region or object_storage_client[3] in region:
            bucket_retention_rule_data = get_bucket_retention_rules(object_storage_client[0], bucket_object.namespace,bucket_object.name)

            for bucket_retention_rule in bucket_retention_rule_data:
                record = {
                    "display_name": bucket_retention_rule.display_name,
                    "bucket_name": bucket_object.name,
                    "bucket_id": bucket_object.id,
                    "duration": bucket_retention_rule.duration,
                    "etag": bucket_retention_rule.etag,
                    "id": bucket_retention_rule.id,
                    "time_created": bucket_retention_rule.time_created,
                    "time_modified": bucket_retention_rule.time_modified,
                    "time_rule_locked": bucket_retention_rule.time_rule_locked,
                }
                bucket_retention_rules.append(record)

    return bucket_retention_rules

def get_database_systems(item):
    database_client = item[0]
    compartments = item[1:]

    oracle_dbsystems = []

    for compartment in compartments:
        database_system_data = get_db_system_data(database_client, compartment.id)
        for db_sys in database_system_data:
            if "DELETED" not in db_sys.lifecycle_state:
                oracle_dbsystems.append(db_sys)

    return oracle_dbsystems

def get_mysql_dbs(item):
    mysql_client = item[0]
    compartments = item[1:]

    mysql_dbsystems = []

    for compartment in compartments:
        mysql_data = get_db_system_data(mysql_client, compartment.id)
        for mysql_db in mysql_data:
            if "DELETED" not in mysql_db.lifecycle_state:
                mysql_dbsystems.append(mysql_db)

    return mysql_dbsystems


def get_mysql_dbs_with_no_backups(item):
    mysql_backup_client = item[0]
    mysql_dbsystems = item[1:]

    mysql_dbs_with_no_backups = []
    backup_window = 10

    # Checks that each MySQL DB has a backup within the last `backup_window` days
    for mysql_database in mysql_dbsystems:
        region = mysql_database.id.split('.')[3]
        if mysql_backup_client[1] in region or mysql_backup_client[2] in region:
            backup_data = get_mysql_backup_data(mysql_backup_client[0], mysql_database.compartment_id)
            # Checks if there are any backups for the current db within the last `backup_window` days
            for backup in backup_data:
                if "DELETED" not in backup.lifecycle_state and mysql_database.id == backup.db_system_id:
                    if datetime.now() < (backup.time_created.replace(tzinfo=None) + timedelta(days=backup_window)):
                        break
            else:
                mysql_dbs_with_no_backups.append(mysql_database)

    return mysql_dbs_with_no_backups


def get_dbs_from_db_homes(item):
    database_client = item[0]
    db_system_homes = item[1:]

    dbs_from_db_homes = []

    for db_home in db_system_homes:
        region = db_home.id.split('.')[3]
        if database_client[1] in region or database_client[2] in region:
            databases = database_client[0].list_databases(db_home_id=db_home.id, system_id=db_home.db_system_id, compartment_id=db_home.compartment_id).data
            for db in databases:
                if "TERMINATED" not in db.lifecycle_state:
                    dbs_from_db_homes.append(db)

    return dbs_from_db_homes


def get_user_with_api_keys(item):
    indentity_client = item[0]
    users = item[1:]

    users_with_api_keys = []

    for user in users:
        api_key_data = get_api_key_data(indentity_client, user.id)
        user_api_keys = []
        for api_key in api_key_data:
            user_api_keys.append(api_key) 
        
        users_with_api_keys.append( (user, user_api_keys) )

    return users_with_api_keys


def get_policies(item):
    identity_client = item[0]
    compartments = item[1:]

    policies = []

    for compartment in compartments:
        policy_data = get_policies_data(identity_client, compartment.id)
        for policy in policy_data:
            policies.append(policy)

    return policies


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

def get_adb_nsgs(item):
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

def get_security_lists_from_mounts(item):
    network_client = item[0]
    mounts = item[1:]

    security_lists_from_mount_targets = []

    for mount in mounts:
        region = mount.subnet_id.split('.')[3]
        if network_client[1] in region or network_client[2] in region:
            subnet_info = network_client[0].get_subnet(subnet_id=mount.subnet_id)
            security_lists_info = network_client[0].get_security_list(security_list_id=subnet_info.data.security_list_ids)
            security_lists_from_mount_targets.append(security_lists_info.data)

    return security_lists_from_mount_targets

def get_export_options(item):
    file_storage_client = item[0]
    mounts = item[1:]

    export_options = []

    for mount in mounts:
        region = mount.subnet_id.split('.')[3]
        if file_storage_client[1] in region or file_storage_client[2] in region:
            export_info = file_storage_client[0].list_exports(export_set_id=mount.export_set_id)
            if len(export_info.data) != 0:
                export_details = file_storage_client[0].get_export(export_id=export_info.data[0].id)
                export_options.append(export_details.data)

    return export_options

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


def get_bucket_lifecycle_policies(item):
    object_storage_client = item[0]
    namespace = object_storage_client[1]
    buckets = item[1:]

    bucket_lifecycle_policies = []

    for bucket in buckets:
        region = bucket.id.split('.')[3]  
        if object_storage_client[2] in region or object_storage_client[3] in region:
            if bucket.object_lifecycle_policy_etag is not None:
                lifecycle_policies = object_storage_client[0].get_object_lifecycle_policy(namespace, bucket.name).data
                bucket_lifecycle_policies.append( (bucket, lifecycle_policies) )
            else:
                bucket_lifecycle_policies.append( (bucket, None) )

    return bucket_lifecycle_policies


def get_preauthenticated_requests_per_bucket(item):
    object_storage_client = item[0]
    namespace = object_storage_client[1]
    buckets = item[1:]

    bucket_preauthenticated_requests = []

    for bucket in buckets:
        region = bucket.id.split('.')[3]
        if object_storage_client[2] in region or object_storage_client[3] in region:
            preauthenticated_requests = get_preauthenticated_requests(object_storage_client[0], namespace, bucket.name)
            if preauthenticated_requests:
                bucket_preauthenticated_requests.append( (bucket, preauthenticated_requests) )

    return bucket_preauthenticated_requests


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


def get_database_home_patches(item):
    database_client = item[0]
    database_objects = item[1:]

    oracle_dbsystems_applicable_patches = []


    for db_ocids in database_objects:
        region = db_ocids.id.split('.')[3]
        if database_client[1] in region or database_client[2] in region:
            if db_ocids.lifecycle_state == "AVAILABLE":
                patches_data = get_db_home_patches(database_client[0], db_ocids.id)
                for patch in patches_data:
                    oracle_dbsystems_applicable_patches.append(patch)

    return oracle_dbsystems_applicable_patches

def get_database_homes_applied_patch_history(item):
    database_client = item[0]
    database_home_objects = item[1:]

    oracle_db_home_patch_history = []

    for db_home_ocids in database_home_objects:
        patch_ocid = ""

        region = db_home_ocids.id.split('.')[3]
        if database_client[1] in region or database_client[2] in region:
            if db_home_ocids.lifecycle_state == "AVAILABLE":
                patches_data = get_db_home_patch_history(database_client[0], db_home_ocids.id)
                db_home_patch_history_dict = {
                    "db_home_ocid": db_home_ocids.id,
                    "display_name": db_home_ocids.display_name,
                    "db_version": db_home_ocids.db_version,
                    "compartment_id": db_home_ocids.compartment_id,
                    "lifecycle_state": db_home_ocids.lifecycle_state,
                }
                if len(patches_data) > 0:
                    patch_ocid = patches_data[0].patch_id
                    db_home_patch_history_dict['patch_id'] = patch_ocid
                else:
                    db_home_patch_history_dict['patch_id'] = None

                oracle_db_home_patch_history.append(db_home_patch_history_dict)

    return oracle_db_home_patch_history


def get_database_systems_applied_patch_history(item):
    database_client = item[0]
    database_system_objects = item[1:]

    oracle_db_system_patch_history = []

    for db_system_ocids in database_system_objects:
        patch_ocid = ""
        region = db_system_ocids.id.split('.')[3]
        if database_client[1] in region or database_client[2] in region:
            if db_system_ocids.lifecycle_state == "AVAILABLE":
                patches_data = get_db_system_patch_history(database_client[0], db_system_ocids.id)
                db_system_patch_history_dict = {
                    "db_system_ocid": db_system_ocids.id,
                    "display_name": db_system_ocids.display_name,
                    "db_version": db_system_ocids.version,
                    "compartment_id": db_system_ocids.compartment_id,
                    "lifecycle_state": db_system_ocids.lifecycle_state,
                }
                if len(patches_data) > 0:
                    patch_ocid = patches_data[0].patch_id
                    db_system_patch_history_dict['patch_id'] = patch_ocid
                else:
                    db_system_patch_history_dict['patch_id'] = None

                oracle_db_system_patch_history.append(db_system_patch_history_dict)

    return oracle_db_system_patch_history


def get_steering_policies(item):
    dns_client = item[0]
    compartments = item[1:]

    steering_policies = []
    for compartment in compartments:
        steering_policy_data = get_steering_policy_data(dns_client, compartment.id)
        for steering_policy in steering_policy_data:
            steering_policies.append(steering_policy)

    return steering_policies


def check_vcns_in_multiple_regions(network_clients, regions, compartments):

    values = vcns_in_multiple_regions

    if values is not None:
        return values

    vcn_objects = executor(network_clients, compartments, get_vcns_in_compartments, len(compartments), vcns)

    vcn_regions = []

    for region in regions:
        for vcn in vcn_objects:
            vcn_region = vcn.id.split('.')[3]
            if region.region_name in vcn_region or region.region_key in vcn_region:
                if region not in vcn_regions:
                    vcn_regions.append(region)

    if len(vcn_regions) > 1:
        values = True
    else:
        values = False

    return values


def get_oke_clusters(item):
    container_engine_client = item[0]
    compartments = item[1:]

    oke_clusters = []

    for compartment in compartments:
        oke_cluster_data = get_oke_cluster_data(container_engine_client, compartment.id)
        for oke_cluster in oke_cluster_data:
            if oke_cluster.lifecycle_state != "DELETED":
                oke_clusters.append(oke_cluster)

    return oke_clusters 


def get_drgs(item):
    network_client = item[0]
    compartments = item[1:]

    drgs = []

    for compartment in compartments:
        drg_data = get_drg_data(network_client, compartment.id)
        for drg in drg_data:
            if "TERMINATED" not in drg.lifecycle_state:
                drgs.append(drg)

    return drgs


def get_drg_attachment_ids(item):
    network_client = item[0]
    drgs = item[1:]

    drg_attachment_ids = []

    for drg in drgs:
        region = drg.id.split('.')[3]
        if network_client[1] in region or network_client[2] in region:
            drg_attachment_ids_data = get_all_drg_attachments_data(network_client[0], drg.id)
            for drg_attachment_id in drg_attachment_ids_data:
                drg_attachment_ids.append(drg_attachment_id)

    return drg_attachment_ids


def get_drg_attachments(item):
    network_client = item[0]
    drg_attachment_ids = item[1:]

    drg_attachments = []

    for drg_attachment_id in drg_attachment_ids:
        region = drg_attachment_id.id.split('.')[3]
        if network_client[1] in region or network_client[2] in region:
            # A try, except is needed here for old version DRGs that do not return data correctly.
            try:
                drg_attachment_data = get_drg_attachment_data(network_client[0], drg_attachment_id.id)
                drg_attachments.append(drg_attachment_data)
            except:
                continue

    return drg_attachments


def get_service_gateways(item):
    network_client = item[0]
    compartments = item[1:]

    service_gateways = []

    for compartment in compartments:
        service_gateways_data = get_service_gateway_data(network_client, compartment.id)
        for service_gateway in service_gateways_data:
            if "TERMINATED" not in service_gateway.lifecycle_state:
                service_gateways.append(service_gateway)

    return service_gateways


def get_local_peering_gateways(item):
    network_client = item[0]
    compartments = item[1:]

    local_peering_gateways = []

    for compartment in compartments:
        local_peering_gateways_data = get_local_peering_gateway_data(network_client, compartment.id)
        for local_peering_gateway in local_peering_gateways_data:
            if "TERMINATED" not in local_peering_gateway.lifecycle_state:
                local_peering_gateways.append(local_peering_gateway)

    return local_peering_gateways


def get_virtual_circuits(item):
    network_client = item[0]
    compartments = item[1:]

    virtual_circuits = []

    for compartment in compartments:
        virtual_circuits_data = get_virtual_circuit_data(network_client, compartment.id)
        for virtual_circuit in virtual_circuits_data:
            if "TERMINATED" not in virtual_circuit.lifecycle_state:
                virtual_circuits.append(virtual_circuit)

    return virtual_circuits


def get_autoscaling_configurations(item):
    autoscaling_client = item[0]
    compartments = item[1:]

    autoscaling_configurations = []

    for compartment in compartments:
        autoscaling_configurations_data = get_autoscaling_configurations_data(autoscaling_client, compartment.id)
        for configuration in autoscaling_configurations_data:
            autoscaling_configurations.append(configuration)
            
    return autoscaling_configurations


def get_instance_pools(item):
    compute_management_client = item[0]
    compartments = item[1:]
    instance_pools = []

    for compartment in compartments:
        instance_pools_data = get_instance_pools_data(compute_management_client, compartment.id)
        for instance_pool in instance_pools_data:        
            instance_pools.append(instance_pool)
        
    return instance_pools


def get_limit_values(item):
    limits_client = item[0][0]
    tenancy_id = item[0][1]
    region = item[0][2]
    services = item[1:]

    limit_values_with_regions = []

    for service in services:
        limit_value_data = get_limit_value_data(limits_client, tenancy_id, service.name)
        for limit_value in limit_value_data:
            limit_values_with_regions.append( (region, service.name, limit_value) )

    return limit_values_with_regions


def get_limit_availabilities(item):
    limits_client = item[0][0]
    tenancy_id = item[0][1]
    region = item[0][2]
    limit_values = item[1:]

    limit_availabilities_with_regions = []

    for limit_value in limit_values:
        if region == limit_value[0]:
            if "AD" in limit_value[2].scope_type:
                limit_availabilities_with_regions.append( (region, limit_value[1], limit_value[2], get_resource_availability_data(limits_client, limit_value[1], limit_value[2].name, tenancy_id, limit_value[2].availability_domain)) )
            else:
                limit_availabilities_with_regions.append( (region, limit_value[1], limit_value[2], get_resource_availability_data(limits_client, limit_value[1], limit_value[2].name, tenancy_id)) )

    return limit_availabilities_with_regions


def get_alarms(item):
    monitoring_client = item[0]
    compartments = item[1:]

    alarms = []

    for compartment in compartments:
        alarm_data = get_alarm_data(monitoring_client, compartment.id)
        for alarm in alarm_data:
            if "DELETED" not in alarm.lifecycle_state:
                alarms.append(alarm)

    return alarms


def get_metrics(item):
    monitoring_client = item[0]
    compartments = item[1:]

    metrics = []

    for compartment in compartments:
        metric_data = get_metric_data(monitoring_client, compartment.id)
        for metric in metric_data:
            metrics.append(metric)

    return metrics


def get_log_groups(item):
    logging_management_client = item[0]
    compartments = item[1:]

    log_groups = []

    for compartment in compartments:
        log_groups_data = get_log_group_data_per_compartment(logging_management_client, compartment.id)
        for log_group in log_groups_data:
            log_groups.append(log_group)
    
    return log_groups


def get_logs(item):
    logging_management_client = item[0]
    log_groups = item[1:]

    logs = []

    for log_group in log_groups:
        region = log_group.id.split('.')[3]
        if logging_management_client[1] in region or logging_management_client[2] in region:    
            logs_data = get_log_data(logging_management_client[0], log_group.id)
            for log in logs_data:
                if log.configuration:
                    logs.append(log)
    return logs


def get_applications(item):
    functions_management_client = item[0]
    compartments = item[1:]

    applications = []

    for compartment in compartments:
        application_data = get_applications_per_compartment(functions_management_client, compartment.id)
        for application in application_data:
            applications.append(application)
    return applications


def get_functions(item):
    functions_management_client = item[0]
    applications = item[1:]

    functions = []

    for application in applications:
        region = application.id.split('.')[3]
        if functions_management_client[1] in region or functions_management_client[2] in region:    
            functions_data = get_functions_per_application(functions_management_client[0], application.id)
            for function in functions_data:
                functions.append(function)
    return functions


def get_ip_sec_connections(item):
    network_client = item[0]
    compartments = item[1:]

    ip_sec_connections = []

    for compartment in compartments:
        ip_sec_data = get_ip_sec_connections_per_compartment(network_client, compartment.id)
        for ip_sec_connection in ip_sec_data:
            if ip_sec_connection:
                ip_sec_connections.append(ip_sec_connection)
    return ip_sec_connections


def get_ip_sec_connections_tunnels(item):
    network_client = item[0]
    ip_sec_connections = item[1:]
    
    ip_sec_connections_tunnels= []

    for connection in ip_sec_connections:
        region = connection.id.split('.')[3]
        if network_client[1] in region or network_client[2] in region:    
            connection_data = get_ip_sec_connections_tunnels_per_connection(network_client[0], connection.id)
            for tunnel in connection_data:
                ip_sec_connections_tunnels.append(tunnel)

    return ip_sec_connections_tunnels


def get_events_rules(item):
    events_client = item[0]
    compartments = item[1:]

    events_rules = []

    for compartment in compartments:
        rule_data = get_event_rules_per_compartment(events_client, compartment.id)
        for rule in rule_data:
            events_rules.append(rule)
    return events_rules


def get_quotas_in_compartments(item):
    # Pull out the client that you need as well as the list of compartments from the passed item
    quota_client = item[0]
    compartments = item[1:]

    quotas = []
    for compartment in compartments:
        quota_data = list_quota_data(quota_client, compartment.id)
        for quota in quota_data:
            if "TERMINATED" not in quota.lifecycle_state:
                quotas.append(quota)

    return quotas


def get_cross_connects(item):
    network_client = item[0]
    compartments = item[1:]

    cross_connects = []

    for compartment in compartments:
        cross_connects_data = get_cross_connects_per_compartment(network_client, compartment.id)
        if cross_connects_data:
            cross_connects.append(cross_connects_data)

    return cross_connects


def get_networking_topologies(item):
    network_client = item[0]
    compartments_with_regions = item[1:]

    topologies_with_cpe_connections = []

    for compartment, region in compartments_with_regions:
        if region == network_client[1] or region == network_client[2]:
            network_client[0].base_client.endpoint = f"https://vnca-api.{network_client[1]}.oci.oraclecloud.com"
            topologies_with_cpe_connections.append(get_networking_topology_per_compartment(network_client[0], compartment))

    return topologies_with_cpe_connections


def get_operations_insights_warehouses(item):
    operations_insights_client = item[0]
    tenancy_id = item[1]

    operations_insights_warehouses = []

    warehouse_data = list_operations_insights_warehouses(operations_insights_client, tenancy_id)
    for warehouse in warehouse_data.items:
        operations_insights_warehouses.append(warehouse)

    return operations_insights_warehouses


def get_awr_hubs(item):
    operations_insights_client = item[0]
    operations_insights_warehouses = item[1:]

    awr_hubs = []

    for warehouse in operations_insights_warehouses:
        region = warehouse.id.split('.')[3]
        if operations_insights_client[1] in region or operations_insights_client[2] in region:    
            awr_hubs_data = list_awr_hubs(operations_insights_client[0], warehouse.id, warehouse.compartment_id)
            for awr_hub in awr_hubs_data.items:
                awr_hubs.append(awr_hub)

    return awr_hubs
def get_detector_recipes(item):
    cloud_guard_client = item[0]
    compartments = item[1:]

    detector_recipes = []

    for compartment in compartments:
        detector_recipes_data = get_detector_recipes_by_compartments(cloud_guard_client, compartment.id)
        for detector_recipe in detector_recipes_data:
            detector_recipes.append(detector_recipe)

    return detector_recipes


def get_responder_recipes(item):
    cloud_guard_client = item[0]
    compartments = item[1:]

    responder_recipes = []

    for compartment in compartments:
        responder_recipes_data = get_responder_recipes_by_compartments(cloud_guard_client, compartment.id)
        for responder_recipe in responder_recipes_data:
            responder_recipes.append(responder_recipe)

    return responder_recipes

def get_detector_rules(item):
    cloud_guard_client = item[0]
    detector_recipes = item[1:]

    detector_recipes_with_rules = []

    for detector_recipe in detector_recipes:
        rules = get_detector_rules_by_compartment(cloud_guard_client, detector_recipe.id, detector_recipe.compartment_id)
        detector_recipes_with_rules.append( (detector_recipe, rules) )

    return detector_recipes_with_rules


def get_responder_rules(item):
    cloud_guard_client = item[0]
    responder_recipes = item[1:]

    responder_recipes_with_rules = []

    for responder_recipe in responder_recipes:
        rules = get_responder_rules_by_compartment(cloud_guard_client, responder_recipe.id, responder_recipe.compartment_id)
        responder_recipes_with_rules.append( (responder_recipe, rules) )

    return responder_recipes_with_rules


def get_notifications(item):
    notification_control_plane_client = item[0]
    compartments = item[1:]

    notifications = []

    for compartment in compartments:
        notification_data = get_notification_data(notification_control_plane_client, compartment.id)
        for notification in notification_data:
            notifications.append(notification)

    return notifications


def get_compute_instances(item):
    compute_client = item[0]
    compartments = item[1:]

    compute_instances = []

    for compartment in compartments:
        compute_data = get_compute_data(compute_client, compartment.id)        
        for compute in compute_data:
            compute_instances.append(compute)

    return compute_instances


def get_compute_images(item):
    compute_client = item[0]
    compartments = item[1:]

    compute_images = []

    for compartment in compartments:
        compute_data = get_compute_image_data(compute_client, compartment.id)        
        for compute in compute_data:
            compute_images.append(compute)

    return compute_images


def get_database_target_summaries(item):
    data_safe_client = item[0]
    root_compartment = item[1]

    return list_target_databases_data(data_safe_client, root_compartment.id)


def get_database_targets(item):
    data_safe_client = item[0]
    database_target_summaries = item[1:]

    database_targets = []

    for summary in database_target_summaries:
        region = summary.id.split('.')[3]
        if data_safe_client[1] in region or data_safe_client[2] in region:    
            database_targets.append(get_target_database_data(data_safe_client[0], summary.id))

    return database_targets

    

def get_resource_manager_jobs(item):
    resource_manager_client = item[0]
    compartments = item[1:]

    jobs = []

    for compartment in compartments:
        jobs_data = get_resource_manager_jobs_per_compartment(resource_manager_client, compartment.id)
        if jobs_data:
            jobs.append(jobs_data)
    return jobs


def get_nsgs(item):
    network_client = item[0]
    compartments = item[1:]

    nsgs = []

    for compartment in compartments:
        nsg_info = get_network_security_groups_data(network_client=network_client, compartment_id=compartment.id)
        for nsg_value in nsg_info:
            nsg = network_client.get_network_security_group(network_security_group_id=nsg_value.id).data
            nsgs.append(nsg)

    return nsgs


def get_nsg_rules(item):
    network_client = item[0]
    nsgs = item[1:]

    nsg_rules = []

    for nsg in nsgs:
        region = nsg.id.split('.')[3]
        if network_client[1] in region or network_client[2] in region: 
            rules = get_nsg_rules_data(network_client[0], nsg.id)
            nsg_rules.append((nsg,rules))

    return nsg_rules

  
def get_secrets(item):
    vaults_client = item[0]
    compartments = item[1:]

    secrets = []

    for compartment in compartments:
        secret_list = get_secrets_per_compartment(vaults_client, compartment.id)
        for secret in secret_list:
            secrets.append(get_secret_data(vaults_client,secret.id))
    return secrets


def get_waf_firewalls(item):
    waf_client = item[0]
    compartments = item[1:]

    waf_firewalls = []

    for compartment in compartments:
        waf_firewalls_data = get_waf_firewalls_data(waf_client, compartment.id)
        for waf_firewall in waf_firewalls_data:
            waf_firewalls.append(waf_firewall)

    return waf_firewalls
 

def get_managed_instances(item):
    os_management_client = item[0]
    compartments = item[1:]

    managed_instances = []

    for compartment in compartments:
        managed_instance_data = get_managed_instnaces(os_management_client, compartment.id)        
        for instance in managed_instance_data:
            managed_instances.append(instance)

    return managed_instances

