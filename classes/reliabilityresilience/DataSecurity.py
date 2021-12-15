# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# DataSecurity.py
# Description: Implementation of class DataSecurity based on abstract

from datetime import datetime, timedelta
from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *


class DataSecurity(ReviewPoint):

    # Class Variables
    __instances = []
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
        compute_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            compute_clients.append(get_compute_client(region_config, self.signer))

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        debug_with_date('start')
        self.__instances = parallel_executor(compute_clients, compartments, self.__search_for_computes, len(compartments), "__instances")
        debug_with_date('stop')

        return self.__instances


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for instance in self.__instances:
            if not instance['launch_options'].is_pv_encryption_in_transit_enabled:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(instance)
                dictionary[entry]['mitigations'].append(f"Enabled in-transit encryption for instance: {instance['display_name']}")
                dictionary[entry]['failure_cause'].append('Instances detected without in-transit encryption between boot volume and instance.')

        return dictionary

    
    def __search_for_computes(self, item):
        compute_client = item[0]
        compartments = item[1:]

        instances = []

        for compartment in compartments:
            instance_data = get_instance_data(compute_client, compartment.id)
            for instance in instance_data:
                if instance.lifecycle_state != "TERMINATED":
                    record = {
                        'id': instance.id,
                        'display_name': instance.display_name,
                        'compartment_id': instance.compartment_id,
                        'availability_config': instance.availability_config,
                        'availability_domain': instance.availability_domain,
                        'fault_domain': instance.fault_domain,
                        'image_id': instance.image_id,
                        'launch_options': instance.launch_options,
                        'lifecycle_state': instance.lifecycle_state,
                        'shape': instance.shape,
                        'shape_config': instance.shape_config,
                        'time_created': instance.time_created,
                    }

                    instances.append(record)

        return instances
