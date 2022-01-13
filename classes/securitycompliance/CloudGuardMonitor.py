# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CloudGuardMonitor.py
# Description: Implementation of class CloudGuardMonitor based on abstract


from common.utils.formatter.printer import debug, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class CloudGuardMonitor(ReviewPoint):

    # Class Variables    
    __tenancy_data_including_cloud_guard = None 
    # __tenancy_data_including_cloud_guard captures tenancy id, name descirption, region key, and cloud guard status
    __identity = None
    __cloud_guard_client = None
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
       self.__cloud_guard_client = get_cloud_guard_client(self.config, self.signer)


    def load_entity(self):   
        
        # Get cloud guard configuration data based on tenancy id
        cloud_guard_data = get_cloud_guard_configuration_data(self.__cloud_guard_client, self.__tenancy.id)
        
        # Record some data of a tenancy and its cloud guard enable status
        tenancy_data_including_cloud_guard = {
            "tenancy_id" : self.__tenancy.id,
            "tenancy_name" : self.__tenancy.name,
            "tenancy_description" : self.__tenancy.description,
            "tenancy_region_key" : self.__tenancy.home_region_key,
            "cloud_guard_enable_stautus" : cloud_guard_data.status
        }
        self.__tenancy_data_including_cloud_guard = tenancy_data_including_cloud_guard
    

    def analyze_entity(self, entry):
        self.load_entity()        
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        
        # Check if Cloud Guard is enable
        if self.__tenancy_data_including_cloud_guard['cloud_guard_enable_stautus'] != 'ENABLED':
            dictionary[entry]['status'] = False
            dictionary[entry]['findings'].append(self.__tenancy_data_including_cloud_guard) 
            dictionary[entry]['failure_cause'].append("Root level of the tenancy does not have Cloud Guard enabled")
            dictionary[entry]['mitigations'].append('Enable Cloud Guard on tenancy: ' + self.__tenancy_data_including_cloud_guard['tenancy_name'])
                                  
        return dictionary