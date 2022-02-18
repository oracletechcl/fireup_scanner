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
    __root_compartment = []
    __root_policies = []
    __compartment_policies = []
    __compartment_policy_objects = []
    __root_policy_objects = []
    __policies_by_compartment = []
    __compartment_dicts = []
    __identity = None
    __tenancy = None
    

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
        
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__root_compartment = get_root_compartment_data(self.__identity, self.__tenancy.id)

        self.__compartment_policy_objects = ParallelExecutor.executor([self.__identity], self.__compartments, ParallelExecutor.get_policies, len(self.__compartments), ParallelExecutor.policies)
        self.__root_policy_objects = get_policies_data(self.__identity,self.__root_compartment.id) 
        
        for compartment in self.__compartments:
            record = {
                "compartment_id": compartment.compartment_id,
                "defined_tags": compartment.defined_tags,
                "description": compartment.description,
                "freeform_tags": compartment.freeform_tags,
                "id": compartment.id,
                "lifecycle_state": compartment.lifecycle_state,
                "name": compartment.name,
                "time_created": compartment.time_created,
            }
            self.__compartment_dicts.append(record)


        for policy in self.__root_policy_objects:            
            record = {
                "compartment_id": policy.compartment_id,
                "defined_tags": policy.defined_tags,
                "description": policy.description,
                "freeform_tags": policy.freeform_tags,
                "id": policy.id,
                "lifecycle_state": policy.lifecycle_state,
                "name": policy.name,
                "statements": policy.statements,
                "time_created": policy.time_created,
            }
            self.__root_policies.append(record)
        
        
        self.__policies_by_compartment = {}

        for policy in self.__compartment_policy_objects:
            current_compartment_id = policy.compartment_id
            
            if not current_compartment_id in self.__policies_by_compartment.keys():
                self.__policies_by_compartment[current_compartment_id]= []
            
            record = {
                "defined_tags": policy.defined_tags,
                "description": policy.description,
                "freeform_tags": policy.freeform_tags,
                "id": policy.id,
                "lifecycle_state": policy.lifecycle_state,
                "name": policy.name,
                "statements": policy.statements,
            }
            self.__policies_by_compartment[current_compartment_id].append(record)
            
    def analyze_entity(self, entry):

        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        if len(self.__root_policies) != 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Some policies are attached to the root compartment")
            for policy in self.__root_policies:
                dictionary[entry]['mitigations'].append(f"Remove policy \"{policy['name']}\" from root compartment")

        compliant_compartments = []
        for compartment_id, policies in self.__policies_by_compartment.items():
            compliant_compartments.append(compartment_id)
            counter = 0
            for policy in policies:
                for statement in policy['statements']:
                    if 'in compartment' in statement:
                        counter += 1

            if counter < 5:
                for compartment in self.__compartment_dicts:
                    if compartment_id == compartment['id']:
                        dictionary[entry]['status'] = False
                        dictionary[entry]['findings'].append(compartment)
                        dictionary[entry]['failure_cause'].append("Not enough granular policies found in compartment")
                        dictionary[entry]['mitigations'].append(f"Create further granular policies attached to compartment: \"{compartment['name']}\" Current total policies found: \"{counter}\"")
        
        for compartment in self.__compartment_dicts:
            if compartment['id'] not in compliant_compartments:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(compartment)
                dictionary[entry]['failure_cause'].append("No granular policies found in compartment")
                dictionary[entry]['mitigations'].append(f"Create granular policies for compartment: \"{compartment['name']}\" Current total policies were found to be 0.")
                      
        return dictionary
