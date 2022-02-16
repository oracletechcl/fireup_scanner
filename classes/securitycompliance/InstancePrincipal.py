# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# InstancePrincipal.py
# Description: Implementation of class InstancePrincipal based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import re


class InstancePrincipal(ReviewPoint):

    # Class Variables
    __identity = None
    __tenancy = None
    __compartments = []
    __dyn_groups = []
    __instances = []
    __instance_objects = []
    __dyn_groups_with_inst_prins = []
    __inst_prin_compartment_id_list = []
    __inst_prin_instance_id_list = []


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
        
        for dyngrp in self.__dyn_groups:
            if 'compartment.id' in dyngrp['matching_rule'] or 'instance.id' in dyngrp['matching_rule']:
                self.__dyn_groups_with_inst_prins.append(dyngrp)

        self.__inst_prin_compartment_id_list, self.__inst_prin_instance_id_list = self.__get_matching_rule_entry_from_dyn_statement()

        regions = get_regions_data(self.__identity, self.config)
        compute_clients = []
        
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            compute_clients.append(get_compute_client(region_config, self.signer))

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        self.__instance_objects = ParallelExecutor.executor(compute_clients, self.__compartments, ParallelExecutor.get_instances, len(self.__compartments), ParallelExecutor.instances)

        for instance in self.__instance_objects:
            instance_record = {
                'id': instance.id,
                'display_name': instance.display_name,
                'compartment_id': instance.compartment_id,
                'lifecycle_state': instance.lifecycle_state,
            }
            self.__instances.append(instance_record)
    

    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for instance in self.__instances:
            if instance['id'] not in self.__inst_prin_instance_id_list:
                if instance['compartment_id'] not in self.__inst_prin_compartment_id_list:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['findings'].append(instance)
                    dictionary[entry]['mitigations'].append(f"Consider creating an instance principal that contains instance: \"{instance['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, instance['compartment_id'])}\" as the target")
                    dictionary[entry]['failure_cause'].append("Instances detected without proper Instance Principal Configuration")

        return dictionary


    def __get_matching_rule_entry_from_dyn_statement(self):
        instance_principal_compartments = []
        instance_principal_instances = []
        for dyngrp in self.__dyn_groups_with_inst_prins:
            if "compartment.id" in dyngrp['matching_rule']:
                compartment_ocid = re.search(r"\w+\.compartment\.oc1..*[\']", dyngrp['matching_rule'])

                if compartment_ocid:
                    compartment_ocid = compartment_ocid.group(0).split(',')[0]
                    compartment_ocid = re.sub(r"[\'{}]", "", compartment_ocid)
                    instance_principal_compartments.append(compartment_ocid)
            
            if "instance.id" in dyngrp['matching_rule']:
                instance_ocid = re.search(r"\w+\.instance\.oc1..*[\']", dyngrp['matching_rule'])

                if instance_ocid:
                    instance_ocid = instance_ocid.group(0).split(',')[0]
                    instance_ocid = re.sub(r"[\'{}]", "", instance_ocid)
                    instance_principal_instances.append(instance_ocid)

        return self.__remove_repeated_from_list(instance_principal_compartments), self.__remove_repeated_from_list(instance_principal_instances)


    def __remove_repeated_from_list(self, list_to_clean):
        return list(dict.fromkeys(list_to_clean))
