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
    __autoscaling_configurations_objects = None
    __autoscaling_configurations = []
    __instance_pools_objects = None
    __instance_pools = []
    __kubernetes_clusters_objects = None
    __kubernetes_clusters = []
    __policy_objects = None
    __policies = []
    


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

        compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))
        regions = get_regions_data(self.__identity, self.config)

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            compute_management_clients.append(get_compute_management_client(region_config, self.signer))
            autoscaling_clients.append(get_autoscaling_client(region_config, self.signer))
            container_engine_clients.append(get_container_engine_client(region_config, self.signer))
            identity_clients.append(get_identity_client(region_config, self.signer))
      
        self.__autoscaling_configurations_objects = ParallelExecutor.executor(autoscaling_clients, compartments, ParallelExecutor.get_autoscaling_configurations, len(compartments), ParallelExecutor.autoscaling_configurations)
        
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
            
        self.__instance_pools_objects = ParallelExecutor.executor(compute_management_clients, compartments, ParallelExecutor.get_instance_pool, len(compartments), ParallelExecutor.instance_pools)

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

        self.__kubernetes_clusters_objects = ParallelExecutor.executor(container_engine_clients, compartments, ParallelExecutor.get_kubernetes_clusters_with_compartment, len(compartments), ParallelExecutor.kubernetes_clusters)     
        
        for kubernetes_cluster_with_compartment in self.__kubernetes_clusters_objects:  
            record = {
                "available_kubernetes_upgrades": kubernetes_cluster_with_compartment[0].available_kubernetes_upgrades,
                "compartment_id": kubernetes_cluster_with_compartment[0].compartment_id, 
                "endpoint_config": kubernetes_cluster_with_compartment[0].endpoint_config,   
                "endpoints": kubernetes_cluster_with_compartment[0].endpoints, 
                "id": kubernetes_cluster_with_compartment[0].id, 
                "image_policy_config": kubernetes_cluster_with_compartment[0].image_policy_config, 
                "kubernetes_version": kubernetes_cluster_with_compartment[0].kubernetes_version, 
                "lifecycle_details": kubernetes_cluster_with_compartment[0].lifecycle_details, 
                "lifecycle_state": kubernetes_cluster_with_compartment[0].lifecycle_state, 
                "metadata": kubernetes_cluster_with_compartment[0].metadata,
                "name": kubernetes_cluster_with_compartment[0].name,
                "options": kubernetes_cluster_with_compartment[0].options, 
                "vcn_id": kubernetes_cluster_with_compartment[0].vcn_id
            }
            self.__kubernetes_clusters.append( (record,kubernetes_cluster_with_compartment[1]) )

        self.__policy_objects = ParallelExecutor.executor(identity_clients, compartments, ParallelExecutor.get_policies, len(compartments), ParallelExecutor.policies)
            
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

        # Check for autoscaling configuration for instance pools
        for instance_pool in self.__instance_pools:
            configuration_present = False
            for configuration in self.__autoscaling_configurations:
                if instance_pool['id'] == configuration['resource'].id:
                    configuration_present = True
                    break
            if not configuration_present:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(instance_pool)    
                dictionary[entry]['failure_cause'].append('The instance pool does not have any autoscaling configuraiton')                
                dictionary[entry]['mitigations'].append('Make sure to create and attach autoscaling configuraiton for instance pool named: ' + instance_pool['display_name'])          
        
        # Check if Autoscaler for Kubernetes is enabled in policy statements

        __required_part_of_policy_statement = 'manage cluster-node-pools in compartment '

        for kubernetes_cluster_with_compartment in self.__kubernetes_clusters:
            have_autoscaling_policy = False
            for policy in self.__policies:
                if (__required_part_of_policy_statement + kubernetes_cluster_with_compartment[1].name) in policy:
                    have_autoscaling_policy = True
                    break
            if not have_autoscaling_policy:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(kubernetes_cluster_with_compartment[0])    
                dictionary[entry]['failure_cause'].append('Kubernetes cluster does not have any autoscaling enabled')                
                dictionary[entry]['mitigations'].append('Make sure that the right policies are in place to enable Kubernetes autoscaler in a cluster named: ' + kubernetes_cluster_with_compartment[0]['name'])

        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        return dictionary
