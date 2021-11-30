# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract

from common.utils.helpers.helper import *
from common.utils.formatter.printer import debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.statics import Statics




class Mfa(ReviewPoint):

    # Class Variables
    __users = []
    __groups_to_users = []
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
        return self.__users
                

    def analyze_entity(self, entry):
        self.load_entity()       
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        for user in self.__users:
            if user['is_mfa_activated'] == False and user['lifecycle_state'] == 'ACTIVE':
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(user)
                dictionary[entry]['failure_cause'].append('Faulty User:' + user['name'])                
                dictionary[entry]['mitigations'].append('Enable MFA on user: ' + user['name'])                                

        return dictionary

        
        



    