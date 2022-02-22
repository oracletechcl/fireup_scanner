# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# SecurityList.py
# Description: Implementation of class SecurityList based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import ipaddr

class SecurityList(ReviewPoint):

    # Class Variables
    __identity = None
    __compartments = []
    __sec_list_objects = []
    __non_compliant_sec_list = []
    __load_balancers = []
    __network_load_balancer_objects = []
    __load_balancer_objects = []
    __network_clients = []


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
            self.__network_clients.append((get_virtual_network_client(region_config, self.signer),region.region_name,region.region_key.lower()))
            load_balancer_clients.append(get_load_balancer_client(region_config, self.signer))
            network_load_balancer_clients.append(get_network_load_balancer_client(region_config, self.signer))

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, tenancy.id))

        self.__sec_list_objects = ParallelExecutor.executor([x[0] for x in self.__network_clients], self.__compartments, ParallelExecutor.get_security_lists, len(self.__compartments), ParallelExecutor.security_lists)
        self.__load_balancer_objects = ParallelExecutor.executor(load_balancer_clients, self.__compartments, ParallelExecutor.get_load_balancers, len(self.__compartments), ParallelExecutor.load_balancers)
        self.__network_load_balancer_objects = ParallelExecutor.executor(network_load_balancer_clients, self.__compartments, ParallelExecutor.get_network_load_balancers, len(self.__compartments), ParallelExecutor.network_load_balancers)
        

        for load_balancer in self.__load_balancer_objects + self.__network_load_balancer_objects:

            if "networkloadbalancer" in load_balancer.id:
                record = {
                    'display_name': load_balancer.display_name,
                    'id': load_balancer.id,
                    'compartment_id': load_balancer.compartment_id,
                    'backend_sets': load_balancer.backend_sets,
                    'subnet_id':load_balancer.subnet_id,
                    'is_private': load_balancer.is_private,
                    'lifecycle_state': load_balancer.lifecycle_state,
                    'time_created': load_balancer.time_created,
                }
            else:
                record = {
                    'display_name': load_balancer.display_name,
                    'id': load_balancer.id,
                    'compartment_id': load_balancer.compartment_id,
                    'backend_sets': load_balancer.backend_sets,
                    'subnet_id':load_balancer.subnet_ids,
                    'is_private': load_balancer.is_private,
                    'lifecycle_state': load_balancer.lifecycle_state,
                    'time_created': load_balancer.time_created,
                }
            self.__load_balancers.append(record)

        for sec_list in self.__sec_list_objects:
            for ingress in sec_list.ingress_security_rules:
                if ingress.source == '0.0.0.0/0':
                    sec_list_record = {
                        'compartment_id': sec_list.compartment_id,
                        'defined_tags': sec_list.defined_tags,
                        'display_name': sec_list.display_name,
                        'id': sec_list.id,
                        'lifecycle_state': sec_list.lifecycle_state,
                        'time_created': sec_list.time_created,
                        'vcn_id': sec_list.vcn_id,
                    }
                    self.__non_compliant_sec_list.append(sec_list_record)
                break
            else:
                continue

        return self.__non_compliant_sec_list


    def analyze_entity(self, entry):
    
        self.load_entity()    
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        vcn_backend_cidrs = []
        for load_balancer in self.__load_balancers:
            backend_cidr_blocks = []
            for backend_set in load_balancer['backend_sets']:
                backends = load_balancer['backend_sets'][backend_set].backends
                for backend in backends:
                    backend_ip = backend.ip_address
                    backend_cidr_blocks.append(backend_ip)

            if type(load_balancer['subnet_id']) is list:
                subnet_id = load_balancer['subnet_id'][0]
            else: 
                subnet_id = load_balancer['subnet_id']

            for network_client in self.__network_clients:
                region = subnet_id.split('.')[3]
                if network_client[1] in region or network_client[2] in region:
                    subnet_info = get_subnet_info(network_client[0], subnet_id = subnet_id)
                    vcn_info = get_vcn_from_subnet(network_client[0], vcn_id = subnet_info.vcn_id)
                    subnets = get_subnets_per_compartment_data(network_client[0], compartment_id = vcn_info.compartment_id)
                    subnet_cidr_blocks = []
                    for subnet in subnets:
                        if subnet.vcn_id in vcn_info.id:
                            if subnet.prohibit_internet_ingress is False:
                                subnet_cidr_blocks.append(subnet.cidr_block)
                    record = {
                        'load_balancer_name': load_balancer['display_name'],
                        'load_balancer_id': load_balancer['id'],
                        'vcn_id': vcn_info.id,
                        'subnet_id': subnet.id,
                        'subnet_cidr_blocks': subnet.cidr_block,
                        'backend_cidr_blocks': backend_cidr_blocks
                    }
                    vcn_backend_cidrs.append(record)

        for blocks in vcn_backend_cidrs:
            subnet_block = blocks['subnet_cidr_blocks']
            backend_blocks = blocks['backend_cidr_blocks']
            for backend_block in backend_blocks:
                if ipaddr.IPNetwork(subnet_block).overlaps(ipaddr.IPNetwork(backend_block)) is True:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['failure_cause'].append("Load Balancer: {} contains backends which are not in a private subnet".format(blocks['load_balancer_name']))
                    dictionary[entry]['findings'].append(blocks)
                    dictionary[entry]['mitigations'].append("Make sure to move load balancer: {} backends to a private subnet".format(blocks['load_balancer_name']))
                    break
            else:
                continue

        if len(self.__non_compliant_sec_list) > 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Security List contains a wide open \"0.0.0.0/0\" CIDR in ingress rule that needs to be closed")
            for sec_list in self.__non_compliant_sec_list:
                if sec_list not in dictionary[entry]['findings']:
                    dictionary[entry]['findings'].append(sec_list)
                    dictionary[entry]['mitigations'].append(f"Make sure to reduce access and set more granular permissions into: \"{sec_list['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, sec_list['compartment_id'])}\"")
                                       
        return dictionary

