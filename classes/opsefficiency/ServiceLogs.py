# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ServiceLogs.py
# Description: Implementation of class ServiceLogs based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class ServiceLogs(ReviewPoint):

    # Class Variables

    __identity = None
    __logs = None
    __bucket_objects = None
    __compartments = None
    __load_balancers_objects = None
    __load_balancers = []
    __network_load_balancers_objects = None
    __network_load_balancers = []
    __subnets_objects = None
    __subnets = []
    __functions_objects = None
    __functions = []
    __buckets = []
    __ip_sec_connections_objects = None
    __ip_sec_connections = []
    __events_rules_objects = None
    __events_rules = []
    



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
        self.__tenancy = get_tenancy_data(self.__identity, self.config)


    def load_entity(self):

        obj_client = get_object_storage_client(self.config,self.signer)
        obj_namespace = get_objectstorage_namespace_data(obj_client)

        logging_management_clients = []
        object_storage_clients = []
        load_balancer_clients = []
        network_load_balancer_clients = []
        network_clients = []
        functions_management_clients = []
        events_clients = []
        regions = get_regions_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        # get clients from each region 
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name

            logging_management_clients.append((get_logging_management_client(region_config, self.signer)))
            object_storage_clients.append((get_object_storage_client(region_config, self.signer), obj_namespace))
            load_balancer_clients.append(get_load_balancer_client(region_config, self.signer))
            network_load_balancer_clients.append(get_network_load_balancer_client(region_config, self.signer))
            network_clients.append(get_virtual_network_client(region_config, self.signer))            
            functions_management_clients.append(get_functions_management_client(region_config, self.signer))            
            events_clients.append(get_events_client(region_config, self.signer))            
            
 
        self.__logs = ParallelExecutor.executor(logging_management_clients, self.__compartments, ParallelExecutor.get_log_groups, len(self.__compartments), ParallelExecutor.log_groups)   
        self.__bucket_objects = ParallelExecutor.executor(object_storage_clients, self.__compartments, ParallelExecutor.get_buckets, len(self.__compartments), ParallelExecutor.buckets)
        self.__load_balancers_objects = ParallelExecutor.executor(load_balancer_clients, self.__compartments, ParallelExecutor.get_load_balancers, len(self.__compartments), ParallelExecutor.load_balancers)
        self.__network_load_balancers_objects = ParallelExecutor.executor(network_load_balancer_clients, self.__compartments, ParallelExecutor.get_network_load_balancers, len(self.__compartments), ParallelExecutor.network_load_balancers)
        self.__subnets_objects = ParallelExecutor.executor(network_clients, self.__compartments, ParallelExecutor.get_subnets_in_compartments, len(self.__compartments), ParallelExecutor.subnets)
        self.__functions_objects = ParallelExecutor.executor(functions_management_clients, self.__compartments, ParallelExecutor.get_functions, len(self.__compartments), ParallelExecutor.functions)
        self.__ip_sec_connections_objects = ParallelExecutor.executor(network_clients, self.__compartments, ParallelExecutor.get_ip_sec_connections_tunnels, len(self.__compartments), ParallelExecutor.ip_sec_connections_tunnels)
        self.__events_rules_objects = ParallelExecutor.executor(events_clients, self.__compartments, ParallelExecutor.get_events_rules, len(self.__compartments), ParallelExecutor.events_rules)

        for bucket in self.__bucket_objects:
            record = {
                    "compartment_id": bucket.compartment_id,
                    "created_by": bucket.created_by,
                    "id": bucket.id,
                    "name": bucket.name,
                    "namespace": bucket.namespace,
                    "public_access_type": bucket.public_access_type,
                    "storage_tier": bucket.storage_tier,
                    "time_created": bucket.time_created,
            }
            self.__buckets.append(record)

        for load_balancer in self.__load_balancers_objects:
            record = {
                    "compartment_id": load_balancer.compartment_id,
                    "id": load_balancer.id,
                    "shape_details": load_balancer.shape_details,
                    "shape_name": load_balancer.shape_name, 
                    "time_created": load_balancer.time_created,
                    "display_name": load_balancer.display_name,
                    "lifecycle_state": load_balancer.lifecycle_state,
            }
            self.__load_balancers.append(record)

        for network_load_balancer in self.__network_load_balancers_objects:
            record = {
                    "compartment_id": network_load_balancer.compartment_id, 
                    "id": network_load_balancer.id, 
                    "time_created": network_load_balancer.time_created, 
                    "display_name": network_load_balancer.display_name, 
                    "lifecycle_state": network_load_balancer.lifecycle_state,
            }
            self.__network_load_balancers.append(record)

        for subnet in self.__subnets_objects:
            record = {
                    "compartment_id": subnet.compartment_id,  
                    "id": subnet.id,  
                    "time_created": subnet.time_created,  
                    "display_name": subnet.display_name,  
                    "lifecycle_state": subnet.lifecycle_state,
                    "cidr_block": subnet.cidr_block,
                    "dns_label": subnet.dns_label,
                    "subnet_domain_name": subnet.subnet_domain_name
            }
            self.__subnets.append(record)

        for function in self.__functions_objects:
            record = {
                    "compartment_id": function.compartment_id,   
                    "id": function.id,   
                    "time_created": function.time_created,  
                    "display_name": function.display_name,   
                    "lifecycle_state": function.lifecycle_state,
                    "application_id": function.application_id,              
            }
            self.__functions.append(record)

        for tunnel in self.__ip_sec_connections_objects:
            record = {
                    "compartment_id": tunnel.compartment_id, 
                    "id": tunnel.id,   
                    "time_created": tunnel.time_created,  
                    "display_name": tunnel.display_name,  
                    "lifecycle_state": tunnel.lifecycle_state, 
                    "status": tunnel.status, 
                    "vpn_ip": tunnel.vpn_ip       
            }
            self.__ip_sec_connections.append(record)

        for rule in self.__events_rules_objects:
            record = {
                    "compartment_id": rule.compartment_id, 
                    "id": rule.id,   
                    "time_created": rule.time_created,  
                    "display_name": rule.display_name,
                    "description": rule.description,
                    "lifecycle_state": rule.lifecycle_state, 
                    "is_enabled": rule.is_enabled
            }
            self.__events_rules.append(record)

    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        self.find_logs(self.__buckets,'Bucket ',dictionary,entry)
        self.find_logs(self.__load_balancers,'Load Balancer ',dictionary,entry)
        self.find_logs(self.__network_load_balancers,'Network Load Balancer ',dictionary,entry)
        self.find_logs(self.__subnets,'Subnet ',dictionary,entry)
        self.find_logs(self.__functions,'Function ',dictionary,entry)
        self.find_logs(self.__ip_sec_connections,'IPSec Tunnel ',dictionary,entry)
        self.find_logs(self.__events_rules,'Event Rule ',dictionary,entry)

        return dictionary

    def find_logs(self,infrastructure_service_resources, service_name, dictionary,entry):
        for resource in infrastructure_service_resources:
            log_enabled = False
            for log in self.__logs:
                if log.configuration.source.resource == resource['id']:
                    log_enabled = True
                    break
            if not log_enabled:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(resource)
                dictionary[entry]['failure_cause'].append('The ' + service_name + 'does not have Log Service enabled') 
                dictionary[entry]['mitigations'].append('Consider enabling Log Service for ' + service_name + 'identified by OCID: ' + resource['id'])
    
    # def extract_dict(objects):
    #      for element in self.__functions_objects:
    #         record = {
    #                 "compartment_id": function.compartment_id,   
    #                 "id": function.id,   
    #                 "time_created": function.time_created,  
    #                 "display_name": function.display_name,   
    #                 "lifecycle_state": function.lifecycle_state,
    #                 "application_id": function.application_id,              
    #         }
    #         self.__functions.append(record)







