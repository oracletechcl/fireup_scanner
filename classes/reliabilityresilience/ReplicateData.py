# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ReplicateData.py
# Description: Implementation of class ReplicateData based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *


class ReplicateData(ReviewPoint):

    # Class Variables
    __block_volumes = []
    __boot_volumes = []
    __block_volume_replicas = []
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

        # From here on the code is not implemented on abstract class
        self.config = config
        self.signer = signer
        self.__identity = get_identity_client(self.config, self.signer)


    def load_entity(self):
        regions = get_regions_data(self.__identity, self.config)
        block_storage_clients = []
        identity_clients = []

        tenancy = get_tenancy_data(self.__identity, self.config)

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a block_storage and identity_client for each region
            block_storage_clients.append( (get_block_storage_client(region_config, self.signer), region.region_name, region.region_key.lower()) )
            identity_clients.append(get_identity_client(region_config, self.signer))

        # Retrieve all availability domains
        availability_domains = get_availability_domains(identity_clients, tenancy.id)

        block_storage_clients_with_ADs = []

        for block_storage_client in block_storage_clients:
            for availability_domain in availability_domains:
                if block_storage_client[1][:-2] in availability_domain.lower() or block_storage_client[2] in availability_domain.lower():
                    block_storage_clients_with_ADs.append( (block_storage_client[0], availability_domain) )

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__block_volumes = parallel_executor([x[0] for x in block_storage_clients], compartments, self.__search_block_volumes, len(compartments), "__block_volumes")

        # TODO: Should boot volumes be checked??
        # self.__boot_volumes = parallel_executor(block_storage_clients_with_ADs, compartments, self.__search_boot_volumes, len(compartments), "__boot_volumes")

        if len(self.__block_volumes) > 0:
            self.__block_volume_replicas = parallel_executor(block_storage_clients_with_ADs, compartments, self.__search_for_block_volume_replicas, len(compartments), "__block_volume_replicas")

        return self.__block_volume_replicas


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        debug_with_date(self.__block_volume_replicas[0])
        debug_with_date(len(self.__block_volume_replicas))

        # for block_storage in self.__storages_with_no_replication:
        #     dictionary[entry]['status'] = False
        #     dictionary[entry]['findings'].append(block_storage)
        #     dictionary[entry]['failure_cause'].append('Each block storages should have a backup policy.')
        #     dictionary[entry]['mitigations'].append('Make sure block storage '+str(block_storage['display_name'])+' has a backup policy assigned to it.')

        return dictionary

    
    def __search_block_volumes(self, item):
        block_storage_client = item[0]
        compartments = item[1:]

        block_volumes = []

        for compartment in compartments:
            block_volume_data = get_block_volume_data(block_storage_client, compartment.id)
            for block_volume in block_volume_data:
                record = {
                    'availability_domain': block_volume.availability_domain,
                    'block_volume_replicas': block_volume.block_volume_replicas,
                    'boot_volume_replicas': '',
                    'compartment_id': block_volume.compartment_id,
                    'display_name': block_volume.display_name,
                    'id': block_volume.id,
                    'image_id': '',
                    'is_auto_tune_enabled': block_volume.is_auto_tune_enabled,
                    'is_hydrated': block_volume.is_hydrated,
                    'kms_key_id': block_volume.kms_key_id,
                    'lifecycle_state': block_volume.lifecycle_state,
                    'size_in_gbs': block_volume.size_in_gbs,
                    'volume_group_id': block_volume.volume_group_id,
                    'vpus_per_gb': block_volume.vpus_per_gb,
                    'time_created': block_volume.time_created,
                    'metered_bytes': '',
                    'is_clone_parent': '',
                    'lifecycle_details': '',
                    'source_details': '',
                }

                block_volumes.append(record)

        return block_volumes


    def __search_boot_volumes(self, item):
        block_storage_client = item[0][0]
        availability_domain = item[0][1]
        compartments = item[1:]

        boot_volumes = []

        for compartment in compartments:
            boot_volume_data = get_boot_volume_data(block_storage_client, availability_domain, compartment.id)
            for boot_volume in boot_volume_data:
                record = {
                    'availability_domain': boot_volume.availability_domain,
                    'block_volume_replicas': '',
                    'boot_volume_replicas': boot_volume.boot_volume_replicas,
                    'compartment_id': boot_volume.compartment_id,
                    'display_name': boot_volume.display_name,
                    'id': boot_volume.id,
                    'image_id': boot_volume.image_id,
                    'is_auto_tune_enabled': boot_volume.is_auto_tune_enabled,
                    'is_hydrated': boot_volume.is_hydrated,
                    'kms_key_id': boot_volume.kms_key_id,
                    'lifecycle_state': boot_volume.lifecycle_state,
                    'size_in_gbs': boot_volume.size_in_gbs,
                    'volume_group_id': boot_volume.volume_group_id,
                    'vpus_per_gb': boot_volume.vpus_per_gb,
                    'time_created': boot_volume.time_created,
                    'metered_bytes': '',
                    'is_clone_parent': '',
                    'lifecycle_details': '',
                    'source_details': '',
                }

                boot_volumes.append(record)

        return boot_volumes


    def __search_for_block_volume_replicas(self, item):
        block_storage_client = item[0][0]
        availability_domain = item[0][1]
        compartments = item[1:]

        block_volume_replicas = []

        for compartment in compartments:
            block_volume_replica_data = get_block_volume_replica_data(block_storage_client, availability_domain, compartment.id)
            for block_volume_replica in block_volume_replica_data:
                record = {
                    'availability_domain': block_volume_replica.availability_domain,
                    'block_volume_id': block_volume_replica.block_volume_id,
                    'compartment_id': block_volume_replica.compartment_id,
                    'defined_tags': block_volume_replica.defined_tags,
                    'display_name': block_volume_replica.display_name,
                    'id': block_volume_replica.id,
                    'lifecycle_state': block_volume_replica.lifecycle_state,
                    'size_in_gbs': block_volume_replica.size_in_gbs,
                    'time_created': block_volume_replica.time_created,
                }

                block_volume_replicas.append(record)

        return block_volume_replicas
