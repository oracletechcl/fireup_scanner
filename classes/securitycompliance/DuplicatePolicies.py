# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# DuplicatePolicies.py
# Description: Implementation of class DuplicatePolicies based on abstract

from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class DuplicatePolicies(ReviewPoint):

    # Class Variables    
    __compartments = []
    __policy_objects = []
    __policies = []
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
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        self.__policy_objects = ParallelExecutor.executor([self.__identity], self.__compartments, ParallelExecutor.get_policies, len(self.__compartments), ParallelExecutor.policies)

        for policy in self.__policy_objects:  
            record = {
                "compartment_id": policy.compartment_id,
                "description": policy.description,
                "id": policy.id,
                "lifecycle_state": policy.lifecycle_state,
                "name": policy.name,
                "statements": policy.statements,
                "time_created": policy.time_created,
            }
            self.__policies.append(record)


    def analyze_entity(self, entry):
        self.load_entity()        
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        all_statements = []

        for policy in self.__policies:
            for statement in policy['statements']:
                for seen_policy, seen_statement in all_statements:
                    if statement == seen_statement:
                        dictionary[entry]['status'] = False
                        dictionary[entry]['failure_cause'].append('Duplicate policies found')
                        if seen_policy not in dictionary[entry]['findings']: 
                            dictionary[entry]['findings'].append(seen_policy)
                        if policy not in dictionary[entry]['findings']: 
                            dictionary[entry]['findings'].append(policy)
                        dictionary[entry]['mitigations'].append(f"Policy: \"{policy['name']}\" in compartment: \"{get_compartment_name(self.__compartments, policy['compartment_id'])}\" and policy: \"{seen_policy['name']}\" in compartment: \"{get_compartment_name(self.__compartments, policy['compartment_id'])}\" both contain the same statment: \"{statement}\"")   
                else:
                    all_statements.append( (policy, statement) )

        debug(len(all_statements), "yellow")

        return dictionary
