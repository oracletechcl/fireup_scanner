# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# SeparateCIDRBlocks.py
# Description: Implementation of class SeparateCIDRBlocks based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from itertools import combinations
import common.utils.helpers.ParallelExecutor as ParallelExecutor
import ipaddr


class SeparateCIDRBlocks(ReviewPoint):

    # Class Variables
    __vcns = []
    __vcn_objects = []
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
        network_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            network_clients.append(get_virtual_network_client(region_config, self.signer))

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        # self.__vcns = parallel_executor(network_clients, compartments, self.__search_compartments, len(compartments), "__vcns")

        self.__vcn_objects = ParallelExecutor.executor(network_clients, compartments, ParallelExecutor.get_vcns_in_compartments, len(compartments), ParallelExecutor.vcns)

        for vcn in self.__vcn_objects:
            record = {
                'cidr_blocks': vcn.cidr_blocks,
                'compartment_id': vcn.compartment_id,
                'display_name': vcn.display_name,
                'id': vcn.id,
                'lifecycle_state': vcn.lifecycle_state,
            }
            self.__vcns.append(record)

        return self.__vcns


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        pairs = combinations(self.__vcns, 2)

        for vcn1, vcn2 in pairs:
            for cidr1 in vcn1['cidr_blocks']:
                for cidr2 in vcn2['cidr_blocks']:
                    # If the VCN is not compliant, add it to findings if it hasn't already been added
                    if ipaddr.IPNetwork(cidr1).overlaps(ipaddr.IPNetwork(cidr2)):
                        dictionary[entry]['status'] = False
                        if vcn1 not in dictionary[entry]['findings']:
                            dictionary[entry]['findings'].append(vcn1)
                            dictionary[entry]['failure_cause'].append('VCNs CIDR Blocks are overlapping')
                            dictionary[entry]['mitigations'].append('Make sure vcn '+str(vcn1['display_name'])+' CIDR Blocks are not overlapping with vcn '+str(vcn2['display_name']))

        return dictionary
