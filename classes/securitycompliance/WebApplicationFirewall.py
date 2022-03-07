# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# WebApplicationFirewall.py
# Description: Implementation of class WebApplicationFirewall based on abstract


from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class WebApplicationFirewall(ReviewPoint):

    # Class Variables
    __identity = None
    __tenancy = None
    __compartments = []
    __load_balancer_objects = []
    __load_balancers = []
    __waf_objects = []
    __waf_lb_ids = []
    
 
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
        
        regions = get_regions_data(self.__identity, self.config)
        
        load_balancer_clients = []
        waf_clients = []

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name

            load_balancer_clients.append(get_load_balancer_client(region_config, self.signer))
            waf_clients.append(get_waf_client(region_config, self.signer))

        self.__load_balancer_objects = ParallelExecutor.executor(load_balancer_clients, self.__compartments, ParallelExecutor.get_load_balancers, len(self.__compartments), ParallelExecutor.load_balancers)

        for load_balancer in self.__load_balancer_objects:
            record = {
                'display_name': load_balancer.display_name,
                'id': load_balancer.id,
                'compartment_id': load_balancer.compartment_id,
                'lifecycle_state': load_balancer.lifecycle_state,
                'time_created': load_balancer.time_created,
            }
            self.__load_balancers.append(record)

        self.__waf_objects = ParallelExecutor.executor(waf_clients, self.__compartments, ParallelExecutor.get_waf_firewalls, len(self.__compartments), ParallelExecutor.waf_firewalls)
        
        for waf in self.__waf_objects:
            if waf.lifecycle_state == "ACTIVE":
                self.__waf_lb_ids.append(waf.load_balancer_id)


    def analyze_entity(self, entry):

        self.load_entity()        
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for load_balancer in self.__load_balancers:
            if load_balancer['id'] not in self.__waf_lb_ids:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(load_balancer)
                dictionary[entry]['failure_cause'].append('Application load balancers should be secured with Web Application Firewall (WAF)')
                dictionary[entry]['mitigations'].append(f"Application load balancer: \"{load_balancer['display_name']}\" located in \"{get_compartment_name(self.__compartments, load_balancer['compartment_id'])}\" has no WAF policies attached to it.")

        return dictionary
