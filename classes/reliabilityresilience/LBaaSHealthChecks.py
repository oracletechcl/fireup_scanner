# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# LBaaSHealthChecks.py
# Description: Implementation of class LBaaSHealthChecks based on abstract

from oci.load_balancer import load_balancer_client
from oci.load_balancer.load_balancer_client import LoadBalancerClient
from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *


class LBaaSHealthChecks(ReviewPoint):

    # Class Variables
    __load_balancers = []
    __network_load_balancers = []
    __load_balancer_healths = []
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
            load_balancer_clients.append( (get_load_balancer_client(region_config, self.signer), region.region_name, region.region_key.lower()) )
            network_load_balancer_clients.append( (get_network_load_balancer_client(region_config, self.signer), region.region_name, region.region_key.lower()) )

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__load_balancers = parallel_executor([x[0] for x in load_balancer_clients], compartments, self.__search_load_balancers, len(compartments), "__load_balancers")

        self.__network_load_balancers = parallel_executor([x[0] for x in network_load_balancer_clients], compartments, self.__search_network_load_balancers, len(compartments), "__network_load_balancers")

        load_balancer_healths = parallel_executor(load_balancer_clients, self.__load_balancers, self.__search_load_balancer_healths, len(self.__load_balancers), "__load_balancer_healths")

        network_load_balancer_healths = parallel_executor(network_load_balancer_clients, self.__network_load_balancers, self.__search_load_balancer_healths, len(self.__network_load_balancers), "__network_load_balancer_healths")

        self.__load_balancer_healths = load_balancer_healths + network_load_balancer_healths

        return self.__load_balancer_healths


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for load_balancer, health in self.__load_balancer_healths:
            if "OK" not in health.status:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(load_balancer)
                dictionary[entry]['failure_cause'].append('Load balancers should all have passing health checks.')
                if "networkloadbalancer" in load_balancer['id']:
                    dictionary[entry]['mitigations'].append('Make sure network load balancer '+str(load_balancer['display_name'])+' has passing health checks')
                else:
                    dictionary[entry]['mitigations'].append('Make sure load balancer '+str(load_balancer['display_name'])+' has passing health checks')

        return dictionary


    def __search_load_balancers(self, item):
        network_load_balancer_client = item[0]
        compartments = item[1:]

        load_balancers = []

        for compartment in compartments:
            load_balancer_data = get_load_balancer_data(network_load_balancer_client, compartment.id)
            for load_balancer in load_balancer_data:
                record = {
                    'display_name': load_balancer.display_name,
                    'id': load_balancer.id,
                    'compartment_id': load_balancer.compartment_id,
                    'ip_addresses': load_balancer.ip_addresses,
                    'backend_sets': load_balancer.backend_sets,
                    'is_private': load_balancer.is_private,
                    'lifecycle_state': load_balancer.lifecycle_state,
                    'listeners': load_balancer.listeners,
                    'shape_name': load_balancer.shape_name,
                    'subnet_ids': load_balancer.subnet_ids,
                    'network_security_group_ids': load_balancer.network_security_group_ids,
                    'routing_policies': load_balancer.routing_policies,
                    'time_created': load_balancer.time_created,
                    'is_preserve_source_destination': '',
                }

                load_balancers.append(record)

        return load_balancers


    def __search_network_load_balancers(self, item):
        load_balancer_client = item[0]
        compartments = item[1:]

        network_load_balancers = []

        for compartment in compartments:
            network_load_balancer_data = get_network_load_balancer_data(load_balancer_client, compartment.id)
            for network_load_balancer in network_load_balancer_data:
                record = {
                    'display_name': network_load_balancer.display_name,
                    'id': network_load_balancer.id,
                    'compartment_id': network_load_balancer.compartment_id,
                    'ip_addresses': network_load_balancer.ip_addresses,
                    'backend_sets': network_load_balancer.backend_sets,
                    'is_private': network_load_balancer.is_private,
                    'lifecycle_state': network_load_balancer.lifecycle_state,
                    'listeners': network_load_balancer.listeners,
                    'network_security_group_ids': network_load_balancer.network_security_group_ids,
                    'is_preserve_source_destination': network_load_balancer.is_preserve_source_destination,
                    'time_created': network_load_balancer.time_created
                }

                network_load_balancers.append(record)

        return network_load_balancers


    def __search_load_balancer_healths(self, item):
        client = item[0]
        load_balancers = item[1:]

        healths = []

        for load_balancer in load_balancers:
            id = load_balancer['id']
            if "networkloadbalancer" in id:
                if client[1] in id or client[2] in id:
                    healths.append( (load_balancer, client[0].get_network_load_balancer_health(id).data) )
            else:
                if client[1] in id or client[2] in id:
                    healths.append( (load_balancer, client[0].get_load_balancer_health(id).data) )

        return healths        
