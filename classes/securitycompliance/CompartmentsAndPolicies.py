# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract


from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *



class CompartmentsAndPolicies(ReviewPoint):

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
   
        compartments = get_compartments_data(self.__identity, self.__tenancy.id)        
        for compartment in compartments:
            compartment_record = {
                'compartment_id': compartment.id,
                'defined_tags': compartment.defined_tags,
                'description': compartment.description,
                'freeform_tags': compartment.freeform_tags,
                'id': compartment.id,
                'inactive_status': compartment.inactive_status,
                'is_accessible': compartment.is_accessible,
                'lifecycle_state': compartment.lifecycle_state,
                'name': compartment.name,
                'time_created': compartment.time_created,  
                'statements': ""              
            }
            self.__compartments.append(compartment_record)

        compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__policy_objects = ParallelExecutor.executor([self.__identity], compartments, ParallelExecutor.get_policies, len(compartments), ParallelExecutor.policies)

        for policy in self.__policy_objects:  
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
            }
            self.__policies.append(policy_record)
            
        return self.__compartments, self.__policies
        

    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        env_list = ['prd', 'dev', 'test', 'stage', 'qa', 'sandbox', 'prod', 'tst', 'stg', 'quality', 'sbx', 'sand', 'hub', 'hom']
        compliant_compartment_names = []

        for compartment in self.__compartments:
            compartment_name = compartment['name']
            for env in env_list:
                if env.lower() in compartment['name'].lower():
                    compliant_compartment_names.append(compartment_name)
                    break
            else:
                dictionary[entry]['status'] = False
                dictionary[entry]['failure_cause'].append(f"Some compartment names do not match environment name convention containing these keywords: {env_list}")
                dictionary[entry]['mitigations'].append(f"Rename compartment: \"{compartment_name}\" to match the environment name convention")
      
        if len(compliant_compartment_names) < 2:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Not enough compliant compartments (2) are present within the tenancy.")

        # Policy Analysis
        for policy in self.__policies:
            if policy['compartment_id'] == self.__tenancy.id:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(policy)
                dictionary[entry]['failure_cause'].append("Some policies are attached to the root compartment")
                dictionary[entry]['mitigations'].append(f"Remove policy \"{policy['name']}\" from root compartment")                

        return dictionary
