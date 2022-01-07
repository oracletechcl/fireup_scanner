# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ComputeLimits.py
# Description: Implementation of class ComputeLimits based on abstract

from concurrent import futures
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class ComputeLimits(ReviewPoint):

    # Class Variables
    __limit_data_objects = []
    __limit_value_objects = []
    __limit_definitions_objects = []
    __compute_limits = []
    __non_compliant_compute_limits = dict()
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


    def load_entity(self):

        regions = get_regions_data(self.__identity, self.config)

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        limits_clients = []
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            limits_clients.append(get_limits_client(region_config, self.signer))

        # Specialised parallel execution method for getting the limits in each region
        with futures.ThreadPoolExecutor(len(limits_clients)) as executor:
            processes = [
                executor.submit(get_limits_data, limits_client, tenancy.id)
                for limits_client in limits_clients
            ]

            futures.wait(processes)

            for p in processes:
                self.__limit_data_objects.append(p.result())
            
        compute_types = ['dense', 'gpu', 'hpc', 'bm']

        for limit_values, limit_definitions in self.__limit_data_objects:
            for limit_definition in limit_definitions:
                if limit_definition.is_deprecated:
                    for limit_value in limit_values:
                        if limit_definition.name == limit_value.name:
                            # Checks if limit name matches any of the compute types
                            if any(compute in limit_value.name for compute in compute_types):
                                record = {
                                    "availability_domain": limit_value.availability_domain,
                                    "name": limit_value.name,
                                    "scope_type": limit_value.scope_type,
                                    "value": limit_value.value,
                                }
                                self.__compute_limits.append(record)

        return self.__compute_limits


    def analyze_entity(self, entry):
        debug_with_color_date('start', 'green')
        self.load_entity()
        debug_with_color_date('stop', 'red')

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for limit in self.__compute_limits:
            if limit['value'] > 5:
                dictionary[entry]['findings'].append(limit)
                if limit['name'] in self.__non_compliant_compute_limits:
                    self.__non_compliant_compute_limits[limit['name']].append(limit['availability_domain'])
                else:
                    self.__non_compliant_compute_limits[limit['name']] = [limit['availability_domain']]

        for key, value in self.__non_compliant_compute_limits.items():
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append('Limits should be correctly configured to what is required for the workload.')
            dictionary[entry]['mitigations'].append(f"Limit name: {key}, is set greater than 5 in all of these ADs: {value}")

        return dictionary


def get_limits_data(limits_client, tenancy_id):

    limits_value_data = list_limit_value_data(limits_client, tenancy_id, "compute")

    limits_definition_data = list_limit_definition_data(limits_client, tenancy_id, "compute")

    return (limits_value_data, limits_definition_data)
