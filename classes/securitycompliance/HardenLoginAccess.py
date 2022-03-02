# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# HardenLoginAccess.py
# Description: Implementation of class HardenLoginAccess based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import ipaddr

class HardenLoginAccess(ReviewPoint):

    # Class Variables
    __identity = None
    __compartments = []
    __sec_list_objects = []
    __non_compliant_sec_list = []
    __nsg_objects = []
    __nsgs = []
    __nsg_rule_objects = []
    __nsg_rules = []
    

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
        core_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            network_clients.append( (get_virtual_network_client(region_config, self.signer), region.region_name, region.region_key.lower()) )

        tenancy = get_tenancy_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, tenancy.id))

        self.__sec_list_objects = ParallelExecutor.executor([x[0] for x in network_clients], self.__compartments, ParallelExecutor.get_security_lists, len(self.__compartments), ParallelExecutor.security_lists)
        self.__nsg_objects = ParallelExecutor.executor([x[0] for x in network_clients], self.__compartments, ParallelExecutor.get_nsgs, len(self.__compartments), ParallelExecutor.nsgs)
        self.__nsg_rule_objects = ParallelExecutor.executor(network_clients, self.__nsg_objects, ParallelExecutor.get_nsg_rules, len(self.__nsg_objects), ParallelExecutor.nsg_rules)

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

        for nsg, rules in self.__nsg_rule_objects:
            for rule in rules:
                nsg_record = {
                    'description': rule.description,
                    'direction': rule.direction,
                    'is_stateless': rule.is_stateless,
                    'protocol': rule.protocol,
                    'source': rule.source,
                    'compartment_id': nsg.compartment_id,    
                    'display_name': nsg.display_name,
                    'nsg_id': nsg.id,
                    'vcn_id': nsg.vcn_id           
                }
                self.__nsg_rules.append(nsg_record)


    def analyze_entity(self, entry):
    
        self.load_entity()    
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        if len(self.__non_compliant_sec_list) > 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Security List contains a wide open \"0.0.0.0/0\" CIDR in ingress rule that needs to be closed")
            for sec_list in self.__non_compliant_sec_list:
                if sec_list not in dictionary[entry]['findings']:
                    dictionary[entry]['findings'].append(sec_list)
                    dictionary[entry]['mitigations'].append(f"Make sure to reduce access and set more granular permissions into: \"{sec_list['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, sec_list['compartment_id'])}\"")

        for nsg in self.__nsg_rules:
            if nsg['direction'] == 'INGRESS' and nsg['protocol'] == 'all': 
                dictionary[entry]['status'] = False
                dictionary[entry]['failure_cause'].append("Security Group contains a wide open \"0.0.0.0/0\" CIDR in ingress rule that needs to be closed")
                if not any(d['display_name'] == nsg['display_name'] for d in dictionary[entry]['findings']):
                    dictionary[entry]['findings'].append(nsg)
                    dictionary[entry]['mitigations'].append(f"Set more granular permissions into: \"{nsg['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, nsg['compartment_id'])}\"")

            if nsg['direction'] == 'INGRESS' and nsg['protocol'] != 'all' and nsg['source'] == '0.0.0.0/0':
                dictionary[entry]['status'] = False
                dictionary[entry]['failure_cause'].append("Security Group contains a wide open \"0.0.0.0/0\" CIDR in ingress rule that needs to be closed")
                if not any(d['display_name'] == nsg['display_name'] for d in dictionary[entry]['findings']):
                    dictionary[entry]['findings'].append(nsg)
                    dictionary[entry]['mitigations'].append(f"Set more granular permissions into: \"{nsg['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, nsg['compartment_id'])}\"")

        return dictionary

