# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# TenancyQuotas.py
# Description: Implementation of class TenancyQuotas based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
import re


class TenancyQuotas(ReviewPoint):

    # Class Variables
    __compartments = []
    __quotas_data = []
    __identity = None
    __quotas_client = None


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
        
        # Create quotas client in home region
        home_region = get_home_region(self.__identity, self.config)
        region_config = self.config
        region_config['region'] = home_region.region_name
        self.__quotas_client = get_quotas_client(region_config, self.signer)

        for compartment in compartments:
            compartment_record = {
                'compartment_id': compartment.id,
                'description': compartment.description,
                'id': compartment.id,
                'lifecycle_state': compartment.lifecycle_state,
                'name': compartment.name,
            }
            self.__compartments.append(compartment_record)
        
        quotas_data = list_quota_data(self.__quotas_client, tenancy.id)

        for quota in quotas_data:
            quota_record = {
                'compartment_id': quota.compartment_id,
                'description': quota.description,
                'id': quota.id,
                'lifecycle_state': quota.lifecycle_state,
                'name': quota.name,
            }
            self.__quotas_data.append(quota_record)
        
        return self.__compartments, self.__quotas_data


    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        # Create copy of compartments
        non_compliant_compartments = self.__compartments[:]
    
        for quota_data in self.__quotas_data:
            quota_policy_data = get_quota_policy_data(self.__quotas_client, quota_data['id'])
            for statement in quota_policy_data.statements:
                # Regex that recieves compartment name from quota
                quoata_compartment_name = re.search('(?<=in compartment )(\w+)', statement).group(1)
                for compartment in non_compliant_compartments:
                    if compartment['name'] == quoata_compartment_name:
                        non_compliant_compartments.remove(compartment)
                        break

        for compartment in non_compliant_compartments:
            dictionary[entry]['status'] = False
            dictionary[entry]['findings'].append(compartment)
            dictionary[entry]['failure_cause'].append("Some compartments do not have quota(s) set")
            dictionary[entry]['mitigations'].append(f"Please set quota(s) for compartment: \"{compartment['name']}\"")  
  
        return dictionary
