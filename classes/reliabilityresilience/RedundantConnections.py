# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# RedundantConnections.py
# Description: Implementation of class RedundantConnections based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class RedundantConnections(ReviewPoint):

    # Class Variables
    __virtual_circuit_objects = []
    __virtual_circuit_dicts = []
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

        # From here on the code is not implemented on abstract class
        self.config = config
        self.signer = signer
        self.__identity = get_identity_client(self.config, self.signer)


    def load_entity(self):
        regions = get_regions_data(self.__identity, self.config)
        
        tenancy = get_tenancy_data(self.__identity, self.config)

        network_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create clients for each region
            network_clients.append(get_virtual_network_client(region_config, self.signer))

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__virtual_circuit_objects = ParallelExecutor.executor(network_clients, self.__compartments, ParallelExecutor.get_virtual_circuits, len(self.__compartments), ParallelExecutor.virtual_circuits)

        for virtual_circuit in self.__virtual_circuit_objects:
            record = {
                "display_name": virtual_circuit.display_name,
                "id": virtual_circuit.id,
                "compartment_id": virtual_circuit.compartment_id,
                "bgp_session_state": virtual_circuit.bgp_session_state,
                "lifecycle_state": virtual_circuit.lifecycle_state,
                "type": virtual_circuit.type,
            }
            self.__virtual_circuit_dicts.append(record)

        return self.__virtual_circuit_dicts


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        compliant_virtual_circuits = []
        non_compliant_virtual_circuits = []
        
        for virtual_circuit in self.__virtual_circuit_dicts:
            if virtual_circuit['lifecycle_state'] == "PROVISIONED":
                compliant_virtual_circuits.append(virtual_circuit)
            else:
                non_compliant_virtual_circuits.append(virtual_circuit)

        # Checks whether there is only a single compliant virtual circuit set up - failing the review point
        if len(self.__virtual_circuit_dicts) > 0 and len(compliant_virtual_circuits) < 2:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append('When using fast connect, ensure that a reduntant virtual circuit is set up')
            for virtual_circuit in non_compliant_virtual_circuits:
                dictionary[entry]['findings'].append(virtual_circuit)
                dictionary[entry]['mitigations'].append(f"Virtual Circuit: {virtual_circuit['display_name']} in Compartment: {get_compartment_name(self.__compartments, virtual_circuit['compartment_id'])} has not been set up correctly.")
            if len(compliant_virtual_circuits) > 0:
                dictionary[entry]['findings'].append(compliant_virtual_circuits[0])
                dictionary[entry]['mitigations'].append(f"Virtual Circuit: {compliant_virtual_circuits[0]['display_name']} in Compartment: {get_compartment_name(self.__compartments, compliant_virtual_circuits[0]['compartment_id'])} has no redundant connection.")

        return dictionary
