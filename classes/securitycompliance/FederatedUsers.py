# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract


from common.utils.formatter.printer import debug, debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class FederatedUsers(ReviewPoint):

    # Class Variables    
    __users = []
    __identity = None
    __tenancy = None



    def __init__(self, entry, area, sub_area, review_point, status, findings, config, signer):
       self.entry = entry
       self.area = area
       self.sub_area = sub_area
       self.review_point = review_point
       self.status = status
       self.findings = findings

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
                self.__users.append(record)    
        return self.__users
        

    def analyze_entity(self, entry):
        self.load_entity()        
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        # Count all of the users inside variable self.__users
        total_user_count = len(self.__users)
        # count all the users inside self._users that contain the entry identity provider id not null
        none_idp_user_count = 0
        for user in self.__users:
            if user['identity_provider_id'] is None:
                none_idp_user_count += 1                                        
                dictionary[entry]['findings'].append(user)
        
        if none_idp_user_count/total_user_count <= 0.9:
            dictionary[entry]['status'] = False        

        return dictionary