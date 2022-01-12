# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# BucketEncryption.py
# Description: Implementation of class BucketEncryption based on abstract



from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor



class BucketEncryption(ReviewPoint):

    # Class Variables
    __identity = None
    __tenancy = None
    __bucket_objects = []
     
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

        obj_client = get_object_storage_client(self.config,self.signer)
        obj_namespace = get_objectstorage_namespace_data(obj_client)

        object_storage_clients = []
        regions = get_regions_data(self.__identity, self.config)

        compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        # get clients from each region 
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            object_storage_clients.append((get_object_storage_client(region_config, self.signer), obj_namespace))
      
        self.__bucket_objects = ParallelExecutor.executor(object_storage_clients, compartments, ParallelExecutor.get_buckets, len(compartments), ParallelExecutor.buckets)     

    def analyze_entity(self, entry):
    
        self.load_entity()     
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        
        for index, bucket in enumerate(self.__bucket_objects):
            if  not bucket.kms_key_id:               
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append({index:bucket.name})
                dictionary[entry]['failure_cause'].append(f'The bucket is by default encrypted using an Oracle-managed master encryption key.')   
                dictionary[entry]['mitigations'].append(f'For bucket: "{bucket.name}" configure your own master encryption key that you store in the Oracle Cloud Infrastructure Vault service and rotate at a schedule that you define.')   

        return dictionary

