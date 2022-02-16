# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ReplicateData.py
# Description: Implementation of class ReplicateData based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class ReplicateData(ReviewPoint):

    # Class Variables
    __block_volumes_objects = []
    __boot_volumes_objects = []
    __block_storage_dicts = []
    __block_volume_replicas_objects = []
    __boot_volume_replicas_objects = []
    __block_storage_replica_ids = []
    __bucket_objects = []
    __bucket_dicts = []
    __autonomous_database_objects = []
    __autonomous_database_dicts = []
    __identity = None
    __compartments = []


    def __init__(self,
                entry:str, 
                area:str, 
                sub_area:str, 
                review_point: str, 
                status:bool, 
                failure_cause:list, 
                findings:list, 
                mitigations:list, 
                fireup_mapping:list,
                config, 
                signer):
        self.entry = entry
        self.area = area
        self.sub_area = sub_area
        self.review_point = review_point
        self.status = status
        self.failure_cause = failure_cause
        self.findings = findings
        self.mitigations = mitigations
        self.fireup_mapping = fireup_mapping

        # From here on the code is not implemented on abstract class
        self.config = config
        self.signer = signer
        self.__identity = get_identity_client(self.config, self.signer)


    def load_entity(self):
        regions = get_regions_data(self.__identity, self.config)
        block_storage_clients = []
        identity_clients = []
        object_storage_clients = []
        database_clients = []

        tenancy = get_tenancy_data(self.__identity, self.config)

        namespace = get_object_storage_client(self.config, self.signer).get_namespace().data

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create clients for each region
            block_storage_clients.append( (get_block_storage_client(region_config, self.signer), region.region_name, region.region_key.lower()) )
            identity_clients.append(get_identity_client(region_config, self.signer))
            object_storage_clients.append( (get_object_storage_client(region_config, self.signer), namespace) )
            database_clients.append(get_database_client(region_config, self.signer))

        # Retrieve all availability domains
        availability_domains = ParallelExecutor.get_availability_domains(identity_clients, tenancy.id)

        block_storage_clients_with_ADs = []

        for block_storage_client in block_storage_clients:
            for availability_domain in availability_domains:
                if block_storage_client[1][:-2] in availability_domain.lower() or block_storage_client[2] in availability_domain.lower():
                    block_storage_clients_with_ADs.append( (block_storage_client[0], availability_domain) )

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, tenancy.id))

        self.__block_volumes_objects = ParallelExecutor.executor([x[0] for x in block_storage_clients], self.__compartments, ParallelExecutor.get_block_volumes, len(self.__compartments), ParallelExecutor.block_volumes)

        self.__boot_volumes_objects = ParallelExecutor.executor(block_storage_clients_with_ADs, self.__compartments, ParallelExecutor.get_boot_volumes, len(self.__compartments), ParallelExecutor.boot_volumes)

        if len(self.__block_volumes_objects) > 0:
            self.__block_volume_replicas_objects = ParallelExecutor.executor(block_storage_clients_with_ADs, self.__compartments, ParallelExecutor.get_block_volume_replicas, len(self.__compartments), ParallelExecutor.block_volume_replicas)

        if len(self.__boot_volumes_objects) > 0:
            self.__boot_volume_replicas_objects = ParallelExecutor.executor(block_storage_clients_with_ADs, self.__compartments, ParallelExecutor.get_boot_volume_replicas, len(self.__compartments), ParallelExecutor.boot_volume_replicas)

        for block_storage in self.__block_volumes_objects + self.__boot_volumes_objects:
            record = {
                'compartment_id': block_storage.compartment_id,
                'display_name': block_storage.display_name,
                'id': block_storage.id,
                'lifecycle_state': block_storage.lifecycle_state,
                'size_in_gbs': block_storage.size_in_gbs,
                'vpus_per_gb': block_storage.vpus_per_gb,
                'region': block_storage.id.split('.')[3]
            }
            self.__block_storage_dicts.append(record)

        for block_storage_replica in self.__block_volume_replicas_objects + self.__boot_volume_replicas_objects:
            if hasattr(block_storage_replica, "block_volume_id"):
                self.__block_storage_replica_ids.append(block_storage_replica.block_volume_id)
            if hasattr(block_storage_replica, "boot_volume_id"):
                self.__block_storage_replica_ids.append(block_storage_replica.boot_volume_id)
        
        self.__bucket_objects = ParallelExecutor.executor(object_storage_clients, self.__compartments, ParallelExecutor.get_buckets, len(self.__compartments), ParallelExecutor.buckets)

        for extended_bucket_data in self.__bucket_objects:
            record = {
                'compartment_id': extended_bucket_data.compartment_id,
                'display_name': extended_bucket_data.name,
                'id': extended_bucket_data.id,
                'is_read_only': extended_bucket_data.is_read_only,
                'replication_enabled': extended_bucket_data.replication_enabled,
                'region': extended_bucket_data.id.split('.')[3]
            }
            self.__bucket_dicts.append(record)

        self.__autonomous_database_objects = ParallelExecutor.executor(database_clients, self.__compartments, ParallelExecutor.get_autonomous_databases, len(self.__compartments), ParallelExecutor.autonomous_databases)

        for adb in self.__autonomous_database_objects:
            record = {
                'display_name': adb.display_name,
                'dataguard_region_type': adb.dataguard_region_type,
                'compartment_id': adb.compartment_id,
                'id': adb.id,
                'region': adb.id.split('.')[3]
            }
            self.__autonomous_database_dicts.append(record)


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for block_storage in self.__block_storage_dicts:
            if block_storage['id'] not in self.__block_storage_replica_ids:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(block_storage)
                dictionary[entry]['failure_cause'].append("Each block storages should be replicated to a disaster recovery region.")
                dictionary[entry]['mitigations'].append(f"Make sure block storage \"{block_storage['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, block_storage['compartment_id'])}\" and region: \"{block_storage['region']}\" is replicated to a disaster recovery region.")

        
        for bucket in self.__bucket_dicts:
            if not bucket['is_read_only'] and not bucket['replication_enabled']:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(bucket)
                dictionary[entry]['failure_cause'].append("Each bucket should be replicated to a disaster recovery region.")
                dictionary[entry]['mitigations'].append(f"Make sure bucket \"{bucket['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, bucket['compartment_id'])}\" and region: \"{bucket['region']}\" is replicated to a disaster recovery region.")


        for adb in self.__autonomous_database_dicts:
            if adb['dataguard_region_type'] == None:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(adb)
                dictionary[entry]['failure_cause'].append("Each autonomous database should have datagaurd enabled.")
                dictionary[entry]['mitigations'].append(f"Make sure autonomous database \"{adb['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, adb['compartment_id'])}\" and region: \"{adb['region']}\" has dataguard enabled.")

        return dictionary
