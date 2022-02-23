# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# BusyLimits.py
# Description: Implementation of class BusyLimits based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *


class BusyLimits(ReviewPoint):

    # Class Variables
    __limit_value_objects = []
    __limit_availability_objects = []
    __limit_availabilities = []
    __non_compliant_limits = dict()
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
        
        services = get_services(limits_clients[0][0], tenancy.id)

        self.__limit_value_objects = ParallelExecutor.executor(limits_clients, services, ParallelExecutor.get_limit_values, len(services), ParallelExecutor.limit_values_with_regions)
        
        limit_availability_threads = min(500, len(self.__limit_value_objects))
        self.__limit_availability_objects = ParallelExecutor.executor(limits_clients, self.__limit_value_objects, ParallelExecutor.get_limit_availabilities, limit_availability_threads, ParallelExecutor.limit_availabilities_with_regions)

        for limit_availability in self.__limit_availability_objects:
            record = {
                "region": limit_availability[0],
                "service_name": limit_availability[1],
                "availability_domain": limit_availability[2].availability_domain,
                "scope_type": limit_availability[2].scope_type,
                "name": limit_availability[2].name,
                "value": limit_availability[2].value,
                "used": limit_availability[3].used,
            }
            self.__limit_availabilities.append(record)

        return self.__limit_availabilities


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for limit in self.__limit_availabilities:
            if limit['value'] is not None and limit['value'] > 0 and limit['used'] is not None:
                if (limit['used'] / limit['value']) >= 0.9:
                    dictionary[entry]['findings'].append(limit)
                    location = limit['region']
                    if "AD" in limit['scope_type']:
                        location = limit['availability_domain']
                    if limit['name'] in self.__non_compliant_limits:
                        self.__non_compliant_limits[limit['name']].append(location)
                    else:
                        self.__non_compliant_limits[limit['name']] = [location]

        for key, value in self.__non_compliant_limits.items():
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Ensure you have room for growth and expansion in your tenancy.")
            dictionary[entry]['mitigations'].append(f"Limit name: \"{key}\", has reached \"90%\" or greater use in: {value}")

        return dictionary
