# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract


from common.utils.formatter.printer import debug, debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import datetime


class ApiKeys(ReviewPoint):

    # Class Variables    
    __users = []
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
        api_key_data = None
        for user in users_data:
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
                    'api_key': []                    
                }
                # load the api key data inside the empty resource api_key[] per each user
                api_key_data = get_api_key_data(self.__identity, user.id)
                for api_key in api_key_data:
                    api_key_record = {
                      'fingerprint': api_key.fingerprint,
                      'inactive_status': api_key.inactive_status,
                      'lifecycle_state': api_key.lifecycle_state,
                      'user_id': api_key.user_id,
                      'time_created': api_key.time_created,  
                    }
                    user_record['api_key'].append(api_key_record)                    
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
                        dictionary[entry]['failure_cause'].append('User: '+user['name']+' has an API key that is older than 90 days')
                        dictionary[entry]['mitigations'].append('Update API Key: '+str(api_key['fingerprint'])+' of user'+user['name'])

        return dictionary