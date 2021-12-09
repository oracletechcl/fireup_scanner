# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# InstancePrincipal.py
# Description: Implementation of class InstancePrincipal based on abstract



from common.utils.formatter.printer import debug, debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import re


class InstancePrincipal(ReviewPoint):

    # Class Variables    
    __compartments = []    
    __identity = None
    __tenancy = None
    __compute_client = None
    __dyn_groups_per_tenancy = []
    __instance_principals_from_dyn_grp = []
    __policies = []

    __compartment_ocids = []
    
    

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
       self.__compute_client = get_compute_client(self.config, self.signer)
       self.__tenancy = get_tenancy_data(self.__identity, self.config)


    def load_entity(self):                        

        dyn_groups = get_dynamic_group_data(self.__identity, self.__tenancy.id)
        for group in dyn_groups:
            dyn_group_record = {
                'compartment_id': group.compartment_id,
                'defined_tags': group.defined_tags,
                'description': group.description,
                'freeform_tags': group.freeform_tags,
                'id': group.id,
                'inactive_status': group.inactive_status,
                'lifecycle_state': group.lifecycle_state,
                'matching_rule': group.matching_rule,
                'name': group.name,
                'time_created': group.time_created,
            }
            self.__dyn_groups_per_tenancy.append(dyn_group_record)

        compartments = get_compartments_data(self.__identity, self.__tenancy.id)        
        for compartment in compartments:
            compartment_record = {
                'compartment_id': compartment.id,
                'defined_tags': compartment.defined_tags,
                'description': compartment.description,
                'freeform_tags': compartment.freeform_tags,
                'id': compartment.id,
                'inactive_status': compartment.inactive_status,
                'is_accessible': compartment.is_accessible,
                'lifecycle_state': compartment.lifecycle_state,
                'name': compartment.name,
                'time_created': compartment.time_created,  
                'statements': ""              
            }
            self.__compartments.append(compartment_record)

        policy_data = get_policies_data(self.__identity, self.__tenancy.id)        
        for policy in policy_data:  
            policy_record = {
                "compartment_id": policy.compartment_id,
                "defined_tags": policy.defined_tags,
                "description": policy.description,
                "freeform_tags": policy.freeform_tags,
                "id": policy.id,
                "lifecycle_state": policy.lifecycle_state,
                "name": policy.name,
                "statements": policy.statements,
                "time_created": policy.time_created,
            }
            self.__policies.append(policy_record)               
            
        
       

    def analyze_entity(self, entry):
        instance_principal_entry_check = ['instance.id', 'compartment.oc1']        
        instance_principal_compartment_list  = []
        instance_ocid_list = []
        instance_entry = []       
        self.load_entity()    
        dictionary = ReviewPoint.get_benchmark_dictionary(self)     


        for dyngrp in self.__dyn_groups_per_tenancy:                        
             if instance_principal_entry_check[0] in dyngrp['matching_rule'] or instance_principal_entry_check[1] in dyngrp['matching_rule']:
                 self.__instance_principals_from_dyn_grp.append(dyngrp)

        instance_principal_compartment_list, instance_ocid_list = self.__get_matching_rule_entry_from_dyn_statement()
        for compartment in instance_principal_compartment_list:
           instance_data = get_instances_in_compartment_data(self.__compute_client, compartment)

           for instance in instance_data:
               instance_record = {
                   'id': instance.id,
                   'display_name': instance.display_name,
                   'compartment_id': instance.compartment_id,
               }
               instance_entry.append(instance_record)

        

        
        for compartment in instance_principal_compartment_list:
            for instance in instance_entry:
                if compartment != instance['compartment_id']:                  
                    dictionary[entry]['status'] = False
                    dictionary[entry]['findings'].append(instance)                    
                    dictionary[entry]['mitigations'].append('Create an instance principal that contains instance: '+ instance['display_name'] + ' in compartment: ' + compartment+ " as target")                
        
        dictionary[entry]['failure_cause'].append('Instances detected without proper Instance Principal Configuration')


        return dictionary


    def __get_matching_rule_entry_from_dyn_statement(self):
        instance_principal_compartment = []
        instance_ocid_list = []
        for dyngrp in self.__instance_principals_from_dyn_grp:            
            if "compartment.id" in dyngrp['matching_rule']:
                instance_principal_compartment.append(self.__get_compartment_ocid_from_match_rule(dyngrp['matching_rule']))
            elif "instance.oc1" in dyngrp['matching_rule']:
                instance_ocid_list.append(self.__get_instance_ocid_from_match_rule(dyngrp['matching_rule']))                
        return self.__remove_repeated_from_list(instance_principal_compartment), self.__remove_repeated_from_list(instance_ocid_list)
            
            

    def __get_compartment_ocid_from_match_rule(self, matching_rule):        
        compartment_ocid = re.search(r'\w+\.compartment\.oc1..*[\']', 
         matching_rule).group(0).replace("'","").split(",")[0].split("}")[0]                      
        
        return compartment_ocid
        
    def __get_instance_ocid_from_match_rule(self, matching_rule):
        instance_ocid = re.search(r'\w+\.instance\.oc1..*[\']', 
         matching_rule).group(0).replace("'","").split(",")[0].split("}")[0]            
        
        return instance_ocid


    def __remove_repeated_from_list(self, list_to_clean):
        return list(dict.fromkeys(list_to_clean))