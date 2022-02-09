# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# LBaaSBackends.py
# Description: Implementation of class LBaaSBackends based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *


class LBaaSBackends(ReviewPoint):

    # Class Variables
    __combined_load_balancers = []
    __load_balancer_objects = []
    __network_load_balancer_objects = []
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
        load_balancer_clients = []
        network_load_balancer_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            load_balancer_clients.append(get_load_balancer_client(region_config, self.signer))
            network_load_balancer_clients.append(get_network_load_balancer_client(region_config, self.signer))

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__load_balancer_objects = ParallelExecutor.executor(load_balancer_clients, self.__compartments, ParallelExecutor.get_load_balancers, len(self.__compartments), ParallelExecutor.load_balancers)
        
        self.__network_load_balancer_objects = ParallelExecutor.executor(network_load_balancer_clients, self.__compartments, ParallelExecutor.get_network_load_balancers, len(self.__compartments), ParallelExecutor.network_load_balancers)

        for load_balancer in self.__load_balancer_objects + self.__network_load_balancer_objects:
            record = {
                'display_name': load_balancer.display_name,
                'id': load_balancer.id,
                'compartment_id': load_balancer.compartment_id,
                'backend_sets': load_balancer.backend_sets,
                'is_private': load_balancer.is_private,
                'lifecycle_state': load_balancer.lifecycle_state,
                'time_created': load_balancer.time_created,
            }
            self.__combined_load_balancers.append(record)

        return self.__combined_load_balancers


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        # Loop through each load balancer and look for those without backends
        for load_balancer in self.__combined_load_balancers:
            for backend_set in load_balancer['backend_sets']:
                backend_set_dict = load_balancer['backend_sets'][backend_set].backends

                if len(backend_set_dict) == 0:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['findings'].append(load_balancer)
                    dictionary[entry]['failure_cause'].append("Load balancers should all have attached backend sets populated with one or more backend.")
                    if "networkloadbalancer" in load_balancer['id']:
                        dictionary[entry]['mitigations'].append(f"Make sure network load balancer \"{load_balancer['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, load_balancer['compartment_id'])}\" has backends attached to it.")
                    else:
                        dictionary[entry]['mitigations'].append(f"Make sure load balancer \"{load_balancer['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, load_balancer['compartment_id'])}\" has backends attached to it.")
                    break

        return dictionary
