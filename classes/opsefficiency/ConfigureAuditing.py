# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ConfigureAuditing.py
# Description: Implementation of class ConfigureAuditing based on abstract


from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class ConfigureAuditing(ReviewPoint):

    # Class Variables    
    __tenancy_data = []
    __identity = None
    __audit_client = None
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
       self.__audit_client=get_audit_client(self.config, self.signer)


    def load_entity(self):   
        
        audit_data = get_audit_configuration_data(self.__audit_client,self.__tenancy.id)
        # Record some data of a tenancy and its auditing configuration
        tenancy_data = {
            "tenancy_id" : self.__tenancy.id,
            "tenancy_name" : self.__tenancy.name,
            "tenancy_description" : self.__tenancy.description,
            "tenancy_region_key" : self.__tenancy.home_region_key,
            "audit_retention_period_days": audit_data.retention_period_days
        }
        self.__tenancy_data.append(tenancy_data)
    

    def analyze_entity(self, entry):
        self.load_entity()        
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        
        # Check if audit retention is set to 365 Days
        for tenancy in self.__tenancy_data:
            if tenancy['audit_retention_period_days'] != 365:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(tenancy)
                dictionary[entry]['failure_cause'].append("Audit retention is not set to 365 Days")
                dictionary[entry]['mitigations'].append('Set audit retention to 365 days on tenancy: ' + tenancy['tenancy_name'])
                                  
        return dictionary