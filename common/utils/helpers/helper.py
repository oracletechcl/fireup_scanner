# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Helper.py
# Description: Helper functions for OCI Python SDK

import oci
from common.utils.tokenizer.signer import *
from common.utils.formatter.printer import *


def get_config_and_signer():
    try:
       config, signer = create_signer("", False, False)
    except Exception as e:
        raise RuntimeError("Failed to load configuration: {}".format(e))
    return config, signer

def get_identity_client(config, signer):
    try:
        identity_client = oci.identity.IdentityClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create identity client: {}".format(e))
    return identity_client

def get_audit_client(config, signer):
    try:
        audit_client = oci.audit.AuditClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create audit client: {}".format(e))
    return audit_client

def get_cloud_guard_client(config, signer):
    try:
        cloud_guard_client = oci.cloudguard.CloudGuardClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create cloud guard client: {}".format(e))
    return cloud_guard_client

def get_resource_search_client(config, signer):
    try:
        resource_search_client = oci.resource_search.ResourceSearchClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create resource search client: {}".format(e))
    return resource_search_client

def get_virtual_network_client(config, signer):
    try:
        virtual_network_client = oci.core.VirtualNetworkClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create virtual network client: {}".format(e))
    return virtual_network_client

def get_events_client(config, signer):
    try:
        events_client = oci.events.EventsClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create events client: {}".format(e))
    return events_client

def get_logging_management_client(config, signer):
    try:
        logging_management_client = oci.logging.LoggingManagementClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create logging management client: {}".format(e))
    return logging_management_client

def get_object_storage_client(config, signer):
    try:
        object_storage_client = oci.object_storage.ObjectStorageClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create object storage client: {}".format(e))
    return object_storage_client

def get_kms_valult_client(config, signer):
    try:
        kms_valult_client = oci.key_management.KmsVaultClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create kms vault client: {}".format(e))
    return kms_valult_client

def get_notification_data_plane_client(config, signer):
    try:
        notification_data_plane_client = oci.ons.NotificationDataPlaneClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create notification data client: {}".format(e))
    return notification_data_plane_client

def get_load_balancer_client(config, signer):
    try:
        load_balancer_client = oci.load_balancer.LoadBalancerClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create load balancer client: {}".format(e))
    return load_balancer_client

def get_network_load_balancer_client(config, signer):
    try:
        network_load_balancer_client = oci.network_load_balancer.NetworkLoadBalancerClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create network load balancer client: {}".format(e))
    return network_load_balancer_client

def get_compute_client(config, signer):
    try:
        compute_client = oci.core.ComputeClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create compute client: {}".format(e))
    return compute_client

def get_block_storage_client(config, signer):
    try:
        block_storage_client = oci.core.BlockstorageClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create block storage client: {}".format(e))
    return block_storage_client

def get_file_storage_client(config, signer):
    try:
        file_storage_client = oci.file_storage.FileStorageClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create file storage client: {}".format(e))
    return file_storage_client

def get_object_storage_client(config, signer):
    try:
        object_storage_client = oci.object_storage.ObjectStorageClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create object storage client: {}".format(e))
    return object_storage_client

def get_database_client(config, signer):
    try:
        database_client = oci.database.DatabaseClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create database client: {}".format(e))
    return database_client

def get_mysql_client(config, signer):
    try:
        mysql_client = oci.mysql.DbSystemClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create MySQL client: {}".format(e))
    return mysql_client

def get_mysql_backup_client(config, signer):
    try:
        mysql_backup_client = oci.mysql.DbBackupsClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create MySQL Backup client: {}".format(e))
    return mysql_backup_client

def get_tenancy_data(identity_client, config):
    try:
        tenancy = identity_client.get_tenancy(config["tenancy"]).data
    except Exception as e:
        raise RuntimeError("Failed to get tenancy: {}".format(e))
    return tenancy

