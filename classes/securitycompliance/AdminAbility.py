# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract


from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class AdminAbility(ReviewPoint):

    # Class Variables    
    __compartments = []
    __policies = []
    __policy_objects = []
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
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

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
        counter = 0        
        for policy in self.__policies:
            for statement in policy['statements']:
                if "service".upper() not in statement.upper():                    
                    if "Allow group".upper() in statement.upper():
                        if "to inspect groups in tenancy".upper() in statement.upper():
                            if "Administrator".upper() or "admin".upper() or "adm".upper() or "UserAdmins".upper() in statement.upper():             
                                counter+=1
        
        if counter == 0 : 
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Policy to allow user admins to inspect groups does not exists in tenancy")                
            dictionary[entry]['mitigations'].append("Create a policy \"Allow group UserAdmins to inspect groups in tenancy\"")
        else:
            dictionary[entry]['status'] = True
            dictionary[entry]['findings'].append(policy)  
     
        return dictionary
