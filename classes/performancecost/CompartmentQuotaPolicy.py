# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CompartmentQuotaPolicy.py
# Description: Implementation of class CompartmentQuotaPolicy based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
import re


class CompartmentQuotaPolicy(ReviewPoint):

    # Class Variables
    __compartments = []
    __compartments_with_quotas = []
    __identity = None
    __quota_client = None


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
        

    def load_entity(self):
        tenancy = get_tenancy_data(self.__identity, self.config)
        compartments = get_compartments_data(self.__identity, tenancy.id)

        # Get quota client based on region
        home_region=get_home_region(self.__identity, self.config).region_name
        config_with_region=self.config
        config_with_region['region'] = home_region
        self.__quota_client = get_quotas_client(config_with_region, self.signer)

        # Get basic information of a compartment
        for compartment in compartments:
            compartment_record = {
                'compartment_id': compartment.compartment_id,
                'name': compartment.name,
                'description': compartment.description,
                'id': compartment.id,
                'inactive_status': compartment.inactive_status,
                'lifecycle_state': compartment.lifecycle_state
            }
            self.__compartments.append(compartment_record)
        quotas = list_quota_data(self.__quota_client, tenancy.id)

        for quota_compartment_id in quotas:
            self.__compartments_with_quotas.append(quota_compartment_id.compartment_id)
        return self.__compartments, self.__compartments_with_quotas


    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        compartments_without_quotas = []
        for compartment in self.__compartments:
            if compartment['compartment_id'] not in self.__compartments_with_quotas:
                compartments_without_quotas.append(compartment)
        
        if len(compartments_without_quotas)!= 0:
            dictionary[entry]['status'] = False
            for no_quota_compartment in compartments_without_quotas:
                dictionary[entry]['findings'].append(no_quota_compartment)
                dictionary[entry]['failure_cause'].append("The compartment has no enabled quotas")
                dictionary[entry]['mitigations'].append("Set the quota for " + no_quota_compartment['name'] + " with id: " + no_quota_compartment['compartment_id'])  

        return dictionary 
