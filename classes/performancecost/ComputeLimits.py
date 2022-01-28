# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ComputeLimits.py
# Description: Implementation of class ComputeLimits based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *


class ComputeLimits(ReviewPoint):

    # Class Variables
    __limit_value_objects = []
    __limit_definition_objects = []
    __compute_limits = []
    __non_compliant_compute_limits = dict()
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

        limits_clients = []
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            limits_clients.append( (get_limits_client(region_config, self.signer), tenancy.id, region.region_name) )

        services = limits_clients[0][0].list_services(tenancy.id).data

        self.__limit_definition_objects = ParallelExecutor.executor([limits_clients[0]], services, ParallelExecutor.get_limit_definitions, len(services), ParallelExecutor.limit_definitions)
        self.__limit_value_objects = ParallelExecutor.executor(limits_clients, services, ParallelExecutor.get_limit_values, len(services), ParallelExecutor.limit_values_with_regions)
       
        compute_limit_definitions = []
        compute_limit_values = []

        # Pick out just the compute limit definitions
        for limit_definition in self.__limit_definition_objects:
            if limit_definition.service_name == "compute":
                compute_limit_definitions.append(limit_definition)

        # Pick out just the compute limit values
        for limit_value in self.__limit_value_objects:
            if limit_value[1] == "compute":
                compute_limit_values.append(limit_value)

        # List of compute keywords checked against
        compute_types = ['dense', 'gpu', 'hpc', 'bm']

        for limit_value in compute_limit_values:
            # Only if limit is set in AD 1
            if limit_value[2].scope_type == "AD" and limit_value[2].availability_domain[-1] == "1":
                for limit_definition in compute_limit_definitions:
                    if limit_definition.is_deprecated and limit_definition.name == limit_value[2].name:
                        # Checks if limit name matches any of the compute types
                        if any(compute in limit_value[2].name for compute in compute_types):
                            record = {
                                "availability_domain": limit_value[2].availability_domain,
                                "name": limit_value[2].name,
                                "scope_type": limit_value[2].scope_type,
                                "value": limit_value[2].value,
                            }
                            self.__compute_limits.append(record)

        return self.__compute_limits


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for limit in self.__compute_limits:
            if limit['value'] > 5:
                dictionary[entry]['findings'].append(limit)
                # Coverts AD to look like a region
                ad = "-".join(limit['availability_domain'].split(':')[1].split('-')[:3])
                if ad.split('-')[-1] == "AD":
                    ad = "-".join(ad.split('-')[:2])
                if limit['name'] in self.__non_compliant_compute_limits:
                    self.__non_compliant_compute_limits[limit['name']].append(ad)
                else:
                    self.__non_compliant_compute_limits[limit['name']] = [ad]

        for key, value in self.__non_compliant_compute_limits.items():
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append('Limits should be correctly configured to what is required for the workload.')
            dictionary[entry]['mitigations'].append(f"Limit name: {key}, is set greater than 5 in all of these ADs: {value}")

        return dictionary
