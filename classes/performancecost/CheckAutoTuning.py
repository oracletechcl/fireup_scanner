# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CheckAutoTuning.py
# Description: Implementation of class CheckAutoTuning based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class CheckAutoTuning(ReviewPoint):

    # Class Variables
    __block_volume_objects = []
    __boot_volume_objects = []
    __block_storages = []
    __compartments = []
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
        self.__tenancy = get_tenancy_data(self.__identity, self.config)


    def load_entity(self):

        regions = get_regions_data(self.__identity, self.config)
        block_storage_clients = []
        identity_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            block_storage_clients.append( (get_block_storage_client(region_config, self.signer), region.region_name, region.region_key.lower()) )
            identity_clients.append(get_identity_client(region_config, self.signer))

        availability_domains = ParallelExecutor.get_availability_domains(identity_clients, self.__tenancy.id)

        block_storage_clients_with_ADs = []

        for block_storage_client in block_storage_clients:
            for availability_domain in availability_domains:
                if block_storage_client[1][:-2] in availability_domain.lower() or block_storage_client[2] in availability_domain.lower():
                    block_storage_clients_with_ADs.append( (block_storage_client[0], availability_domain) )

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        self.__block_volume_objects = ParallelExecutor.executor([x[0] for x in block_storage_clients], self.__compartments, ParallelExecutor.get_block_volumes, len(self.__compartments), ParallelExecutor.block_volumes)

        self.__boot_volume_objects = ParallelExecutor.executor(block_storage_clients_with_ADs, self.__compartments, ParallelExecutor.get_boot_volumes, len(self.__compartments), ParallelExecutor.boot_volumes)

        for block_storage in self.__block_volume_objects + self.__boot_volume_objects:
            record = {
                'compartment_id': block_storage.compartment_id,
                'display_name': block_storage.display_name,
                'id': block_storage.id,
                'is_auto_tune_enabled': block_storage.is_auto_tune_enabled,
                'lifecycle_state': block_storage.lifecycle_state,
                'size_in_gbs': block_storage.size_in_gbs,
                'vpus_per_gb': block_storage.vpus_per_gb,
                'time_created': block_storage.time_created,
            }

            self.__block_storages.append(record)

        return self.__block_storages


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for block_storage in self.__block_storages:
            if not block_storage['is_auto_tune_enabled']:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(block_storage)
                dictionary[entry]['failure_cause'].append("Block and boot volumes should have auto tune enabled to reduce cost when not attached")
                dictionary[entry]['mitigations'].append(f"Block storage: \"{block_storage['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, block_storage['compartment_id'])}\" does not have auto tune enabled.")

        return dictionary
