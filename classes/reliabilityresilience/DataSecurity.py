# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# DataSecurity.py
# Description: Implementation of class DataSecurity based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class DataSecurity(ReviewPoint):

    # Class Variables
    __instance_objects = []
    __instances = []
    __policy_objects = []
    __policies = []
    __compartments = []
    __identity = None

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
        regions = get_regions_data(self.__identity, self.config)
        compute_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            compute_clients.append(get_compute_client(region_config, self.signer))

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__instance_objects = ParallelExecutor.executor(compute_clients, self.__compartments, ParallelExecutor.get_instances, len(self.__compartments), ParallelExecutor.instances)

        for instance in self.__instance_objects:
            instance_record = {
                'id': instance.id,
                'display_name': instance.display_name,
                'compartment_id': instance.compartment_id,
                'lifecycle_state': instance.lifecycle_state,
                'launch_options': instance.launch_options,
                'time_created': instance.time_created,
            }
            self.__instances.append(instance_record)

        self.__policy_objects = ParallelExecutor.executor([self.__identity], self.__compartments, ParallelExecutor.get_policies, len(self.__compartments), ParallelExecutor.policies)     

        for policy in self.__policy_objects:
            record = {
                "compartment_id": policy.compartment_id,
                "defined_tags": policy.defined_tags,
                "description": policy.description,
                "freeform_tags": policy.freeform_tags,
                "id": policy.id,
                "lifecycle_state": policy.lifecycle_state,
                "name": policy.name,
                "statements": policy.statements,
                "time_created": policy.time_created,
                "version_date": policy.version_date
            }
            self.__policies.append(record)

        return self.__instances, self.__policies


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        # Checks in transit encryption is enabled per instance
        for instance in self.__instances:
            if not instance['launch_options'].is_pv_encryption_in_transit_enabled:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(instance)
                dictionary[entry]['failure_cause'].append("Instances detected without in-transit encryption between boot volume and instance.")
                dictionary[entry]['mitigations'].append(f"Instance: \"{instance['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, instance['compartment_id'])}\" does not have in-transit encryption enabled.")

        # Checks a policy exists relating to each of the following families
        __criteria = ["file-family", "object-family", "volume-family", "autonomous-database-family", "database-family"]

        for policy in self.__policies:
            for statement in policy['statements']:
                for criteria in __criteria:
                    if criteria.lower() in statement.lower():
                        __criteria.remove(criteria)

        for criteria in __criteria:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Add missing policies for providing granular access controls for your data and its backups.")
            dictionary[entry]['mitigations'].append(f"Add a policy for managing the family: \"{criteria}\"")

        return dictionary
