# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# LifecycleManagement.py
# Description: Implementation of class LifecycleManagement based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class LifecycleManagement(ReviewPoint):

    # Class Variables
    __bucket_objects = []
    __bucket_lifecycle_policies = []
    __bucket_lifecycle_policies_dicts = []
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


    def load_entity(self):

        regions = get_regions_data(self.__identity, self.config)

        tenancy = get_tenancy_data(self.__identity, self.config)

        namespace = get_object_storage_client(self.config, self.signer).get_namespace().data

        object_storage_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            object_storage_clients.append( (get_object_storage_client(region_config, self.signer), namespace, region.region_name, region.region_key.lower()) )

        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__bucket_objects = ParallelExecutor.executor(object_storage_clients, self.__compartments, ParallelExecutor.get_buckets, len(self.__compartments), ParallelExecutor.buckets)

        if len(self.__bucket_objects) > 0:
            self.__bucket_lifecycle_policies = ParallelExecutor.executor(object_storage_clients, self.__bucket_objects, ParallelExecutor.get_bucket_lifecycle_policies, len(self.__bucket_objects), ParallelExecutor.bucket_lifecycle_policies)

        for bucket, lifecycle_policies in self.__bucket_lifecycle_policies:
            record = {
                    "compartment_id": bucket.compartment_id,
                    "name": bucket.name,
                    "namespace": bucket.namespace,
                    "id": bucket.id,
                    "created_by": bucket.created_by,
                    "policies": False,
                }
            if lifecycle_policies is not None:
                record['policies'] = True
            self.__bucket_lifecycle_policies_dicts.append(record)

        return self.__bucket_lifecycle_policies_dicts


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for bucket in self.__bucket_lifecycle_policies_dicts:
            if not bucket['policies']:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(bucket)    
                dictionary[entry]['failure_cause'].append("Adds lifecycle policies to each bucket to reduce your storage costs and the amount of time you spend managing data.")                
                dictionary[entry]['mitigations'].append(f"Bucket: \"{bucket['name']}\" in compartment: \"{get_compartment_name(self.__compartments, bucket['compartment_id'])}\" has no lifecycle policies attached to it.")

        return dictionary
