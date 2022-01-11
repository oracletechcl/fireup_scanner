# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# OneRegionPerVCN.py
# Description: Implementation of class OneRegionPerVCN based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import ipaddr
from itertools import combinations


class OneRegionPerVCN(ReviewPoint):
    # Class Variables
    __vcn_objects = []
    __identity = None
    __vcns = []

    def __init__(self,
                 entry: str,
                 area: str,
                 sub_area: str,
                 review_point: str,
                 status: bool,
                 failure_cause: list,
                 findings: list,
                 mitigations: list,
                 fireup_mapping: list,
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
            network_clients.append((get_virtual_network_client(region_config, self.signer), region.region_name,region.region_key.lower()))

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__vcn_objects = ParallelExecutor.executor([x[0] for x in network_clients], compartments, ParallelExecutor.get_vcns_in_compartments, len(compartments), ParallelExecutor.vcns)

        for vcn in self.__vcn_objects:
            record = {
                'cidr_blocks': vcn.cidr_blocks,
                'compartment_id': vcn.compartment_id,
                'region': vcn.id.split('.')[3],
                'display_name': vcn.display_name,
                'id': vcn.id,
                'lifecycle_state': vcn.lifecycle_state,
            }
            self.__vcns.append(record)

        return self.__vcns


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        seen = []
        duplicates = []
        for vcn in self.__vcns:
            for d in seen:
                if d['display_name'] == vcn['display_name']:
                    duplicates.append((vcn,d))
            else:
                seen.append(vcn)

        for vcn1,vcn2 in duplicates:
            cidr1 = vcn1['cidr_blocks'][0]
            cidr2 = vcn2['cidr_blocks'][0]
            if ipaddr.IPNetwork(cidr1).overlaps(ipaddr.IPNetwork(cidr2)):
                dictionary[entry]['status'] = False
                if vcn1 not in dictionary[entry]['findings']:
                    dictionary[entry]['findings'].append(vcn1)
                    dictionary[entry]['failure_cause'].append('VCNs are overlapping in regions')
                    dictionary[entry]['mitigations'].append('Make sure vcn ' + str(
                        vcn1['display_name']) + ' in ' + str(vcn1['region']) +' and ' + str(
                        vcn2['display_name']) + ' in ' + str(vcn2['region']) + ' are not the same.')
        return dictionary
