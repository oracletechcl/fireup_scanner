# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ApiKeys.py
# Description: Implementation of class ApiKeys based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import datetime


class ApiKeys(ReviewPoint):

    # Class Variables    
    __users = []
    __user_objects = []
    __users_with_api_keys = []
    __identity = None
    __tenancy = None
    __now = datetime.datetime.now()
    __now_formatted = __now.strftime("%d/%m/%Y %H:%M:%S")



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
            self.__user_objects.append(user)

        self.__users_with_api_keys = ParallelExecutor.executor([self.__identity], self.__user_objects, ParallelExecutor.get_user_with_api_keys, len(self.__user_objects), ParallelExecutor.users_with_api_keys)

        for user, api_keys in self.__users_with_api_keys:
            user_api_records = []
            for api_key in api_keys:
                api_key_record = {
                    'fingerprint': api_key.fingerprint,
                    'inactive_status': api_key.inactive_status,
                    'lifecycle_state': api_key.lifecycle_state,
                    'user_id': api_key.user_id,
                    'time_created': api_key.time_created,  
                }
                user_api_records.append(api_key_record)

            user_record = {
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
                'api_key': user_api_records,
            }

            self.__users.append(user_record)

        return self.__users
        

    def analyze_entity(self, entry):
        self.load_entity()              
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        # Count all of the users inside variable self.__users
        total_user_count = len(self.__users)        
        for user in self.__users:
            if user['api_key'] is not None:
                for api_key in user['api_key']:                   
                    time_created = api_key['time_created']
                    time_now = datetime.datetime.strptime(self.__now_formatted, "%d/%m/%Y %H:%M:%S")
                    time_difference = time_now - time_created.replace(tzinfo=None)                    
                    if time_difference.days > 90 and total_user_count > 5:                        
                        dictionary[entry]['findings'].append(user)
                        dictionary[entry]['status'] = False
                        dictionary[entry]['failure_cause'].append('Users have an API key that is older than 90 days')
                        dictionary[entry]['mitigations'].append('Update API Key: '+str(api_key['fingerprint'])+' of user'+user['name'])
        if total_user_count <= 5:
            for user in self.__users:
                dictionary[entry]['findings'].append(user)
                dictionary[entry]['status'] = False
                dictionary[entry]['failure_cause'].append('Less than 5 users in tenancy have been detected')
            dictionary[entry]['mitigations'].append('Consider creating more users to avoid using a single shared Administrator user for all tasks')
        return dictionary
