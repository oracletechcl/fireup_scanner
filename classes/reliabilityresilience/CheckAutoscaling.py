# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CheckAutoscaling.py
# Description: Implementation of class CheckAutoscaling based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *


class CheckAutoscaling(ReviewPoint):

    # Class Variables
    __identity = None
    __tenancy = None
    __autoscaling_client = None
    __autoscaling_configurations = []
    __autoscaling_configurations_objects = None
    __compute_management_client = None
    __container_engine_client = None
    __instance_pools = []
    __instance_pools_objects = None
    __kubernetes_clusters_objects = None
    __kubernetes_clusters = []
    __policy_objects = None
    __policies = []
    __compartments = []


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
        compute_management_clients = []
        autoscaling_clients = []
        container_engine_clients = []
        identity_clients = []

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))
        regions = get_regions_data(self.__identity, self.config)

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            compute_management_clients.append(get_compute_management_client(region_config, self.signer))
            autoscaling_clients.append(get_autoscaling_client(region_config, self.signer))
            container_engine_clients.append(get_container_engine_client(region_config, self.signer))
            identity_clients.append(get_identity_client(region_config, self.signer))
      
        self.__autoscaling_configurations_objects = ParallelExecutor.executor(autoscaling_clients, self.__compartments, ParallelExecutor.get_autoscaling_configurations, len(self.__compartments), ParallelExecutor.autoscaling_configurations)
        
        for configuration in self.__autoscaling_configurations_objects:        
            record = {
                "compartment_id": configuration.compartment_id, 
                "cool_down_in_seconds": configuration.cool_down_in_seconds,
                "defined_tags": configuration.defined_tags, 
                "display_name": configuration.display_name,
                "freeform_tags": configuration.freeform_tags,
                "id": configuration.id, 
                "is_enabled": configuration.is_enabled,
                "resource": configuration.resource,
                "time_created": configuration.time_created                
            }
            self.__autoscaling_configurations.append(record)
            
        self.__instance_pools_objects = ParallelExecutor.executor(compute_management_clients, self.__compartments, ParallelExecutor.get_instance_pool, len(self.__compartments), ParallelExecutor.instance_pools)

        for instance_pool in self.__instance_pools_objects:  
            record = {
                "availability_domains": instance_pool.availability_domains,
                "compartment_id": instance_pool.compartment_id, 
                "defined_tags": instance_pool.defined_tags, 
                "display_name": instance_pool.display_name, 
                "freeform_tags": instance_pool.freeform_tags, 
                "id": instance_pool.id, 
                "instance_configuration_id": instance_pool.instance_configuration_id, 
                "lifecycle_state": instance_pool.lifecycle_state, 
                "size": instance_pool.size, 
                "time_created": instance_pool.time_created
            }
            self.__instance_pools.append(record)

            debug(self.__kubernetes_clusters_objects,color = 'green')
            self.__kubernetes_clusters_objects = ParallelExecutor.executor(container_engine_clients, self.__compartments, ParallelExecutor.get_kubernetes_clusters, len(self.__compartments), ParallelExecutor.kubernetes_clusters)     
            debug(self.__kubernetes_clusters_objects,color = 'green')
        for kubernetes_cluster in self.__kubernetes_clusters_objects:  
            record = {
                "available_kubernetes_upgrades": kubernetes_cluster.available_kubernetes_upgrades,
                "compartment_id": kubernetes_cluster.compartment_id, 
                "endpoint_config": kubernetes_cluster.endpoint_config,   
                "endpoints": kubernetes_cluster.endpoints, 
                "id": kubernetes_cluster.id, 
                "image_policy_config": kubernetes_cluster.image_policy_config, 
                "kubernetes_version": kubernetes_cluster.kubernetes_version, 
                "lifecycle_details": kubernetes_cluster.lifecycle_details, 
                "lifecycle_state": kubernetes_cluster.lifecycle_state, 
                "metadata": kubernetes_cluster.metadata,
                "name": kubernetes_cluster.name,
                "options": kubernetes_cluster.options, 
                "vcn_id": kubernetes_cluster.vcn_id
            }
            self.__kubernetes_clusters.append(record)

        self.__policy_objects = ParallelExecutor.executor(identity_clients, self.__compartments, ParallelExecutor.get_policies, len(self.__compartments), ParallelExecutor.policies)
            
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

        return None


    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        # Check for configuration for instance pools
        for instance_pool in self.__instance_pools:
            config_present = False
            for configuration in self.__autoscaling_configurations:
                if instance_pool['id'] == configuration['resource'].id:
                    config_present = True
                    break
            if not config_present:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(instance_pool)    
                dictionary[entry]['failure_cause'].append('The instance pool does not have any autoscaling configuraiton')                
                dictionary[entry]['mitigations'].append('Make sure to create and attach autoscaling configuraiton for instance pool named: ' + instance_pool['display_name'])        
        # Check for configuraiton for kubernetes clusters

        __autoscalling_statement = 'manage cluster-node-pools'

        for kubernetes_cluster in self.__kubernetes_clusters:
            have_autoscalling_policy = False
            for compartment in self.__compartments:
                if kubernetes_cluster['compartment_id'] == compartment.id:
                    for policy in self.__policies:
                        if compartment.name in policy and __autoscalling_statement in policy:
                            have_autoscalling_policy = True
            if not have_autoscalling_policy:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(kubernetes_cluster)    
                dictionary[entry]['failure_cause'].append('Kubernetes cluster does not have nay autoscaling configurtion running')                
                dictionary[entry]['mitigations'].append('Make sure that the right policies are in place to enable Kubernetes autoscaler in a cluster named: ' + kubernetes_cluster['name'])

        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        return dictionary
