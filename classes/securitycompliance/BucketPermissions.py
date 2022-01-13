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
    __policies = []
    __bucket_objects = []
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

        compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        # get clients from each region 
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            object_storage_clients.append((get_object_storage_client(region_config, self.signer), obj_namespace))
            par_object_storage_clients.append((get_object_storage_client(region_config, self.signer),obj_namespace, region.region_name, region.region_key.lower()))
      
        self.__bucket_objects = ParallelExecutor.executor(object_storage_clients, compartments, ParallelExecutor.get_buckets, len(compartments), ParallelExecutor.buckets)
        par_data = ParallelExecutor.executor(par_object_storage_clients, self.__bucket_objects, ParallelExecutor.get_preauthenticated_requests_per_bucket, len(self.__bucket_objects), ParallelExecutor.bucket_preauthenticated_requests)
        
        for par in par_data:
            self.__par_data.update(par)
      
        policy_data = get_policies_data(self.__identity, self.__tenancy.id)   

        for policy in policy_data:  
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
        for bucket in self.__bucket_objects: 
            if bucket.public_access_type == 'NoPublicAccess':
                total_private_buckets+=1
                             
                if self.__par_data[bucket.name]:
                    for par in self.__par_data[bucket.name]:
                        past = par.time_expires
                        present = datetime.now()
                        if past.date() < present.date():
                            dictionary[entry]['status'] = False
                            dictionary[entry]['findings'].append({bucket.name:par.name})
                            dictionary[entry]['failure_cause'].append(f'The pre-authenticated request is expired')   
                            dictionary[entry]['mitigations'].append(f'Following PAR: "{par.name}" related to bucket: "{bucket.name}" is expired with the date: {par.time_expires.date()}, check if the access is still needed')      
            else:
                total_public_buckets+=1      
        # Check if there is too many public buckets
        if total_public_buckets > (total_public_buckets + total_private_buckets)/2:
             dictionary[entry]['status'] = False
             dictionary[entry]['findings'].append({'Public_buckets':f'Total public buckets: {total_public_buckets}'})    
             dictionary[entry]['failure_cause'].append(f'Majority of buckets are public: {total_public_buckets}/{total_private_buckets + total_public_buckets}')   
             dictionary[entry]['mitigations'].append(f'Consider creating private buckets and use pre-authenticated requests (PARs) to provide access to objects stored in buckets')
            
        # Check how many users have access to update bucket access
        __problem_policies = []
        __criteria_1 = 'manage'
        __criteria_2 = 'use'
        __criteria_3_list = ['all-resources', 'object-family', 'buckets']
    
        counter = 0        

        for policy in self.__policies:
            for statement in policy['statements']:
                if __criteria_1.upper() in statement.upper() or __criteria_2.upper() in statement.upper():
                    for criteria in __criteria_3_list:
                        if criteria.upper() in statement.upper():
                            counter+=1
                            __problem_policies.append({counter:statement})
                
        if counter > 0:
            for idx, policy in enumerate(__problem_policies):        

                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(policy)    
                dictionary[entry]['failure_cause'].append('This policy allows users to update private bucket to public access')                
                dictionary[entry]['mitigations'].append('Make sure that users in the following policy are allowed to update bucket access : ' + str(policy[idx+1]) +
                                                         ' : the number of users able to update bucket access should be none or minimal (less than 5 %)')
        return dictionary

