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
    __dyn_groups = []
    __instance_principals_from_dyn_grp = []
    __instances_with_instance_principals = []
    __instance_principal_compartment_list = []

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
            self.__dyn_groups.append(dyn_group_record)

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

        
        for dyngrp in self.__dyn_groups:
            if 'compartment.id' in dyngrp['matching_rule']:
                self.__instance_principals_from_dyn_grp.append(dyngrp)

        self.__instance_principal_compartment_list = self.__get_matching_rule_entry_from_dyn_statement()

        regions = get_regions_data(self.__identity, self.config)
        compute_clients = []
        
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            compute_clients.append(get_compute_client(region_config, self.signer))

        if len(self.__instance_principal_compartment_list) > 0:
            self.__instances_with_instance_principals = parallel_executor(compute_clients, self.__instance_principal_compartment_list, self.__search_for_computes, len(self.__instance_principal_compartment_list), "__instances_with_instance_principals")
    

    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for compartment in self.__instance_principal_compartment_list:
            for instance in self.__instances_with_instance_principals:
                if compartment == instance['compartment_id']:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['findings'].append(instance)
                    dictionary[entry]['mitigations'].append('Create an instance principal that contains instance: '+ instance['display_name'] + ' in compartment: ' + compartment+ " as target")
        
        dictionary[entry]['failure_cause'].append('Instances detected without proper Instance Principal Configuration')

        return dictionary


    def __get_matching_rule_entry_from_dyn_statement(self):
        instance_principal_compartment = []
        for dyngrp in self.__instance_principals_from_dyn_grp:
            if "compartment.id" in dyngrp['matching_rule']:
                compartment_ocid = re.search(r"\w+\.compartment\.oc1..*[\']", dyngrp['matching_rule'])

                if compartment_ocid:
                    compartment_ocid = compartment_ocid.group(0).split(',')[0]
                    compartment_ocid = re.sub(r"[\'{}]", "", compartment_ocid)
                    instance_principal_compartment.append(compartment_ocid)

        return self.__remove_repeated_from_list(instance_principal_compartment)

    def __remove_repeated_from_list(self, list_to_clean):
        return list(dict.fromkeys(list_to_clean))


    def __search_for_computes(self, item):
        compute_client = item[0]
        compartments = item[1:]

        instances = []

        for compartment in compartments:
            instance_data = get_instances_in_compartment_data(compute_client, compartment)

            for instance in instance_data:
                instance_record = {
                    'id': instance.id,
                    'display_name': instance.display_name,
                    'compartment_id': instance.compartment_id,
                }

                instances.append(instance_record)

        return instances
