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
    __log_groups = None
    __bucket_objects = None
    __compartments = None
    __load_balancers_objects = None
    __network_load_balancers_objects = None
    __subnets_objects = None
    __functions_objects = None
    __ip_sec_connections_objects = None
    __ip_sec_tunnels_objects = None
    __events_rules_objects = None
    __applications_objects = None
    __ip_sec_tunnels = []
    __load_balancers = []
    __network_load_balancers = []
    __subnets = []
    __functions = []
    __buckets = []
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

        logging_management_logs_clients = []
        object_storage_clients = []
        load_balancer_clients = []
        network_load_balancer_clients = []
        network_clients_for_tunnels = []
        functions_management_clients_for_functions = []
        events_clients = []

        regions = get_regions_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name

            logging_management_logs_clients.append((get_logging_management_client(region_config, self.signer),region.region_name, region.region_key.lower()))
            object_storage_clients.append((get_object_storage_client(region_config, self.signer), obj_namespace))
            load_balancer_clients.append(get_load_balancer_client(region_config, self.signer))
            network_load_balancer_clients.append(get_network_load_balancer_client(region_config, self.signer))
            network_clients_for_tunnels.append((get_virtual_network_client(region_config, self.signer),region.region_name, region.region_key.lower()))
            functions_management_clients_for_functions.append((get_functions_management_client(region_config, self.signer), region.region_name, region.region_key.lower()))            
            events_clients.append(get_events_client(region_config, self.signer))      
            
        logging_management_groups_clients = [x[0] for x in logging_management_logs_clients]
        network_clients_for_connections = [x[0] for x in network_clients_for_tunnels]
        functions_management_clients_for_applications = [x[0] for x in functions_management_clients_for_functions]          


        self.__log_groups = ParallelExecutor.executor(logging_management_groups_clients, self.__compartments, ParallelExecutor.get_log_groups, len(self.__compartments), ParallelExecutor.log_groups)   
        self.__logs = ParallelExecutor.executor(logging_management_logs_clients, self.__log_groups, ParallelExecutor.get_logs, len(self.__log_groups), ParallelExecutor.logs)   
        self.__bucket_objects = ParallelExecutor.executor(object_storage_clients, self.__compartments, ParallelExecutor.get_buckets, len(self.__compartments), ParallelExecutor.buckets)
        self.__load_balancers_objects = ParallelExecutor.executor(load_balancer_clients, self.__compartments, ParallelExecutor.get_load_balancers, len(self.__compartments), ParallelExecutor.load_balancers)
        self.__network_load_balancers_objects = ParallelExecutor.executor(network_load_balancer_clients, self.__compartments, ParallelExecutor.get_network_load_balancers, len(self.__compartments), ParallelExecutor.network_load_balancers)
        self.__subnets_objects = ParallelExecutor.executor(network_clients_for_connections, self.__compartments, ParallelExecutor.get_subnets_in_compartments, len(self.__compartments), ParallelExecutor.subnets)
        self.__applications_objects = ParallelExecutor.executor(functions_management_clients_for_applications, self.__compartments, ParallelExecutor.get_applications, len(self.__compartments), ParallelExecutor.applications)
        self.__functions_objects = ParallelExecutor.executor(functions_management_clients_for_functions, self.__applications_objects, ParallelExecutor.get_functions, len(self.__applications_objects), ParallelExecutor.functions)
        self.__ip_sec_connections_objects = ParallelExecutor.executor(network_clients_for_connections, self.__compartments, ParallelExecutor.get_ip_sec_connections, len(self.__compartments), ParallelExecutor.ip_sec_connections)
        self.__ip_sec_tunnels_objects = ParallelExecutor.executor(network_clients_for_tunnels, self.__ip_sec_connections_objects, ParallelExecutor.get_ip_sec_connections_tunnels, len(self.__ip_sec_connections_objects), ParallelExecutor.ip_sec_connections_tunnels)
        self.__events_rules_objects = ParallelExecutor.executor(events_clients, self.__compartments, ParallelExecutor.get_events_rules, len(self.__compartments), ParallelExecutor.events_rules)

        # JSON data to Python dictionary
        self.__extract_dict(self.__buckets, self.__bucket_objects, "Bucket", [])
        self.__extract_dict(self.__load_balancers, self.__load_balancers_objects, "Load Balancer", ["display_name", "lifecycle_state"])
        self.__extract_dict(self.__network_load_balancers, self.__network_load_balancers_objects, "Network Load Balancer", ["display_name", "lifecycle_state"])
        self.__extract_dict(self.__subnets, self.__subnets_objects, "Subnet", ["display_name", "cidr_block", "lifecycle_state"])
        self.__extract_dict(self.__functions, self.__functions_objects, "Function", ["display_name", "lifecycle_state"])
        self.__extract_dict(self.__ip_sec_tunnels, self.__ip_sec_tunnels_objects, "IPSec Tunnel", ["display_name", "lifecycle_state"])
        self.__extract_dict(self.__events_rules, self.__events_rules_objects, "Event", ["display_name", "description", "lifecycle_state"])


    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        self.__check_logs(self.__buckets, dictionary,entry)
        self.__check_logs(self.__load_balancers,dictionary,entry)
        self.__check_logs(self.__network_load_balancers,dictionary,entry)
        self.__check_logs(self.__subnets,dictionary,entry)
        self.__check_logs(self.__functions,dictionary,entry)
        self.__check_logs(self.__ip_sec_tunnels, dictionary,entry)
        self.__check_logs(self.__events_rules, dictionary,entry)

        return dictionary


    def __check_logs(self,resources, dictionary,entry):
        for resource in resources:
            log_enabled = False
            resource_name = None

            if "display_name" in resource.keys():
                resource_name = resource['display_name']
            else:
                resource_name = resource['name']
            for log in self.__logs:
                if log.configuration.source.resource == resource['id']:
                    log_enabled = True
                    break
            if not log_enabled:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(resource)
                dictionary[entry]['failure_cause'].append(f"\"{resource['asset']}(s)\" found without Log Services enabled")
                dictionary[entry]['mitigations'].append(f"Consider enabling Log Service for {resource['asset']}: \"{resource_name}\" in compartment: \"{get_compartment_name(self.__compartments, resource['compartment_id'])}\"")
    

    def __extract_dict(self, destination_list, resource_objects, asset, custom_fields ):
        for element in resource_objects:
            record = {
                "compartment_id": element.compartment_id,
                "id": element.id,
                "asset": asset,
            }
            if asset == "Bucket":
                record['display_name'] = element.name
            for field in custom_fields:
                record[field] = getattr(element, field)

            destination_list.append(record)
