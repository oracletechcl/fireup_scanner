# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract

from common.utils.helpers.Helper import *
from common.utils.formatter.printer import debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
import oci


class Mfa(ReviewPoint):

    # Class Variables
    __users = []
    __groups_to_users = []



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
       try:
        self.__identity = oci.identity.IdentityClient(
        self.config, signer=self.signer)
        self.__tenancy = self.__identity.get_tenancy(
                config["tenancy"]).data
       except Exception as e:
           raise RuntimeError("Failed to create identity client: {}".format(e))

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
         if user['external_identifier'] is None and not(user['is_mfa_activated']) and user['lifecycle_state'] == 'ACTIVE':
             dictionary[entry]['status'] = False
             dictionary[entry]['findings'].append(user)
        return dictionary

        
        



    