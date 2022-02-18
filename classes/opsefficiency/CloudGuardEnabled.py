# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CloudGuardEnabled.py
# Description: Implementation of class CloudGuardEnabled based on abstract


from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class CloudGuardEnabled(ReviewPoint):

    # Class Variables    
    __cloud_guard_data = None 
    __identity = None
    __cloud_guard_client = None
    __cloud_guard_config = []
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
        self.__cloud_guard_config = get_cloud_guard_configuration_data(self.__cloud_guard_client, self.__tenancy.id)

        if type(self.__cloud_guard_config) == oci.exceptions.ServiceError:
            return

        # Record some data of a tenancy and its cloud guard enable status
        cloud_guard_data = {
            "tenancy_id" : self.__tenancy.id,
            "tenancy_name" : self.__tenancy.name,
            "tenancy_description" : self.__tenancy.description,
            "tenancy_region_key" : self.__tenancy.home_region_key,
            "cloud_guard_enable_stautus" : self.__cloud_guard_config.status
        }
        self.__cloud_guard_data = cloud_guard_data


    def analyze_entity(self, entry):
        self.load_entity()        
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        if type(self.__cloud_guard_config) == oci.exceptions.ServiceError:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Cloud guard is not available in an always free tenancy")
            dictionary[entry]['mitigations'].append(str(self.__cloud_guard_config.message))

            return dictionary

        # Check if Cloud Guard is enable
        if self.__cloud_guard_data['cloud_guard_enable_stautus'] != 'ENABLED':
            dictionary[entry]['status'] = False
            dictionary[entry]['findings'].append(self.__cloud_guard_data) 
            dictionary[entry]['failure_cause'].append("Root level of the tenancy does not have Cloud Guard enabled")
            dictionary[entry]['mitigations'].append("Enable Cloud Guard on tenancy")

        return dictionary