def get_regions_data(identity_client, config):
    try:
        regions = identity_client.list_region_subscriptions(config["tenancy"]).data
    except Exception as e:
        raise RuntimeError("Failed to get regions: {}".format(e))
    return regions

def get_home_region(identity_client, config):
    regions = get_regions_data(identity_client, config)
    for region in regions:
        if region.is_home_region:
            return region

def get_compartments_data(identity_client, compartment_id): 
        __identity_client = identity_client
        __compartment_id = compartment_id

        return oci.pagination.list_call_get_all_results(
        __identity_client.list_compartments,
        __compartment_id,
        compartment_id_in_subtree=True,
        lifecycle_state="ACTIVE"
    ).data
    
def get_policies_data(identity_client, compartment_id): 
        __identity_client = identity_client
        __compartment_id = compartment_id

        return oci.pagination.list_call_get_all_results(
        __identity_client.list_policies,
        __compartment_id
    ).data


def get_user_data(identity_client, compartment_id): 
        __identity_client = identity_client
        __compartment_id = compartment_id

        return oci.pagination.list_call_get_all_results(
        __identity_client.list_users,
        compartment_id
    ).data

def get_user_api_key_data(identity_client, user_id): 
        __identity_client = identity_client
        __user_id = user_id

        return oci.pagination.list_call_get_all_results(
        __identity_client.list_api_keys,
        user_id
    ).data

def get_auth_token_data(identity_client, user_id): 
        __identity_client = identity_client
        __user_id = user_id

        return oci.pagination.list_call_get_all_results(
        __identity_client.list_auth_tokens,
        user_id
    ).data

def get_objectstorage_namespace_data(objectstorage_client):
    try:
        objectstorage_namespace_data = objectstorage_client.get_namespace().data
    except Exception as e:
        raise RuntimeError("Failed to get object storage namespace data: {}".format(e))
    return objectstorage_namespace_data

def get_bucket_per_compartment(objectstorage_client, compartment_id, namespace):
    try:
        bucket_per_compartment = oci.pagination.list_call_get_all_results(
            objectstorage_client.list_buckets,
            namespace,
            compartment_id
        )
    except Exception as e:
        raise RuntimeError("Failed to get bucket per compartment: {}".format(e))
    return bucket_per_compartment


def get_vcn_data(network_client, compartment_id): 
        __network_client = network_client

        return oci.pagination.list_call_get_all_results(
        __network_client.list_vcns,
        compartment_id
    ).data

def get_api_key_data(identity_client, user_id):
    try:
        api_key_data = oci.pagination.list_call_get_all_results(
            identity_client.list_api_keys,
            user_id
        ).data
    except Exception as e:
        raise RuntimeError("Failed to get api key data: {}".format(e))
    return api_key_data

def get_load_balancer_data(load_balancer_client, compartment_id): 
        __load_balancer_client = load_balancer_client

        return oci.pagination.list_call_get_all_results(
        __load_balancer_client.list_load_balancers,
        compartment_id
    ).data

def get_network_load_balancer_data(network_load_balancer_client, compartment_id): 
        __network_load_balancer_client = network_load_balancer_client

        return oci.pagination.list_call_get_all_results(
        __network_load_balancer_client.list_network_load_balancers,
        compartment_id
    ).data

def get_dynamic_group_data(identity_client, compartment_id): 
        __identity_client = identity_client
        __compartment_id = compartment_id

        return oci.pagination.list_call_get_all_results(
        __identity_client.list_dynamic_groups,
        __compartment_id,
    ).data

def get_instance_data(compute_client, compartment_ocid):
    return oci.pagination.list_call_get_all_results(
        compute_client.list_instances,
        compartment_ocid,
    ).data

def get_security_list_data(network_client, compartment_id):
    return oci.pagination.list_call_get_all_results(
        network_client.list_security_lists,
        compartment_id
    ).data        
    
def get_block_volume_data(block_storage_client, compartment_id): 

        return oci.pagination.list_call_get_all_results(
        block_storage_client.list_volumes,
        compartment_id
    ).data

