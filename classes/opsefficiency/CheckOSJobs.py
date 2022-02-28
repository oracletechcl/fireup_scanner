# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CheckOSJobs.py
# Description: Implementation of class CheckOSJobs based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class CheckOSJobs(ReviewPoint):

    # Class Variables
    __identity = None
    __compartments = None
    __compute_objects = []
    __computes_dicts = []
    __managed_instance_objects = []
    __manages_instance_dicts = []


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

        compute_clients = []
        os_management_clients = []

        regions = get_regions_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name

            compute_clients.append(get_compute_client(region_config, self.signer))
            os_management_clients.append(get_os_management_client(region_config, self.signer))

        self.__compute_objects = ParallelExecutor.executor(compute_clients, self.__compartments, ParallelExecutor.get_compute_instances, len(self.__compartments), ParallelExecutor.compute_instances)
        self.__managed_instance_objects = ParallelExecutor.executor(os_management_clients, self.__compartments, ParallelExecutor.get_managed_instances, len(self.__compartments), ParallelExecutor.managed_instances)
        
        for compute in self.__compute_objects:
            record = {
                'display_name': compute.display_name,
                'id': compute.id,
                'lifecycle_state': compute.lifecycle_state,
                'compartment_id': compute.compartment_id,
            }
            self.__computes_dicts.append(record)
            
        for managed_instance in self.__managed_instance_objects:
            record = {
                'display_name': managed_instance.display_name,
                'id': managed_instance.id,
                'updates_available': managed_instance.updates_available,
                'status': managed_instance.status,
                'compartment_id': managed_instance.compartment_id,
            }
            self.__manages_instance_dicts.append(record)
    

    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for compute in self.__computes_dicts:
            for managed_instance in self.__manages_instance_dicts:
                if compute['id'] == managed_instance['id']:
                    # Check no updates need to be applied - if they do log the instance
                    if managed_instance['updates_available'] != 0:
                        dictionary[entry]['status'] = False
                        dictionary[entry]['findings'].append(compute)
                        dictionary[entry]['failure_cause'].append("Compute instances require updates")                                   
                        dictionary[entry]['mitigations'].append(f"Apply updates to instance: \"{compute['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, compute['compartment_id'])}\"")
                    break
            else:
                # Log instances without OS Management enabled
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(compute)
                dictionary[entry]['failure_cause'].append("Compute found without OS Management enabled")                                   
                dictionary[entry]['mitigations'].append(f"Enable OS management for instance: \"{compute['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, compute['compartment_id'])}\"")
                pass

        return dictionary
