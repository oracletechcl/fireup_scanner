# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Helper.py
# Description: Helper functions for OCI Python SDK

import oci
from common.utils.tokenizer.signer import *
from common.utils.formatter.printer import *

# Custom retry strategy which is based on DEFAULT_RETRY_STRATEGY with additional service error checks
CUSTOM_RETRY_STRATEGY = oci.retry.RetryStrategyBuilder().add_max_attempts(max_attempts=8) \
                                                        .add_total_elapsed_time(total_elapsed_time_seconds=600) \
                                                        .add_service_error_check(service_error_retry_config=  {   
                                                                                                            -1: [],
                                                                                                            409: ['IncorrectState'],
                                                                                                            429: [],
                                                                                                            500: [404], 
                                                                                                            500: [429] 
                                                                                                        },
                                                                                service_error_retry_on_any_5xx=True) \
                                                        .get_retry_strategy()


def get_config_and_signer():
    try:
       config, signer = create_signer("", False, False)
    except Exception as e:
        raise RuntimeError("Failed to load configuration: " + e)
    return config, signer


def get_compute_client(config, signer):
    try:
        compute_client = oci.core.ComputeClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create compute client: " + e)
    return compute_client


def get_identity_client(config, signer):
    try:
        identity_client = oci.identity.IdentityClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create identity client: " + e)
    return identity_client


def get_audit_client(config, signer):
    try:
        audit_client = oci.audit.AuditClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create audit client: " + e)
    return audit_client


def get_cloud_guard_client(config, signer):
    try:
        cloud_guard_client = oci.cloud_guard.CloudGuardClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create cloud guard client: " + e)
    return cloud_guard_client


def get_resource_search_client(config, signer):
    try:
        resource_search_client = oci.resource_search.ResourceSearchClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create resource search client: " + e)
    return resource_search_client


def get_virtual_network_client(config, signer):
    try:
        virtual_network_client = oci.core.VirtualNetworkClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create virtual network client: " + e)
    return virtual_network_client


def get_events_client(config, signer):
    try:
        events_client = oci.events.EventsClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create events client: " + e)
    return events_client


def get_logging_management_client(config, signer):
    try:
        logging_management_client = oci.logging.LoggingManagementClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create logging management client: " + e)
    return logging_management_client


def get_object_storage_client(config, signer):
    try:
        object_storage_client = oci.object_storage.ObjectStorageClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create object storage client: " + e)
    return object_storage_client


def get_kms_valult_client(config, signer):
    try:
        kms_valult_client = oci.key_management.KmsVaultClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create kms vault client: " + e)
    return kms_valult_client

def get_vaults_client(config, signer):
    try:
        vaults_client = oci.vault.VaultsClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create vault client: " + e)
    return vaults_client


