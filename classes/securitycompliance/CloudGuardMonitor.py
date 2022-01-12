# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CloudGuardMonitor.py
# Description: Implementation of class CloudGuardMonitor based on abstract


from common.utils.formatter.printer import debug, debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class CloudGuardMonitor(ReviewPoint):

    # Class Variables    
    __compartments = []
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
        compartments = get_compartments_data(self.__identity, self.__tenancy.id)        
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
        counter = 0
        good_policy_list = []
        # check if the policy contains in its statement the word manage and the word family if it does print ok

        # for policy in self.__policies:
        #     for statement in policy['statements']:
        #         if "Administrators".upper() not in statement.upper(): # Drop the word Administrator from statement
        #             if "dynamic-group".upper() not in statement.upper(): # Filter out all dynamic-group based policies
        #                 if "service".upper() not in statement.upper(): # Filter out service policies
        #                     if "group".upper() and "manage".upper() and "family".upper() in statement.upper(): # Check for segregated policies for manage, assigned to specific groups
        #                         if "functions-family".upper() not in statement.upper(): # Filter out functions-family policies as this is mandatory policy in case of functions usage                                    
        #                             counter+=1                 # count the value of a compliant policy
        #                             good_policy_list.append(policy['statements'])
        
        # if counter < 10: #criteria today is above 10 policies, will regard an IAM schema applied. 
        #             dictionary[entry]['status'] = False
        #             dictionary[entry]['findings'].append(policy)
        #             dictionary[entry]['failure_cause'].append("Not enough policies found that are compliant with granularity. A minimum of 10 is considered acceptable")                
        #             dictionary[entry]['mitigations'].append('Increase the amount of granular policies containing \'manage family\' as verbs. Sample: '+str(good_policy_list))                                  
        return dictionary