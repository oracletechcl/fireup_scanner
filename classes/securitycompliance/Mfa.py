# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract

from common.utils.helpers.helper import *
from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *


class Mfa(ReviewPoint):

    # Class Variables
    __users = []
    __groups_to_users = []
    __compartments = []
    __identity = None
    __tenancy = None
    __policy_objects = []
    __policies = []


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
        users_data = get_user_data(self.__identity, self.__tenancy.id)        
        for user in users_data:
                record = {
                    'id': user.id,
                    'defined_tags': user.defined_tags,
                    'description': user.description,
                    'email': user.email,
                    'email_verified': user.email_verified,
                    'external_identifier': user.external_identifier,
                    'identity_provider_id': user.identity_provider_id,
                    'is_mfa_activated': user.is_mfa_activated,
                    'lifecycle_state': user.lifecycle_state,
                    'time_created': user.time_created,
                    'name': user.name,
                    'groups': []
                }
                # Adding Groups to the user
                for group in self.__groups_to_users:
                    if user.id == group['user_id']:
                        record['groups'].append(group['name'])                                                     

                self.__users.append(record)

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        sself.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

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


        return self.__users
                

    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        counter = 0
        __criteria_1 = "in tenancy where request.user.mfaTotpVerified='true'"
        
        for user in self.__users:
            if user['is_mfa_activated'] == False and user['lifecycle_state'] == 'ACTIVE':
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(user)
                dictionary[entry]['failure_cause'].append("User does not have MFA activated")
                dictionary[entry]['mitigations'].append(f"Enable MFA on user: \"{user['name']}\"")

        for policy in self.__policies:
            for statement in policy['statements']:
                if __criteria_1.upper() in statement.upper():
                    counter+=1


        if counter < 1: 
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("No Policies for enforcing MFA have been detected")
            dictionary[entry]['mitigations'].append("Add the following policies into the tenancy to enforce MFA: \"allow group GroupA to manage instance-family in tenancy where request.user.mfaTotpVerified=\'true\'\"")                          

        return dictionary