def get_block_volume_replica_data(block_storage_client, availability_domain, compartment_id): 

        return oci.pagination.list_call_get_all_results(
        block_storage_client.list_block_volume_replicas,
        availability_domain,
        compartment_id
    ).data

def get_boot_volume_data(block_storage_client, availability_domain, compartment_id): 

        return oci.pagination.list_call_get_all_results(
        block_storage_client.list_boot_volumes,
        availability_domain,
        compartment_id
    ).data

def get_boot_volume_replica_data(block_storage_client, availability_domain, compartment_id): 

        return oci.pagination.list_call_get_all_results(
        block_storage_client.list_boot_volume_replicas,
        availability_domain,
        compartment_id
    ).data

def get_bucket_data(object_storage_client, namespace, compartment_id):

    return oci.pagination.list_call_get_all_results(
        object_storage_client.list_buckets,
        str(namespace),
        compartment_id
    ).data

def get_file_system_data(file_storage_client, compartment_id, availability_domain):
    
    return oci.pagination.list_call_get_all_results(
        file_storage_client.list_file_systems,
        compartment_id,
        availability_domain
    ).data

def get_db_system_data(database_client, compartment_id):
    
    return oci.pagination.list_call_get_all_results(
        database_client.list_db_systems,
        compartment_id,
    ).data

def get_db_system_home_data(database_client, compartment_id):
    
    return oci.pagination.list_call_get_all_results(
        database_client.list_db_homes,
        compartment_id,
    ).data

def get_auto_db_data(database_client, compartment_id):
    
    return oci.pagination.list_call_get_all_results(
        database_client.list_autonomous_databases,
        compartment_id,
    ).data

def get_db_system_backup_data(database_client, compartment_id):

    return oci.pagination.list_call_get_all_results(
        database_client.list_backups,
        compartment_id=compartment_id,
    ).data

def get_mysql_backup_data(mysql_client, compartment_id):
    
    return oci.pagination.list_call_get_all_results(
        mysql_client.list_backups,
        compartment_id,
    ).data

def get_quotas_client(config, signer):
    try:
        quotas_client = oci.limits.QuotasClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create quotas client: {}".format(e))
    return quotas_client

def list_quota_data(quotas_client, tenancy_id): 
        __quotas_client = quotas_client
        __tenancy_id = tenancy_id

        return oci.pagination.list_call_get_all_results(
        __quotas_client.list_quotas,
        __tenancy_id
    ).data

def get_subnets_per_compartment_data(network_client, compartment_id):
    return oci.pagination.list_call_get_all_results(
        network_client.list_subnets,
        compartment_id, 
    ).data

def get_compartment_name(compartments, compartment_id):
    for compartment in compartments:
        if compartment_id == compartment.id:
            return compartment.name
    return None

def get_nsg_rules_data(network_client, nsg_id):
    return oci.pagination.list_call_get_all_results(
        network_client.list_network_security_group_security_rules,
        nsg_id
    ).data

def get_max_security_zone_data(identity_client, compartment_id):
    path_params = {
        "compartmentId": compartment_id
    }
    header_params = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    return identity_client.base_client.call_api(
        resource_path="/compartments/{compartmentId}?verboseLevel=securityZone",
        method="GET",
        path_params=path_params,
        header_params=header_params,
        response_type="json").data

def get_limits_client(config, signer):
    try:
        limits_client = oci.limits.LimitsClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create limits client: {}".format(e))
    return limits_client

def list_limit_value_data(limits_client, compartment_id, service_name): 
    return oci.pagination.list_call_get_all_results(
        limits_client.list_limit_values,
        compartment_id,
        service_name
    ).data

def list_limit_definition_data(limits_client, compartment_id, service_name): 
    return oci.pagination.list_call_get_all_results(
        limits_client.list_limit_definitions,
        compartment_id=compartment_id,
        service_name=service_name
    ).data

