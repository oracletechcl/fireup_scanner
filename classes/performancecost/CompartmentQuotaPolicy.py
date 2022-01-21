# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CompartmentQuotaPolicy.py
# Description: Implementation of class CompartmentQuotaPolicy based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor
import re


class CompartmentQuotaPolicy(ReviewPoint):

    # Class Variables
    __compartments = []
    __compartments_with_quotas = []
    __compartments_without_quotas = []
    __identity = None
    __tenancy = None
    __quota_objects = []


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
        quota_clients = []
        home_region = get_home_region(self.__identity, self.config)

        # Get the home region
        home_region_config = self.config
        home_region_config['region'] = home_region.region_name
        quota_clients.append(get_quotas_client(home_region_config, self.signer))
        
        # Get all compartments
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        # Get quota objects using parallel executor
        self.__quota_objects = ParallelExecutor.executor(quota_clients, self.__compartments, ParallelExecutor.get_quotas_in_compartments, len(self.__compartments), ParallelExecutor.quotas)

        # Store compartments with quotas enabled
        for quota in self.__quota_objects:
            self.__compartments_with_quotas.append(quota.compartment_id)

        # compartment_without_quotas = compartments - compartments_with_quotas
        for compartment in self.__compartments:
            if compartment.compartment_id not in self.__compartments_with_quotas:
                compartment_record = {
                    "name": compartment.name,
                    "id": compartment.id,
                    "compartment_id": compartment.compartment_id,
                    "description": compartment.description,
                    "lifecycle_state": compartment.lifecycle_state,
                }
                self.__compartments_without_quotas.append(compartment_record)
        
    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        
        if len(self.__compartments_without_quotas)!= 0:
            dictionary[entry]['status'] = False
            for compartment in self.__compartments_without_quotas:
                dictionary[entry]['findings'].append(compartment)
                dictionary[entry]['failure_cause'].append("Compartments with no configured quota have been detected")
                dictionary[entry]['mitigations'].append("Enable quotas for " + compartment['name'])  

        return dictionary 
