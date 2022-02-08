# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# TrafficSteering.py
# Description: Implementation of class TrafficSteering based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class TrafficSteering(ReviewPoint):

    # Class Variables
    __steering_policy_objects = []
    __steering_policies = []
    __vcns_in_multiple_regions = []
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

        dns_clients = []
        network_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            dns_clients.append(get_dns_client(self.config, self.signer))
            network_clients.append(get_virtual_network_client(region_config, self.signer))

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__steering_policy_objects = ParallelExecutor.executor(dns_clients, self.__compartments, ParallelExecutor.get_steering_policies, len(self.__compartments), ParallelExecutor.steering_policies)
        self.__vcns_in_multiple_regions = ParallelExecutor.check_vcns_in_multiple_regions(network_clients, regions, self.__compartments, ParallelExecutor.vcns_in_multiple_regions)

        return self.__steering_policy_objects, self.__vcns_in_multiple_regions


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        if self.__vcns_in_multiple_regions and len(self.__steering_policy_objects) == 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append('No steering policies found but VCNs are in multiple regions')
            dictionary[entry]['mitigations'].append('Consider using \"steering policies\" if workload is split across multiple regions.')
            
        return dictionary
