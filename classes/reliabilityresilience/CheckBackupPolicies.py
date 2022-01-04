# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CheckBackupPolicies.py
# Description: Implementation of class CheckBackupPolicies based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *


class CheckBackupPolicies(ReviewPoint):

    # Class Variables
    __block_volume_objects = []
    __boot_volume_objects = []
    __storages_with_no_policy = []
    __block_storages_with_no_policy_dicts = []
    __file_system_objects = []
    __file_systems_with_no_snapshots = []
    __file_systems_with_no_snapshots_dicts = []
    __identity = None

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

        # From here on is the code is not implemented on abstract class
        self.config = config
        self.signer = signer
        self.__identity = get_identity_client(self.config, self.signer)


    def load_entity(self):
        regions = get_regions_data(self.__identity, self.config)
        block_storage_clients = []
        file_storage_clients = []
        identity_clients = []

        tenancy = get_tenancy_data(self.__identity, self.config)

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a block_storage and identity_client for each region
            block_storage_clients.append( (get_block_storage_client(region_config, self.signer), region.region_name, region.region_key.lower()) )
            file_storage_clients.append( (get_file_storage_client(region_config, self.signer), region.region_name, region.region_key.lower()) )
            identity_clients.append(get_identity_client(region_config, self.signer))

        # Retrieve all availability domains
        availability_domains = ParallelExecutor.get_availability_domains(identity_clients, tenancy.id)

        block_storage_clients_with_ADs = []
        file_system_clients_with_ADs = []

        for block_storage_client, file_storage_client in zip(block_storage_clients, file_storage_clients):
            for availability_domain in availability_domains:
                if block_storage_client[1][:-2] in availability_domain.lower() or block_storage_client[2] in availability_domain.lower():
                    block_storage_clients_with_ADs.append( (block_storage_client[0], availability_domain) )
                if file_storage_client[1][:-2] in availability_domain.lower() or file_storage_client[2] in availability_domain.lower():
                    file_system_clients_with_ADs.append( (file_storage_client[0], availability_domain) )

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__block_volume_objects = ParallelExecutor.executor([x[0] for x in block_storage_clients], compartments, ParallelExecutor.get_block_volumes, len(compartments), ParallelExecutor.block_volumes)

        self.__boot_volume_objects = ParallelExecutor.executor(block_storage_clients_with_ADs, compartments, ParallelExecutor.get_boot_volumes, len(compartments), ParallelExecutor.boot_volumes)

        if len(self.__block_volume_objects + self.__boot_volume_objects) > 0:
            self.__storages_with_no_policy = ParallelExecutor.executor(block_storage_clients, self.__block_volume_objects + self.__boot_volume_objects, ParallelExecutor.get_block_storages_with_no_policy, len(self.__block_volume_objects + self.__boot_volume_objects), ParallelExecutor.storages_with_no_policy)

        for block_storage in self.__storages_with_no_policy:
            if "bootvolume" in block_storage.id:
                record = {
                    'availability_domain': block_storage.availability_domain,
                    'compartment_id': block_storage.compartment_id,
                    'display_name': block_storage.display_name,
                    'id': block_storage.id,
                    'image_id': block_storage.image_id,
                    'is_auto_tune_enabled': block_storage.is_auto_tune_enabled,
                    'is_hydrated': block_storage.is_hydrated,
                    'kms_key_id': block_storage.kms_key_id,
                    'lifecycle_state': block_storage.lifecycle_state,
                    'size_in_gbs': block_storage.size_in_gbs,
                    'volume_group_id': block_storage.volume_group_id,
                    'vpus_per_gb': block_storage.vpus_per_gb,
                    'time_created': block_storage.time_created,
                    'metered_bytes': '',
                    'is_clone_parent': '',
                    'lifecycle_details': '',
                    'source_details': '',
                }
            else:
                record = {
                    'availability_domain': block_storage.availability_domain,
                    'compartment_id': block_storage.compartment_id,
                    'display_name': block_storage.display_name,
                    'id': block_storage.id,
                    'image_id': '',
                    'is_auto_tune_enabled': block_storage.is_auto_tune_enabled,
                    'is_hydrated': block_storage.is_hydrated,
                    'kms_key_id': block_storage.kms_key_id,
                    'lifecycle_state': block_storage.lifecycle_state,
                    'size_in_gbs': block_storage.size_in_gbs,
                    'volume_group_id': block_storage.volume_group_id,
                    'vpus_per_gb': block_storage.vpus_per_gb,
                    'time_created': block_storage.time_created,
                    'metered_bytes': '',
                    'is_clone_parent': '',
                    'lifecycle_details': '',
                    'source_details': '',
                }
            
            self.__block_storages_with_no_policy_dicts.append(record)

        self.__file_system_objects = ParallelExecutor.executor(file_system_clients_with_ADs, compartments, ParallelExecutor.get_file_systems, len(compartments), ParallelExecutor.file_systems)

        if len(self.__file_system_objects) > 0:
            self.__file_systems_with_no_snapshots = ParallelExecutor.executor(file_storage_clients, self.__file_system_objects, ParallelExecutor.get_file_systems_with_no_snapshots, len(self.__file_system_objects), ParallelExecutor.file_systems_with_no_snapshots)

        for file_system in self.__file_systems_with_no_snapshots:
            record = {
                'availability_domain': file_system.availability_domain,
                'compartment_id': file_system.compartment_id,
                'id': file_system.id,
                'display_name': file_system.display_name,
                'is_clone_parent': file_system.is_clone_parent,
                'is_hydrated': file_system.is_hydrated,
                'kms_key_id': file_system.kms_key_id,
                'lifecycle_state': file_system.lifecycle_state,
                'lifecycle_details': file_system.lifecycle_details,
                'metered_bytes': file_system.metered_bytes,
                'source_details': file_system.source_details,
                'time_created': file_system.time_created,
                'vpus_per_gb': '',
                'size_in_gbs': '',
                'is_auto_tune_enabled': '',
                'image_id': '',
                'volume_group_id': '',
            }
            self.__file_systems_with_no_snapshots_dicts.append(record)

        return self.__block_storages_with_no_policy_dicts, self.__file_systems_with_no_snapshots_dicts

    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for block_storage in self.__block_storages_with_no_policy_dicts:
            dictionary[entry]['status'] = False
            dictionary[entry]['findings'].append(block_storage)
            dictionary[entry]['failure_cause'].append('Each block storages should have a backup policy.')
            dictionary[entry]['mitigations'].append('Make sure block storage '+str(block_storage['display_name'])+' has a backup policy assigned to it.')

        for file_system in self.__file_systems_with_no_snapshots_dicts:
            dictionary[entry]['status'] = False
            dictionary[entry]['findings'].append(file_system)
            dictionary[entry]['failure_cause'].append('Each file system should have snapshots within the last week.')
            dictionary[entry]['mitigations'].append('Make sure file system '+str(file_system['display_name'])+' is creating a snapshot weekly.')

        return dictionary
