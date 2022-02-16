# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract


from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class DBPermissions(ReviewPoint):

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
            self.__policies.append(record)


    def analyze_entity(self, entry):
        self.load_entity()        
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        policy_body_items = [
            "manage db-systems in tenancy where request.permission!='DB_SYSTEM_DELETE'", 
            "manage databases in tenancy where request.permission!='DATABASE_DELETE'", 
            "manage db-homes in tenancy where request.permission!='DB_HOME_DELETE'"
        ]

        for policy in self.__policies:
            for statement in policy['statements']:
                for body_item in policy_body_items:
                    if body_item in statement:
                        policy_body_items.remove(body_item)

        for body_item in policy_body_items:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Missing policies for Restricting Database deletion have been detected")
            dictionary[entry]['mitigations'].append(f"Add something like the following policies into the tenancy: \"Allow group DBUsers to {body_item}\"")

        return dictionary
