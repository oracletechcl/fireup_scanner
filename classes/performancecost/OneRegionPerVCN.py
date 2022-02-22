# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# OneRegionPerVCN.py
# Description: Implementation of class OneRegionPerVCN based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import ipaddr


class OneRegionPerVCN(ReviewPoint):
    # Class Variables
    __vcn_objects = []
    __vcns = []
    __compartments = []
    __identity = None
    __local_peering_gateways = []
    __local_peering_gateway_objects = []

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
            network_clients.append((get_virtual_network_client(region_config, self.signer)))

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, tenancy.id))

        self.__vcn_objects = ParallelExecutor.executor(network_clients, self.__compartments, ParallelExecutor.get_vcns_in_compartments, len(self.__compartments), ParallelExecutor.vcns)
        self.__local_peering_gateway_objects = ParallelExecutor.executor(network_clients, self.__compartments, ParallelExecutor.get_local_peering_gateways, len(self.__compartments), ParallelExecutor.local_peering_gateways)

        for vcn in self.__vcn_objects:
            record = {
                'cidr_blocks': vcn.cidr_blocks,
                'compartment_id': vcn.compartment_id,
                'display_name': vcn.display_name,
                'id': vcn.id,
                'lifecycle_state': vcn.lifecycle_state,
            }
            self.__vcns.append(record)

        for local_gateway in self.__local_peering_gateway_objects:
            record = {
                'compartment_id': local_gateway.compartment_id,
                'display_name': local_gateway.display_name,
                'id': local_gateway.id,
                'peering_status' : local_gateway.peering_status,
                'peer_id': local_gateway.peer_id,
                'vcn_id': local_gateway.vcn_id,
                'cidr_blocks': local_gateway.peer_advertised_cidr,
                'cidr_block_details': local_gateway.peer_advertised_cidr_details,
                'lifecycle_state': local_gateway.lifecycle_state,
            }
            self.__local_peering_gateways.append(record)

        return self.__local_peering_gateways, self.__vcns


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        seen = []
        duplicates = []
        for local_gateway in self.__local_peering_gateways:
            for d in seen:
                if d['peering_status'] == 'PEERED' and d['id'] == local_gateway['peer_id']:
                    duplicates.append((local_gateway, d))
            else:
                seen.append(local_gateway)

        for gateway1, gateway2 in duplicates:
            cidr1 = gateway1['cidr_blocks']
            cidr2 = gateway2['cidr_blocks']
            if ipaddr.IPNetwork(cidr1).overlaps(ipaddr.IPNetwork(cidr2)):
                for vcn in self.__vcns:
                    if vcn['id'] == gateway1['vcn_id']:
                        vcn_name1 = vcn['display_name']
                        gateway1['vcn_display_name'] = vcn_name1
                    if vcn['id'] == gateway2['vcn_id']:
                        vcn_name2 = vcn['display_name']
                        gateway2['vcn_display_name'] = vcn_name2
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(gateway1)
                dictionary[entry]['findings'].append(gateway2)
                dictionary[entry]['failure_cause'].append("VCN is peered to another VCN where the CIDR blocks are overlapping")
                dictionary[entry]['mitigations'].append(f"Make sure peered VCN: (\"{gateway1['vcn_display_name']}\" in compartment: \"{get_compartment_name(self.__compartments,gateway1['compartment_id'])}\") "
                                                        f"and peered VCN: (\"{gateway2['vcn_display_name']}\" in compartment: \"{get_compartment_name(self.__compartments,gateway2['compartment_id'])}\") "
                                                        f"do not have overlapping CIDR blocks.")

        return dictionary
