# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# BucketPermissions.py
# Description: Implementation of class BucketPermissions based on abstract



from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from datetime import datetime




class BucketPermissions(ReviewPoint):

    # Class Variables
    __identity = None
    __tenancy = None
    __compartments = []
    __policy_objects = []
    __policies = []
    __bucket_objects = []
    __buckets = []
    __par_data = {}
 
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
        par_object_storage_clients = []
        regions = get_regions_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        # get clients from each region 
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            object_storage_clients.append((get_object_storage_client(region_config, self.signer), obj_namespace))
            par_object_storage_clients.append((get_object_storage_client(region_config, self.signer),obj_namespace, region.region_name, region.region_key.lower()))
      
        self.__bucket_objects = ParallelExecutor.executor(object_storage_clients, self.__compartments, ParallelExecutor.get_buckets, len(self.__compartments), ParallelExecutor.buckets)

        for bucket in self.__bucket_objects:
            record = {
                    "approximate_count": bucket.approximate_count,
                    "approximate_size": bucket.approximate_size,
                    "auto_tiering": bucket.auto_tiering,
                    "compartment_id": bucket.compartment_id,
                    "created_by": bucket.created_by,
                    "defined_tags": bucket.defined_tags,
                    "etag": bucket.etag,
                    "freeform_tags": bucket.freeform_tags,
                    "id": bucket.id,
                    "is_read_only": bucket.is_read_only,
                    "kms_key_id": bucket.kms_key_id,
                    "metadata":bucket.metadata,
                    "name": bucket.name,
                    "namespace": bucket.namespace,
                    "object_events_enabled": bucket.object_events_enabled,
                    "object_lifecycle_policy_etag": bucket.object_lifecycle_policy_etag,
                    "public_access_type": bucket.public_access_type,
                    "replication_enabled": bucket.replication_enabled,
                    "storage_tier": bucket.storage_tier,
                    "time_created": bucket.time_created,
                    "versioning": bucket.versioning
            }
            self.__buckets.append(record)

        par_data = ParallelExecutor.executor(par_object_storage_clients, self.__bucket_objects, ParallelExecutor.get_preauthenticated_requests_per_bucket, len(self.__bucket_objects), ParallelExecutor.bucket_preauthenticated_requests)

        for par in par_data:
            par_objects = []
            bucket_name = next(iter(par.keys()))
            par_list = next(iter(par.values()))

            for par_object in par_list:
                record = {
                    "access_type": par_object.access_type,
                    "bucket_listing_action": par_object.bucket_listing_action,
                    "id": par_object.id,
                    "name": par_object.name, 
                    "object_name": par_object.object_name, 
                    "time_created": par_object.time_created, 
                    "time_expires": par_object.time_expires
                }
                par_objects.append(record) 
            self.__par_data.update({bucket_name:par_objects})
        
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


    def analyze_entity(self, entry):
    
        self.load_entity()     
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        total_private_buckets = 0
        total_public_buckets = 0        
        
        # Find expired PARs
        for bucket in self.__buckets: 
            if bucket['public_access_type'] == 'NoPublicAccess':
                total_private_buckets+=1
                             
                if bucket['name'] in self.__par_data:
                    for par in self.__par_data[bucket['name']]:
                        past = par['time_expires']
                        present = datetime.now()
                        if past.date() < present.date():
                            dictionary[entry]['status'] = False
                            dictionary[entry]['findings'].append(par)
                            dictionary[entry]['failure_cause'].append('The pre-authenticated request is expired')   
                            dictionary[entry]['mitigations'].append('Check if PAR: "' + par['name'] +
                                                                    '" at bucket: "' + bucket['name'] +
                                                                    '" expired at: ' + str(par['time_expires'].date())+ ' is still needed')      
            else:
                total_public_buckets+=1     
        
        # Check if there is too many public buckets
        if total_public_buckets > (total_public_buckets + total_private_buckets)/2:
             dictionary[entry]['status'] = False
             dictionary[entry]['failure_cause'].append('Gross majority of buckets are public')
             dictionary[entry]['mitigations'].append('Consider make Bucket: "'+ bucket['name'] + 'private')
            
        # Check how many users have access to update bucket access
        __problem_policies = []
        __criteria_list = ['manage','use','all-resources', 'object-family', 'buckets']

        for policy in self.__policies:
            problem_statements = []
            for statement in policy['statements']:             
                if (__criteria_list[0].lower() in statement.lower() or __criteria_list[1].lower() in statement.lower()) and any(criteria.lower() in statement.lower() for criteria in __criteria_list[2:]):
                    problem_statements.append(statement)
            if problem_statements:
                policy['statements'] = problem_statements
                __problem_policies.append(policy)   
   
        for policy in __problem_policies:
            for statement in policy['statements']:       
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(policy)    
                dictionary[entry]['failure_cause'].append('This policy allows users to update private bucket to public access')                
                dictionary[entry]['mitigations'].append('The folowing policy statement: "' + statement + '" gives permission to update bucket access.'
                                                        ' Check if this statement is still valid because the number of users able to update bucket access should be minimal (less than 5%)')
        
        return dictionary

