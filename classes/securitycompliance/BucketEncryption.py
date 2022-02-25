# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# BucketEncryption.py
# Description: Implementation of class BucketEncryption based on abstract


from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor
import datetime



class BucketEncryption(ReviewPoint):

    # Class Variables
    __identity = None
    __tenancy = None
    __bucket_objects = []
    __bucket_dicts = []
    __compartments = []
    __now = datetime.datetime.now()
    __now_formatted = __now.strftime("%d/%m/%Y %H:%M:%S")

     
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
        kms_management_clients = []
        regions = get_regions_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        # get clients from each region 
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            object_storage_clients.append((get_object_storage_client(region_config, self.signer), obj_namespace))
        
        self.__bucket_objects = ParallelExecutor.executor(object_storage_clients, self.__compartments, ParallelExecutor.get_buckets, len(self.__compartments), ParallelExecutor.buckets)     

        for bucket in self.__bucket_objects:
            record = {
                "compartment_id": bucket.compartment_id,
                "id": bucket.id,
                "kms_key_id": bucket.kms_key_id,
                "name": bucket.name,
            }
            self.__bucket_dicts.append(record)


    def analyze_entity(self, entry):
    
        self.load_entity()     
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
                      
        for bucket in self.__bucket_dicts:
            if not bucket['kms_key_id']:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(bucket)
                dictionary[entry]['failure_cause'].append("The bucket is by default encrypted using an Oracle-managed master encryption key.")   
                dictionary[entry]['mitigations'].append(f"For bucket: \"{bucket['name']}\" in compartment: \"{get_compartment_name(self.__compartments, bucket['compartment_id'])}\" configure your own master encryption key that you store in the Oracle Cloud Infrastructure Vault service and rotate at a schedule that you define.") 
            else:
                kms_namespace = bucket['kms_key_id'].split(".")[4]
                kms_region_key = bucket['kms_key_id'].split(".")[3]
                kms_management_endpoint = "https://" + kms_namespace + "-management.kms." + kms_region_key + ".oraclecloud.com" 
                kms_client = get_kms_management_client(self.config, kms_management_endpoint, self.signer)
                kms_key = get_kms_key_info(kms_client,bucket['kms_key_id'])
                key_version = get_key_versions(kms_client,bucket['kms_key_id'])
                for version in key_version:
                    if kms_key.current_key_version == version.id:
                        time_created = version.time_created
                        time_now = datetime.datetime.strptime(self.__now_formatted, "%d/%m/%Y %H:%M:%S")
                        time_difference = time_now - time_created.replace(tzinfo=None)
                        if time_difference.days > 90:
                            dictionary[entry]['status'] = False
                            dictionary[entry]['findings'].append(bucket)
                            dictionary[entry]['failure_cause'].append("The KMS Key of a bucket or more is older than 90 days")
                            dictionary[entry]['mitigations'].append(f"Update KMS Key of bucket: \"{bucket['name']}\" located in compartment: \"{get_compartment_name(self.__compartments, bucket['compartment_id'])}\" in region: \"{kms_region_key}\"")

        return dictionary
