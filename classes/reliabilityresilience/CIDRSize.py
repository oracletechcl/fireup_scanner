# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CIDRSize.py
# Description: Implementation of class CIDRSize based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class CIDRSize(ReviewPoint):

    # Class Variables
    __vcns = []
    __vcn_objects = []
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
        network_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            network_clients.append(get_virtual_network_client(region_config, self.signer))

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, tenancy.id))

        self.__vcn_objects = ParallelExecutor.executor(network_clients, self.__compartments, ParallelExecutor.get_vcns_in_compartments, len(self.__compartments), ParallelExecutor.vcns)

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

        for vcn in self.__vcns:
            for cidr in vcn['cidr_blocks']:
                if int(cidr.split('/')[1]) > 24:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['findings'].append(vcn)
                    dictionary[entry]['failure_cause'].append("VCNs CIDR Blocks are too small, making it harder to expand.")
                    dictionary[entry]['mitigations'].append(f"Make sure vcn: \"{vcn['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, vcn['compartment_id'])}\" CIDR block(s) are at least /24 or bigger.")

        return dictionary
