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
    __quotas_data = []
    __identity = None
    __quotas = None


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
        
        # home_region = get_home_region(self.__identity, self.config)

        # region_config = self.config
        # region_config['region'] = home_region.region_name

        # self.__quotas = get_quotas_client(region_config, self.signer)

        # for compartment in compartments:
        #     compartment_record = {
        #         'compartment_id': compartment.id,
        #         'defined_tags': compartment.defined_tags,
        #         'description': compartment.description,
        #         'freeform_tags': compartment.freeform_tags,
        #         'id': compartment.id,
        #         'inactive_status': compartment.inactive_status,
        #         'is_accessible': compartment.is_accessible,
        #         'lifecycle_state': compartment.lifecycle_state,
        #         'name': compartment.name,
        #         'time_created': compartment.time_created,  
        #         'statements': ""              
        #     }
        #     self.__compartments.append(compartment_record)
        
        # quotas_data = list_quota_data(self.__quotas, tenancy.id)

        # for quota in quotas_data:
        #     quota_record = {
        #         'compartment_id': quota.compartment_id,
        #         'defined_tags': quota.defined_tags,
        #         'description': quota.description,
        #         'freeform_tags': quota.freeform_tags,
        #         'id': quota.id,
        #         'lifecycle_state': quota.lifecycle_state,
        #         'name': quota.name,
        #         'time_created': compartment.time_created
        #     }
        #     self.__quotas_data.append(quota_record)
        
        return self.__compartments, self.__quotas_data


    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        # compliant_compartment_names = []
        # all_compartment_names = []
        # compliant_compartment_count = 0

        # for compartments in self.__compartments:
        #     all_compartment_names.append(compartments['name'])
    
        # for quotas_data in self.__quotas_data:
        #     quota_compart = self.__quotas.get_quota(quotas_data['id'])
    
        #     for statement in quota_compart.data.statements:
        #         # Regex that recieves compartment name from quota
        #         compart_name = re.search('(?<=in compartment )(\w+)', statement).group(1)
        #         for compartments in self.__compartments:
        #             if compartments['name'] == compart_name:
        #                 compliant_compartment_count += 1
        #                 compliant_compartment_names.append(compartments['name'])
        #                 break
        #             else:
        #                 continue
        # non_compliant_compartments_names = list(set(all_compartment_names) - set(compliant_compartment_names))

        
        # for compartments in self.__compartments:
        #     for compart in non_compliant_compartments_names:
        #         dictionary[entry]['status'] = False
        #         if compartments['name'] == compart:
        #             dictionary[entry]['findings'].append(compartments)
        #             dictionary[entry]['failure_cause'].append("Compartment name does not have the quota set: " + compart)
        #             dictionary[entry]['mitigations'].append("Please set the quota for : " + compart + " to make it complaint")  
        #             break
        #         else:
        #             continue


        return dictionary 
