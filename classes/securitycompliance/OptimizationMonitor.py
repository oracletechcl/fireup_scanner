# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# OptimizationMonitor.py
# Description: Implementation of class OptimizationMonitor based on abstract


from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor


class OptimizationMonitor(ReviewPoint):

    # Class Variables    
    __tenancy_data_including_cloud_guard = None
    __identity = None
    __cloud_guard_client = None
    __tenancy = None
    __detector_recipes_data = []
    __responder_recipes_data = []
    __non_compliant_detector_rules = []
    __non_compliant_responder_rules = []
    __detector_recipes_with_rules_data = None 
    __responder_recipes_with_rules_data = None 

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
        compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

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

        home_region = get_home_region(self.__identity, self.config)

        region_config = self.config
        region_config['region'] = home_region.region_name
        self.__cloud_guard_client = [get_cloud_guard_client(region_config, self.signer)]

        # get tenancy and rules data
        self.__tenancy_data_including_cloud_guard = tenancy_data_including_cloud_guard
        self.__detector_recipes_data = ParallelExecutor.executor(self.__cloud_guard_client, compartments, ParallelExecutor.get_detector_recipes, len(compartments), ParallelExecutor.detector_recipes)
        self.__responder_recipes_data = ParallelExecutor.executor(self.__cloud_guard_client, compartments, ParallelExecutor.get_responder_recipes, len(compartments), ParallelExecutor.responder_recipes)

        if len(self.__detector_recipes_data) > 0:
            self.__detector_recipes_with_rules_data = ParallelExecutor.executor(self.__cloud_guard_client, self.__detector_recipes_data, ParallelExecutor.get_detector_rules, len(self.__detector_recipes_data), ParallelExecutor.detector_recipes_with_rules)
        
        if len(self.__responder_recipes_data) > 0:
            self.__responder_recipes_with_rules_data = ParallelExecutor.executor(self.__cloud_guard_client, self.__responder_recipes_data, ParallelExecutor.get_responder_rules, len(self.__responder_recipes_data), ParallelExecutor.responder_recipes_with_rules)
        
        for recipe_with_rules in self.__detector_recipes_with_rules_data:
            if recipe_with_rules[0].owner == "CUSTOMER":
                recipe_record = {
                    'display_name': recipe_with_rules[0].display_name,
                    'id': recipe_with_rules[0].id,
                    'owner': recipe_with_rules[0].owner,
                    'lifecycle_state': recipe_with_rules[0].lifecycle_state,
                    'description': recipe_with_rules[0].description,
                }
                for rule in recipe_with_rules[1]:
                    if not rule.detector_details.is_enabled:
                        rule_record = {
                            'display_name': rule.display_name,
                            'description': rule.description,
                            'id': rule.id,
                            'service_type': rule.service_type,
                            'resource_type': rule.resource_type,
                            'detector': rule.detector,
                            'risk_level': rule.detector_details.risk_level,
                            'detector_details': rule.detector_details,
                        }
                        self.__non_compliant_detector_rules.append( (recipe_record, rule_record) )

        for recipe_with_rules in self.__responder_recipes_with_rules_data:
            if recipe_with_rules[0].owner == "CUSTOMER":
                recipe_record = {
                    'display_name': recipe_with_rules[0].display_name,
                    'id': recipe_with_rules[0].id,
                    'owner': recipe_with_rules[0].owner,
                    'lifecycle_state': recipe_with_rules[0].lifecycle_state,
                    'description': recipe_with_rules[0].description,
                }
                for rule in recipe_with_rules[1]:
                    if not rule.details.is_enabled:
                        rule_record = {
                            'display_name': rule.display_name,
                            'description': rule.description,
                            'id': rule.id,
                            'details': rule.details,
                        }
                        self.__non_compliant_responder_rules.append( (recipe_record, rule_record) )

        
    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
   
        # Check if Cloud Guard and Rules are enabled
        if self.__tenancy_data_including_cloud_guard['cloud_guard_enable_stautus'] == 'ENABLED':
            
                for rule in self.__non_compliant_detector_rules:                    
                    dictionary[entry]['status'] = False
                    if rule[0] not in dictionary[entry]['findings']:
                        dictionary[entry]['findings'].append(rule[0])                    
                    dictionary[entry]['failure_cause'].append("Cloud Guard detector rule not correctly configured")
                    dictionary[entry]['mitigations'].append("Enable Detector rule: "+rule[1]['display_name']+" associated to recipe: "+rule[0]['display_name'])

                for rule in self.__non_compliant_responder_rules:                   
                    dictionary[entry]['status'] = False
                    if rule[0] not in dictionary[entry]['findings']:
                        dictionary[entry]['findings'].append(rule[0])                    
                    dictionary[entry]['failure_cause'].append("Cloud Guard responder rule not correctly configured")
                    dictionary[entry]['mitigations'].append("Enable Response rule: "+rule[1]['display_name']+" associated to recipe: "+rule[0]['display_name'])  
        else:
            dictionary[entry]['status'] = False
            dictionary[entry]['findings'].append(self.__tenancy_data_including_cloud_guard) 
            dictionary[entry]['failure_cause'].append("Cloud Gaurd is not enabled")
            dictionary[entry]['mitigations'].append('Enable Cloud Guard in tenancy: ' + self.__tenancy_data_including_cloud_guard['tenancy_name'])                    
        
                                  
        return dictionary