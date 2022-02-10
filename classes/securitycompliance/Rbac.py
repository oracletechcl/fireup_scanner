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
    __root_policies = []
    __compartment_dicts = []
    __policies_per_compartment = []
    __identity = None
    __tenancy = None
    __policy_dictionary = {}
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
        
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        self.__policies_per_compartment = ParallelExecutor.executor([self.__identity], self.__compartments, ParallelExecutor.get_policies, len(self.__compartments), ParallelExecutor.policies)

        for compartment in self.__compartments:
            if "tenancy" not in compartment.id:
                self.__policy_dictionary[compartment.id] = []

        for policy_object in self.__policies_per_compartment:
            policy_record = {
                "compartment_id": policy_object.compartment_id,
                "defined_tags": policy_object.defined_tags,
                "description": policy_object.description,
                "freeform_tags": policy_object.freeform_tags,
                "id": policy_object.id,
                "lifecycle_state": policy_object.lifecycle_state,
                "name": policy_object.name,
                "statements": policy_object.statements,
                "time_created": policy_object.time_created,
                "version_date": policy_object.version_date
            }
            if "tenancy" in policy_record['compartment_id']:
                self.__root_policies.append(policy_record)
            else:
                self.__policy_dictionary[policy_record['compartment_id']].append(policy_record)

        for compartment in self.__compartments:
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
            if "tenancy" not in compartment_record['id']:
                self.__compartment_dicts.append(compartment_record)


    def analyze_entity(self, entry):
        entry_check = ['inspect', 'read', 'update', 'manage', 'in compartment']
        
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        self.__set_compartment_finding_count(entry_check)
        policies_in_root_compartment = self.__root_policies

        for key, value in self.__compartment_count_results.items():
            for compartment in self.__compartment_dicts:
                if key == compartment['id']:
                    if value < 5:
                        dictionary[entry]['status'] = False
                        dictionary[entry]['findings'].append(compartment)
                        dictionary[entry]['failure_cause'].append("Not enough granular policies found in compartment")
                        dictionary[entry]['mitigations'].append(f"Create further granular policies attached to compartment: \"{compartment['name']}\" Current total policies found: \"{value}\"")

        
        for key, value in self.__no_policy_compartments.items():
            for compartment in self.__compartment_dicts:
                if key == compartment['id']:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['findings'].append(compartment)
                    dictionary[entry]['failure_cause'].append("Not enough granular policies found in compartment")
                    dictionary[entry]['mitigations'].append(f"Create further granular policies attached to compartment: \"{compartment['name']}\" Current total policies found: \"{value}\"")
        

        if len(policies_in_root_compartment) > 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Some policies are attached to the root compartment")
            for policy in policies_in_root_compartment:
                dictionary[entry]['mitigations'].append(f"Remove policy \"{policy['name']}\" from root compartment")
                        
        return dictionary


    def __set_compartment_finding_count(self, entry_check):
        for compartment in self.__compartment_dicts:
            policy_counter = 0
            no_policy_counter = 0
            for comp_id, policy_list in self.__policy_dictionary.items():
                if comp_id == compartment['id']:
                    if len(policy_list) > 0:
                        for policy in policy_list:
                            for check in entry_check:
                                if check.lower() in str(policy['statements']).lower():
                                    policy_counter += 1
                                self.__compartment_count_results[comp_id]=policy_counter
                    else:                            
                        self.__no_policy_compartments[comp_id]=no_policy_counter
