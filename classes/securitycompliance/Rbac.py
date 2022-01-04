# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Rbac.py
# Description: Implementation of class Rbac based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
from collections import defaultdict


class Rbac(ReviewPoint):

    # Class Variables    
    __compartments = [] 
    __policies = []
    __policies_per_compartment = []
    __identity = None
    __tenancy = None
    __policy_dictionary = defaultdict(list)
    __compartment_count_results = {}
    __no_policy_compartments = {}
    

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
        identity_clients = []
        identity_clients.append(get_identity_client(self.config, self.signer))       
        
        compartments = get_compartments_data(self.__identity, self.__tenancy.id)

        self.__policies_per_compartment = ParallelExecutor.executor([self.__identity], compartments, ParallelExecutor.get_policies_per_compartment, len(compartments), ParallelExecutor.policies)

        for policy in self.__policies_per_compartment:
            policy_record = []
            if len(policy_record) > 0:
                policy_record = [{
                    "compartment_id": policy.compartment_id,
                    "defined_tags": policy.defined_tags,
                    "description": policy.description,
                    "freeform_tags": policy.freeform_tags,
                    "id": policy.id,
                    "lifecycle_state": policy.lifecycle_state,
                    "name": policy.name,
                    "statements": policy.statements,
                    "time_created": policy.time_created,
                    "version_date": policy.version_date
                }]
            self.__policies.append(policy_record)

        for compartment in compartments:
            compartment_record = {
                "compartment_id": compartment.compartment_id,
                "defined_tags": compartment.defined_tags,
                "description": compartment.description,
                "freeform_tags": compartment.freeform_tags,
                "id": compartment.id,
                "lifecycle_state": compartment.lifecycle_state,
                "name": compartment.name,
                "time_created": compartment.time_created,          
            }
            self.__compartments.append(compartment_record)

        for i, compartment in enumerate(compartments):
            self.__policy_dictionary.setdefault(compartment.id, []).append(self.__policies[i])

    def analyze_entity(self, entry):
        entry_check = ['inspect', 'read', 'update', 'manage', 'in compartment']
        
        self.load_entity()    
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        self.__set_compartment_finding_count(entry_check)
        policies_in_root_compartment = self.__get_policies_in_root_compartment()        
                

        for key, value in self.__compartment_count_results.items():
            for compartment in self.__compartments:
                if key == compartment['id']:
                    if value < 5:
                        dictionary[entry]['status'] = False
                        dictionary[entry]['findings'].append(compartment)
                        dictionary[entry]['failure_cause'].append('Not enough granular policies found in compartment')
                        dictionary[entry]['mitigations'].append('Create further granular policies attached to compartment: '+compartment['name']+" Current total policies found: "+str(value))

        
        for key, value in self.__no_policy_compartments.items():
            for compartment in self.__compartments:
                if key == compartment['id']:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['findings'].append(compartment)
                    dictionary[entry]['failure_cause'].append('Not enough granular policies found in compartment')
                    dictionary[entry]['mitigations'].append('Create further granular policies attached to compartment: '+compartment['name']+" Current total policies found: "+str(value))    
        

        if len(policies_in_root_compartment) > 0:
            dictionary[entry]['status']= False
            dictionary[entry]['failure_cause'].append('Root compartment has policies')            
            for policy in policies_in_root_compartment:
                dictionary[entry]['mitigations'].append("Remove policy: " + policy['name']+" from root compartment and attach it to a more specific compartment")
                        
                        
            
        return dictionary


    def __set_compartment_finding_count(self, entry_check):
        for compartment in self.__compartments:
            policy_counter = 0
            no_policy_counter = 0
            for comp_id, policy in self.__policy_dictionary.items():
                if comp_id == compartment['id']:                    
                    for pol in policy: 
                        if len(pol) > 0:
                            for p in pol: 
                                for check in entry_check:
                                    if check.lower() in str(p['statements']).lower():                                        
                                        policy_counter += 1
                                    self.__compartment_count_results[comp_id]=policy_counter
                        else:                            
                            self.__no_policy_compartments[comp_id]=no_policy_counter


    def __get_policies_in_root_compartment(self):
        policies = []
        policy_data = get_policies_data(self.__identity, self.__tenancy.id)
        for policy in policy_data:
            policy_record = {
                "compartment_id": policy.compartment_id,
                "defined_tags": policy.defined_tags,
                "description": policy.description,
                "freeform_tags": policy.freeform_tags,
                "id": policy.id,
                "lifecycle_state": policy.lifecycle_state,
                "name": policy.name,
                "statements": policy.statements,
                "time_created": policy.time_created,
                "version_date": policy.version_date
            }
            policies.append(policy_record)
        
        return policies