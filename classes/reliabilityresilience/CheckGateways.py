# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CheckGateways.py
# Description: Implementation of class CheckGateways based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor


class CheckGateways(ReviewPoint):

    # Class Variables
    __compartments = []
    __drg_objects = []
    __drg_attachments_ids = []
    __drg_attachments = []
    __service_gateway_objects = []
    __local_peering_gateway_objects = []
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
            network_clients.append( (get_virtual_network_client(region_config, self.signer), region.region_name, region.region_key.lower()) )

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments .append(get_tenancy_data(self.__identity, self.config))

        self.__drg_objects = ParallelExecutor.executor([x[0] for x in network_clients], self.__compartments , ParallelExecutor.get_drgs, len(self.__compartments ), ParallelExecutor.drgs)

        if len(self.__drg_objects) > 0:
            self.__drg_attachments_ids = ParallelExecutor.executor(network_clients, self.__drg_objects, ParallelExecutor.get_drg_attachment_ids, len(self.__drg_objects), ParallelExecutor.drg_attachment_ids)

        if len(self.__drg_attachments_ids) > 0:    
            self.__drg_attachments = ParallelExecutor.executor(network_clients, self.__drg_attachments_ids, ParallelExecutor.get_drg_attachments, len(self.__drg_attachments_ids), ParallelExecutor.drg_attachments)

        self.__service_gateway_objects = ParallelExecutor.executor([x[0] for x in network_clients], self.__compartments, ParallelExecutor.get_service_gateways, len(self.__compartments), ParallelExecutor.service_gateways)
        self.__local_peering_gateway_objects = ParallelExecutor.executor([x[0] for x in network_clients], self.__compartments, ParallelExecutor.get_local_peering_gateways, len(self.__compartments), ParallelExecutor.local_peering_gateways)


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        # This review point fails, unless valid data is found to prove otherwise
        # i.e some method of bypassing the internet is present
        dictionary[entry]['status'] = False

        # Checks if and DRGs are attachment to IPSEC VPN Tunnels or Virtual Circuits
        valid_attachments = ['VIRTUAL_CIRCUIT', 'IPSEC_TUNNEL']
        for attachment in self.__drg_attachments:
            if attachment.network_details is not None:
                if attachment.network_details.type in valid_attachments:
                    dictionary[entry]['status'] = True
        
        # Checks if a service gateway is present and tied to a route table
        for service_gateway in self.__service_gateway_objects:
            if service_gateway.route_table_id is not None:
                dictionary[entry]['status'] = True

        # Checks if an LPG is correctly peered to another VCN
        for local_peering_gateway in self.__local_peering_gateway_objects:
            if local_peering_gateway.peering_status == "PEERED":
                dictionary[entry]['status'] = True

        if not dictionary[entry]['status']:
            dictionary[entry]['failure_cause'].append('No method of bypassing the internet to access OCI was found.')
            dictionary[entry]['mitigations'].append('When connecting OCI to public resources, use FastConnect, VPN Connect, or a service gateway to bypass the internet.')

        return dictionary
