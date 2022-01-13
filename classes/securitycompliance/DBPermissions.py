# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract


from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class DBPermissions(ReviewPoint):

    # Class Variables    
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
               
        policy_data = get_policies_data(self.__identity, self.__tenancy.id)      

        for policy in policy_data:  
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
        __db_policy_1 = "Allow group DBUsers to manage db-systems in tenancy where request.permission!=\'DB_SYSTEM_DELETE\'"
        __db_policy_2 = "Allow group DBUsers to manage databases in tenancy where request.permission!=\'DATABASE_DELETE\'"
        __db_policy_3 = "Allow group DBUsers to manage db-homes in tenancy where request.permission!=\'DB_HOME_DELETE\'"

        __criteria_1 = "tenancy where request.permission!='DB_SYSTEM_DELETE'"
        __criteria_2 = "tenancy where request.permission!='DATABASE_DELETE'"
        __criteria_3 = "tenancy where request.permission!='DB_HOME_DELETE'"
        counter = 0        
        for policy in self.__policies:
            for statement in policy['statements']:
                if __criteria_1.upper() in statement.upper() and __criteria_2.upper() in statement.upper() and __criteria_3.upper() in statement.upper():                                        
                    counter+=1
        
        if counter < 1: 
                    dictionary[entry]['status'] = False
                    dictionary[entry]['failure_cause'].append('No Policies for Restricting Database deletion have been detected')                
                    dictionary[entry]['mitigations'].append('Add the following policies into the tenancy to enforce database protection: '+ __db_policy_1 + ' and ' + __db_policy_2 + ' and ' + __db_policy_3)                
        else:
                    dictionary[entry]['status'] = True
                    dictionary[entry]['findings'].append(policy)                    
        return dictionary