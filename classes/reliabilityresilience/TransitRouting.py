# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# TransitRouting.py
# Description: Implementation of class TransitRouting based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class TransitRouting(ReviewPoint):

    # Class Variables
    __identity = None
    __tenancy = None
    __networking_topology_objects = []


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

        # From here on the code is not implemented on abstract class
        self.config = config
        self.signer = signer
        self.__identity = get_identity_client(self.config, self.signer)
        self.__tenancy = get_tenancy_data(self.__identity, self.config)



    def load_entity(self):

        # network_client = get_virtual_network_client(self.config, self.signer)
        # topology = get_networking_topology_per_compartment(network_client, self.__tenancy.id)

        # network_client = oci.core.VirtualNetworkClient(self.config, signer = self.signer)
        # network_client.base_client.endpoint = "https://vnca-api.uk-london-1.oci.oraclecloud.com"
        # topology = network_client.get_networking_topology(self.__tenancy.id, query_compartment_subtree = True ).data

        # debug(topology,color="green")
        network_clients = []
        regions = get_regions_data(self.__identity, self.config)

        compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            n_client = get_virtual_network_client(region_config, self.signer)
            n_client.base_client.endpoint = 'https://vnca-api.' + region.region_name + '.oci.oraclecloud.com'
            network_clients.append(n_client)
        
        self.__networking_topology_objects = ParallelExecutor.executor(network_clients, compartments, ParallelExecutor.get_networking_topology_1, len(compartments), ParallelExecutor.networking_topology)     

        debug(self.__networking_topology_objects[1],color = "yellow")

    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        return dictionary