def get_kms_management_client(config, service_endpoint, signer):
    try:
        kms_management_client = oci.key_management.KmsManagementClient(config, service_endpoint, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create kms vault client: " + e)
    return kms_management_client


def get_notification_data_plane_client(config, signer):
    try:
        notification_data_plane_client = oci.ons.NotificationDataPlaneClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create notification data client: " + e)
    return notification_data_plane_client


def get_load_balancer_client(config, signer):
    try:
        load_balancer_client = oci.load_balancer.LoadBalancerClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create load balancer client: " + e)
    return load_balancer_client


def get_network_load_balancer_client(config, signer):
    try:
        network_load_balancer_client = oci.network_load_balancer.NetworkLoadBalancerClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create network load balancer client: " + e)
    return network_load_balancer_client


def get_compute_client(config, signer):
    try:
        compute_client = oci.core.ComputeClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create compute client: " + e)
    return compute_client


def get_block_storage_client(config, signer):
    try:
        block_storage_client = oci.core.BlockstorageClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create block storage client: " + e)
    return block_storage_client


def get_file_storage_client(config, signer):
    try:
        file_storage_client = oci.file_storage.FileStorageClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create file storage client: " + e)
    return file_storage_client


def get_object_storage_client(config, signer):
    try:
        object_storage_client = oci.object_storage.ObjectStorageClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create object storage client: " + e)
    return object_storage_client


def get_database_client(config, signer):
    try:
        database_client = oci.database.DatabaseClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create database client: " + e)
    return database_client


def get_mysql_client(config, signer):
    try:
        mysql_client = oci.mysql.DbSystemClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create MySQL client: " + e)
    return mysql_client


def get_mysql_backup_client(config, signer):
    try:
        mysql_backup_client = oci.mysql.DbBackupsClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create MySQL Backup client: " + e)
    return mysql_backup_client


def get_autoscaling_client(config, signer):
    try:
        autoscaling_client = oci.autoscaling.AutoScalingClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create Autoscaling client: " + e)
    return autoscaling_client


def get_compute_management_client(config, signer):
    try:
        compute_management_client= oci.core.ComputeManagementClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create Compute Management client: " + e)
    return compute_management_client


def get_service_client(config, signer):
    try:
        service_client = oci.sch.ServiceConnectorClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create MySQL Backup client: " + e)
    return service_client


def get_operations_insights_client(config, signer):
    try:
        operations_insights_client = oci.opsi.OperationsInsightsClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create operations insights client: " + e)
    return operations_insights_client


def get_functions_management_client(config, signer):
    try:
        functions_management_client = oci.functions.FunctionsManagementClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create functions management client: " + e)
    return functions_management_client


def get_quotas_client(config, signer):
    try:
        quotas_client = oci.limits.QuotasClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create quotas client: " + e)
    return quotas_client


def get_limits_client(config, signer):
    try:
        limits_client = oci.limits.LimitsClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create limits client: " + e)
    return limits_client


def get_dns_client(config, signer):
    try:
        dns_client = oci.dns.DnsClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create DNS client: " + e)
    return dns_client


def get_container_engine_client(config, signer):
    try:
        container_engine_client = oci.container_engine.ContainerEngineClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create container engine client: " + e)
    return container_engine_client


def get_budget_client(config, signer):
    try:
        budget_client = oci.budget.BudgetClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create budget client: " + e)
    return budget_client


def get_monitoring_client(config, signer):
    try:
        monitoring_client = oci.monitoring.MonitoringClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create Monitoring client: " + e)
    return monitoring_client


def get_notification_control_plane_client(config, signer):
    try:
        notification_control_plane_client = oci.ons.NotificationControlPlaneClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create Notification client: " + e)
    return notification_control_plane_client


def get_data_safe_client(config, signer):
    try:
        data_safe_client = oci.data_safe.DataSafeClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create Data Safe client: " + e)
    return data_safe_client

def get_resource_manager_client(config, signer):
    try:
        resource_manager_client = oci.resource_manager.ResourceManagerClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create Resource Manager client: " + e)
    return resource_manager_client


def get_waf_client(config, signer):
    try:
        waf_client = oci.waf.WafClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create Web Application Firewall client: " + e)
    return waf_client

  
def get_os_management_client(config, signer):
    try:
        os_management_client = oci.os_management.OsManagementClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create OS Management Client: " + e)
    return os_management_client


def get_tenancy_data(identity_client, config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return identity_client.get_tenancy(
        config["tenancy"],
        retry_strategy=retry_strategy
    ).data


def get_regions_data(identity_client, config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return identity_client.list_region_subscriptions(
        config["tenancy"],
        retry_strategy=retry_strategy
    ).data


def get_cost_tracking_tags(identity_client, root_compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return identity_client.list_cost_tracking_tags(
        root_compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_home_region(identity_client, config):
    regions = get_regions_data(identity_client, config)
    for region in regions:
        if region.is_home_region:
            return region


def get_compartments_data(identity_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        identity_client.list_compartments,
        compartment_id,
        compartment_id_in_subtree=True,
        lifecycle_state="ACTIVE",
        retry_strategy=retry_strategy
    ).data


def get_root_compartment_data(identity_client, tenancy_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return identity_client.get_compartment(
        tenancy_id,
        retry_strategy=retry_strategy
    ).data


def get_policies_data(identity_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY): 
    return oci.pagination.list_call_get_all_results(
        identity_client.list_policies,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_dns_zone_data(dns_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        dns_client.list_zones,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_service_connectors(service_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        service_client.list_service_connectors,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_bucket_retention_rules(object_storage_client, namespace_name,bucket_name, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        object_storage_client.list_retention_rules,
        namespace_name,
        bucket_name,
        retry_strategy=retry_strategy
    ).data


def get_user_data(identity_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY): 
    return oci.pagination.list_call_get_all_results(
        identity_client.list_users,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_user_api_key_data(identity_client, user_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        identity_client.list_api_keys,
        user_id,
        retry_strategy=retry_strategy
    ).data


def get_auth_token_data(identity_client, user_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        identity_client.list_auth_tokens,
        user_id,
        retry_strategy=retry_strategy
    ).data


def get_objectstorage_namespace_data(objectstorage_client, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return objectstorage_client.get_namespace(
        retry_strategy=retry_strategy
    ).data


def get_preauthenticated_requests(objectstorage_client, namespace, bucket_name, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        objectstorage_client.list_preauthenticated_requests,
        namespace,
        bucket_name,
        retry_strategy=retry_strategy
    ).data


def get_vcn_data(network_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY): 
    return oci.pagination.list_call_get_all_results(
        network_client.list_vcns,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_api_key_data(identity_client, user_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        identity_client.list_api_keys,
        user_id,
        retry_strategy=retry_strategy
    ).data


def get_load_balancer_data(load_balancer_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY): 
    return oci.pagination.list_call_get_all_results(
        load_balancer_client.list_load_balancers,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_network_load_balancer_data(network_load_balancer_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_load_balancer_client.list_network_load_balancers,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_network_load_balancer_health_data(network_load_balancer_client, load_balancer_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return  network_load_balancer_client.get_network_load_balancer_health(
        load_balancer_id,
        retry_strategy=retry_strategy
    ).data


def get_load_balancer_health_data(load_balancer_client, load_balancer_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return load_balancer_client.get_load_balancer_health(
        load_balancer_id,
        retry_strategy=retry_strategy
    ).data


def get_dynamic_group_data(identity_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        identity_client.list_dynamic_groups,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_instance_data(compute_client, compartment_ocid, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        compute_client.list_instances,
        compartment_ocid,
        retry_strategy=retry_strategy
    ).data


def get_security_list_data(network_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_client.list_security_lists,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_block_volume_data(block_storage_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY): 
    return oci.pagination.list_call_get_all_results(
        block_storage_client.list_volumes,
        compartment_id,
        retry_strategy=retry_strategy
    ).data

def get_block_volume_replica_data(block_storage_client, availability_domain, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        block_storage_client.list_block_volume_replicas,
        availability_domain,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_boot_volume_data(block_storage_client, availability_domain, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        block_storage_client.list_boot_volumes,
        availability_domain,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_boot_volume_replica_data(block_storage_client, availability_domain, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        block_storage_client.list_boot_volume_replicas,
        availability_domain,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_bucket_data(object_storage_client, namespace, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        object_storage_client.list_buckets,
        namespace,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_file_system_data(file_storage_client, compartment_id, availability_domain, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        file_storage_client.list_file_systems,
        compartment_id,
        availability_domain,
        retry_strategy=retry_strategy
    ).data


def get_mount_target_data(file_storage_client, compartment_id, availability_domain, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        file_storage_client.list_mount_targets,
        compartment_id,
        availability_domain,
        retry_strategy=retry_strategy
    ).data


def get_db_system_data(database_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        database_client.list_db_systems,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_db_system_home_data(database_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        database_client.list_db_homes,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_auto_db_data(database_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        database_client.list_autonomous_databases,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_db_system_backup_data(database_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        database_client.list_backups,
        compartment_id=compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_mysql_backup_data(mysql_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        mysql_client.list_backups,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def list_quota_data(quotas_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
        return oci.pagination.list_call_get_all_results(
        quotas_client.list_quotas,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_quota_policy_data(quota_client, quota_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return quota_client.get_quota(
        quota_id = quota_id,
        retry_strategy=retry_strategy
    ).data


def get_subnets_per_compartment_data(network_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_client.list_subnets,
        compartment_id,
        retry_strategy=retry_strategy
    ).data

def get_subnet_info(network_client, subnet_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return network_client.get_subnet(
        subnet_id,
        retry_strategy=retry_strategy
    ).data

def get_vcn_from_subnet(network_client, vcn_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return network_client.get_vcn(
        vcn_id,
        retry_strategy=retry_strategy
    ).data

def get_compartment_name(compartments, compartment_id):
    for compartment in compartments:
        if compartment_id == compartment.id:
            return compartment.name
    return None

def get_block_volume_name(volumes,volume_id): 
    for volume in volumes:
        if volume.id == volume_id:
            return volume.display_name
    return None


def get_nsg_rules_data(network_client, nsg_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_client.list_network_security_group_security_rules,
        nsg_id,
        retry_strategy=retry_strategy
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
        response_type="json",
    ).data


def get_db_home_patches(database_client, db_home_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        database_client.list_db_home_patches,
        db_home_id,
        retry_strategy=retry_strategy
    ).data


def get_db_home_patch_history(database_client, db_home_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        database_client.list_db_home_patch_history_entries,
        db_home_id,
        retry_strategy=retry_strategy
    ).data


def get_db_system_patch_history(database_client, db_home_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        database_client.list_db_system_patch_history_entries,
        db_home_id,
        retry_strategy=retry_strategy
    ).data


def get_db_system_patch_details(database_client, db_system_id, patch_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return database_client.get_db_system_patch(
        db_system_id, 
        patch_id,
        retry_strategy=retry_strategy
    ).data


def get_db_home_patch_details(database_client, db_home_id, patch_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return database_client.get_db_home_patch(
        db_home_id, 
        patch_id,
        retry_strategy=retry_strategy
    ).data

  
def get_drg_data(network_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_client.list_drgs,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_all_drg_attachments_data(network_client, drg_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_client.get_all_drg_attachments,
        drg_id,
        retry_strategy=retry_strategy
    ).data


def get_drg_attachment_data(network_client, drg_attachment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return network_client.get_drg_attachment(
        drg_attachment_id, 
        retry_strategy=retry_strategy
    ).data


def get_service_gateway_data(network_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_client.list_service_gateways,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_local_peering_gateway_data(network_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_client.list_local_peering_gateways,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_limit_value_data(limits_client, compartment_id, service_name, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        limits_client.list_limit_values,
        compartment_id,
        service_name,
        retry_strategy=retry_strategy
    ).data


def get_limit_definition_data(limits_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        limits_client.list_limit_definitions,
        compartment_id=compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_resource_availability_data(limits_client, service_name, limit_name, compartment_id, availability_domain=None, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return limits_client.get_resource_availability(
        service_name=service_name,
        limit_name=limit_name,
        compartment_id=compartment_id,
        availability_domain=availability_domain,
        retry_strategy=retry_strategy
    ).data


def get_services(limits_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results( 
        limits_client.list_services,
        compartment_id=compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_steering_policy_data(dns_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        dns_client.list_steering_policies,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_oke_cluster_data(container_engine_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        container_engine_client.list_clusters,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_network_sources(identity_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        identity_client.list_network_sources,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_authentication_policy(identity_client, tenancy_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return identity_client.get_authentication_policy(
        tenancy_id,
        retry_strategy=retry_strategy
    ).data    


def get_virtual_circuit_data(network_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_client.list_virtual_circuits,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_budget_data(budget_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        budget_client.list_budgets,
        compartment_id,
        target_type="ALL",
        retry_strategy=retry_strategy
    ).data


def get_budget_alert_rules_data(budget_client, budget_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        budget_client.list_alert_rules,
        budget_id,
        retry_strategy=retry_strategy
    ).data

 
def get_cloud_guard_configuration_data(cloud_guard_client, tenancy_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    try:
        return cloud_guard_client.get_configuration(
            tenancy_id,
            retry_strategy=retry_strategy
        ).data
    except oci.exceptions.ServiceError as exception:
        return exception


def get_autoscaling_configurations_data(autoscaling_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY): 
    return oci.pagination.list_call_get_all_results(
        autoscaling_client.list_auto_scaling_configurations,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_instance_pools_data(compute_management_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY): 
    return oci.pagination.list_call_get_all_results(
        compute_management_client.list_instance_pools,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_audit_configuration_data(audit_client, tenancy_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return audit_client.get_configuration(
        tenancy_id,
        retry_strategy=retry_strategy
    ).data


def get_alarm_data(monitoring_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        monitoring_client.list_alarms,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_metric_data(monitoring_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        monitoring_client.list_metrics,
        compartment_id,
        oci.monitoring.models.ListMetricsDetails(),
        retry_strategy=retry_strategy
    ).data


def get_log_group_data_per_compartment(logging_management_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        logging_management_client.list_log_groups,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_log_data(logging_management_client, log_group_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        logging_management_client.list_logs,
        log_group_id,
        retry_strategy=retry_strategy
    ).data


def get_applications_per_compartment(functions_management_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        functions_management_client.list_applications,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_functions_per_application(functions_management_client, application_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        functions_management_client.list_functions,
        application_id,
        retry_strategy=retry_strategy
    ).data


def get_ip_sec_connections_per_compartment(network_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_client.list_ip_sec_connections,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_ip_sec_connections_tunnels_per_connection(network_client, ipsec_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_client.list_ip_sec_connection_tunnels,
        ipsec_id,
        retry_strategy=retry_strategy
    ).data


def get_event_rules_per_compartment(events_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        events_client.list_rules,
        compartment_id,
        retry_strategy=retry_strategy
    ).data
   

def get_networking_topology_per_compartment(network_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return network_client.get_networking_topology(
        compartment_id,
        query_compartment_subtree=True,
        retry_strategy=retry_strategy
    ).data


def get_cross_connects_per_compartment(network_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_client.list_cross_connects,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def list_operations_insights_warehouses(operations_insights_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return operations_insights_client.list_operations_insights_warehouses(
        compartment_id=compartment_id,
        retry_strategy=retry_strategy
    ).data


def list_awr_hubs(operations_insights_client, operations_insights_warehouse_id, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return operations_insights_client.list_awr_hubs(
        operations_insights_warehouse_id=operations_insights_warehouse_id,
        compartment_id=compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_detector_recipes_by_compartments(cloud_guard_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        cloud_guard_client.list_detector_recipes,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_responder_recipes_by_compartments(cloud_guard_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        cloud_guard_client.list_responder_recipes,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_detector_rules_by_compartment(cloud_guard_client, detector_id, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        cloud_guard_client.list_detector_recipe_detector_rules,
        detector_id,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_responder_rules_by_compartment(cloud_guard_client, responder_id, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        cloud_guard_client.list_responder_recipe_responder_rules,
        responder_id,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_compute_data(compute_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY): 
    return oci.pagination.list_call_get_all_results(
        compute_client.list_instances,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_compute_image_data(comput_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        comput_client.list_images,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_notification_data(notification_control_plane_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        notification_control_plane_client.list_topics,
        compartment_id,
        retry_strategy=retry_strategy
    ).data 

def get_volume_attachments_per_compartment(compute_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        compute_client.list_volume_attachments,
        compartment_id,
        retry_strategy=retry_strategy
    ).data 



def is_cloud_shell():
    # check the current os user running this program. If user is ubuntu or opc return false. Else return true
    if os.getenv("USER") == "ubuntu" or os.getenv("USER") == "opc":
        return False    
    else:
        return True


def list_target_databases_data(data_safe_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        data_safe_client.list_target_databases,
        compartment_id=compartment_id,
        compartment_id_in_subtree=True,
        access_level="ACCESSIBLE",
        lifecycle_state="ACTIVE",
        retry_strategy=retry_strategy
    ).data 


def get_target_database_data(data_safe_client, target_database_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return data_safe_client.get_target_database(
        target_database_id=target_database_id,
        retry_strategy=retry_strategy
    ).data 


def get_kms_key_info(kms_management_client, key_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return kms_management_client.get_key(
        key_id,
        retry_strategy=retry_strategy
    ).data


def get_key_versions(kms_management_client, key_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        kms_management_client.list_key_versions,
        key_id,
        retry_strategy=retry_strategy
    ).data

def get_network_security_groups_data(network_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        network_client.list_network_security_groups,
        compartment_id=compartment_id,
        retry_strategy=retry_strategy
    ).data

def get_resource_manager_jobs_per_compartment(resource_manager_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        resource_manager_client.list_jobs,
        compartment_id = compartment_id,
        retry_strategy=retry_strategy
    ).data


def get_secrets_per_compartment(vaults_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        vaults_client.list_secrets,
        compartment_id,
        retry_strategy=retry_strategy
    ).data

def get_secret_data(vaults_client, secret_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return vaults_client.get_secret(
        secret_id,
        retry_strategy=retry_strategy
    ).data


def get_waf_firewalls_data(waf_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        waf_client.list_web_app_firewalls,
        compartment_id,
        retry_strategy=retry_strategy
    ).data 

 
def get_managed_instnaces(os_management_client, compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY):
    return oci.pagination.list_call_get_all_results(
        os_management_client.list_managed_instances,
        compartment_id,
        retry_strategy=retry_strategy
    ).data


