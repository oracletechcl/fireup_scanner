# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Secrets.py
# Description: Implementation of class Secrets based on abstract



from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class Secrets(ReviewPoint):

    # Class Variables
    __secrets_objects = []
    __secrets = []

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

        vaults_clients = []
        regions = get_regions_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        # get clients from each region 
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            vaults_clients.append(get_vaults_client(region_config, self.signer))

        self.__secrets_objects = ParallelExecutor.executor(vaults_clients, self.__compartments, ParallelExecutor.get_secrets, len(self.__compartments), ParallelExecutor.secrets)

        for secret  in self.__secrets_objects:  
            record = {
                "secret_name": secret.secret_name,
                "compartment_id": secret.compartment_id,
                "description": secret.description,
                "id": secret.id,
                "secret_rules": secret.secret_rules
            }
            self.__secrets.append(record)

        
    def analyze_entity(self, entry):

        self.load_entity()        
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for secret in self.__secrets:
            if not secret['secret_rules']:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(secret) 
                dictionary[entry]['failure_cause'].append("Secrets Reuse and Expiry Rules are not defined")                                            
                dictionary[entry]['mitigations'].append(f"For Secret: \"{secret['secret_name']}\" in compartment:\"{get_compartment_name(self.__compartments, secret['compartment_id'])}\" define Reuse and Expiry Rules.")     
            # Overall there are only 2 rules to define,
            # below check if one is missing and advice accordingly
            elif len(secret['secret_rules']) == 1:
                missing_rule = ''
                if secret['secret_rules'][0].rule_type != 'SECRET_EXPIRY_RULE':
                    missing_rule = 'Expiry Rule'
                else:
                    missing_rule = 'Reuse Rule'
                    
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(secret) 
                dictionary[entry]['failure_cause'].append(f"Secret {missing_rule} is not defined")                                            
                dictionary[entry]['mitigations'].append(f"For Secret: \"{secret['secret_name']}\" in compartment:\"{get_compartment_name(self.__compartments, secret['compartment_id'])}\" define {missing_rule}.")    

        return dictionary
