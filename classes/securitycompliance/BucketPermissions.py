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
    __buckets_with_pars = []
 
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

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        # get clients from each region 
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            object_storage_clients.append( (get_object_storage_client(region_config, self.signer), obj_namespace, region.region_name, region.region_key.lower()) )
      
        self.__bucket_objects = ParallelExecutor.executor(object_storage_clients, self.__compartments, ParallelExecutor.get_buckets, len(self.__compartments), ParallelExecutor.buckets)

        par_data = ParallelExecutor.executor(object_storage_clients, self.__bucket_objects, ParallelExecutor.get_preauthenticated_requests_per_bucket, len(self.__bucket_objects), ParallelExecutor.bucket_preauthenticated_requests)
        
        # Loop through tuples of bucket objects with PARs objects
        for bucket, par_list in par_data:
            par_dicts = []

            bucket_dict = {
                "compartment_id": bucket.compartment_id,
                "id": bucket.id,
                "name": bucket.name,
                "public_access_type": bucket.public_access_type,
            }

            for par_object in par_list:
                record = {
                    "bucket_name": bucket.name,
                    "id": bucket.id,
                    "compartment_id": bucket.compartment_id,
                    "access_type": par_object.access_type,
                    "name": par_object.name, 
                    "object_name": par_object.object_name,
                    "time_expires": par_object.time_expires
                }
                par_dicts.append(record)

            # Add tuples of buckets and list of PARs in dictionary form
            self.__buckets_with_pars.append( (bucket_dict, par_dicts) )
        
        self.__policy_objects = ParallelExecutor.executor([self.__identity], self.__compartments, ParallelExecutor.get_policies, len(self.__compartments), ParallelExecutor.policies)

        for policy in self.__policy_objects:  
            record = {
                "compartment_id": policy.compartment_id,
                "description": policy.description,
                "id": policy.id,
                "lifecycle_state": policy.lifecycle_state,
                "name": policy.name,
                "statements": policy.statements,      
            }
            self.__policies.append(record)


    def analyze_entity(self, entry):
    
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        total_private_buckets = 0
        total_public_buckets = 0

        # Loop through tuples of buckets and pars in dictionary form
        for bucket, pars in self.__buckets_with_pars:
            if bucket['public_access_type'] == 'NoPublicAccess':
                total_private_buckets += 1
                for par in pars:
                    expiry = par['time_expires']
                    present = datetime.now()
                    if expiry.date() < present.date():
                        dictionary[entry]['status'] = False
                        dictionary[entry]['findings'].append(par)
                        dictionary[entry]['failure_cause'].append("The pre-authenticated request is expired")
                        dictionary[entry]['mitigations'].append(f"Check if PAR: \"{par['name']}\" on bucket: \"{par['bucket_name']}\" located in compartment: \"{get_compartment_name(self.__compartments, par['compartment_id'])}\" which expired at: \"{par['time_expires'].date()}\" is still needed")
            else:
                total_public_buckets += 1 
        
        # Check if there is too many public buckets
        if total_public_buckets > (total_public_buckets + total_private_buckets)/2:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Gross majority of buckets are public")
            dictionary[entry]['mitigations'].append(f"Consider making Bucket: \"{bucket['name']}\" private")
            
        # Check how many users have access to update bucket access
        verb_list = ['manage', 'use']
        criteria_list = ['all-resources', 'object-family', 'buckets']

        for policy in self.__policies:
            for statement in policy['statements']:
                if any(verb in statement.lower() for verb in verb_list):
                    if any(critera in statement.lower() for critera in criteria_list):
                        dictionary[entry]['status'] = False
                        if policy not in dictionary[entry]['findings']:
                            dictionary[entry]['findings'].append(policy)
                        dictionary[entry]['failure_cause'].append("This policy allows users to update private bucket to public access")                
                        dictionary[entry]['mitigations'].append(f"Evaluate updating statement: \"{statement}\" in policy: \"{policy['name']}\" in compartment: \"{get_compartment_name(self.__compartments, policy['compartment_id'])}\" to give less access to buckets")

        return dictionary
