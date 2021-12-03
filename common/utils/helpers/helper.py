# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Helper.py
# Description: Helper functions for OCI Python SDK

import oci
from common.utils.tokenizer.signer import *
from concurrent import futures
from common.utils.formatter.printer import debug_with_date


__identity_client = None
__network_client = None

__compartment_id = None
__compartments = None

__vcns = []

### LBaasBackends.py Global Variables
# LBaas Clients
__load_balancer_client = None
__network_load_balancer_client = None
# LBaas lists for use with parallel_executor
__load_balancers = []
__network_load_balancers = []

# Rbac.py Global Variables
__policies = []

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

def get_compartments_data(identity_client, compartment_id): 
        __identity_client = identity_client
        __compartment_id = compartment_id

        return oci.pagination.list_call_get_all_results(
        __identity_client.list_compartments,
        __compartment_id,
        compartment_id_in_subtree=True
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

def parallel_executor(dependent_clients:list, independent_iterator:list, fuction_to_execute, threads:int, storage_variable_name:str):

    values = globals()[storage_variable_name]

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
        processes = []

        processes = [executor.submit(
            fuction_to_execute,
            item
            ) 
            for item in items]

        futures.wait(processes)

        for p in processes:
            for value in p.result():
                values.append(value)

    return values
