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
    __compartments = []
    __autoscaling_configurations_objects = []
    __autoscaling_configurations_resource_ids = []
    __instance_pools_objects = []
    __instance_pools = []
    __oke_clusters = []
    __oke_clusters_objects = []
    __policy_objects = []
    


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

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))
        regions = get_regions_data(self.__identity, self.config)

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            compute_management_clients.append(get_compute_management_client(region_config, self.signer))
            autoscaling_clients.append(get_autoscaling_client(region_config, self.signer))
            container_engine_clients.append(get_container_engine_client(region_config, self.signer))
      
        self.__autoscaling_configurations_objects = ParallelExecutor.executor(autoscaling_clients, self.__compartments, ParallelExecutor.get_autoscaling_configurations, len(self.__compartments), ParallelExecutor.autoscaling_configurations)
        self.__policy_objects = ParallelExecutor.executor([self.__identity], self.__compartments, ParallelExecutor.get_policies, len(self.__compartments), ParallelExecutor.policies)
        self.__instance_pools_objects = ParallelExecutor.executor(compute_management_clients, self.__compartments, ParallelExecutor.get_instance_pools, len(self.__compartments), ParallelExecutor.instance_pools)
        self.__oke_clusters_objects = ParallelExecutor.executor(container_engine_clients, self.__compartments, ParallelExecutor.get_oke_clusters, len(self.__compartments), ParallelExecutor.oke_clusters)     

        for autoscaling_config in self.__autoscaling_configurations_objects:
            self.__autoscaling_configurations_resource_ids.append(autoscaling_config.resource.id)

        for instance_pool in self.__instance_pools_objects:  
            record = {
                "availability_domains": instance_pool.availability_domains,
                "compartment_id": instance_pool.compartment_id, 
                "display_name": instance_pool.display_name, 
                "id": instance_pool.id, 
                "instance_configuration_id": instance_pool.instance_configuration_id, 
                "lifecycle_state": instance_pool.lifecycle_state, 
                "size": instance_pool.size, 
                "time_created": instance_pool.time_created
            }
            self.__instance_pools.append(record)

        for oke_cluster in self.__oke_clusters_objects:  
            record = {
                "compartment_id": oke_cluster.compartment_id, 
                "id": oke_cluster.id, 
                "kubernetes_version": oke_cluster.kubernetes_version, 
                "lifecycle_state": oke_cluster.lifecycle_state, 
                "display_name": oke_cluster.name,
                "vcn_id": oke_cluster.vcn_id
            }
            self.__oke_clusters.append(record)

        
    def analyze_entity(self, entry):

        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        # Check for autoscaling configuration for instance pools
        for instance_pool in self.__instance_pools:
            configuration_present = False

            if instance_pool['id'] in self.__autoscaling_configurations_resource_ids:
                configuration_present = True

            if not configuration_present:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(instance_pool)
                dictionary[entry]['failure_cause'].append("The instance pool does not have any autoscaling configuration created")                
                dictionary[entry]['mitigations'].append(f"Make sure to create and attach autoscaling configuration for instance pool named: \"{instance_pool['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, instance_pool['compartment_id'])}\"")          

        # Check if Autoscaler for Kubernetes is enabled in policy statements
        verb_and_resource_type = 'manage cluster-node-pools in compartment '

        for oke_cluster in self.__oke_clusters:
            have_autoscaling_policy = False
            for policy in self.__policy_objects:
                for statement in policy.statements:
                    if 'dynamic-group' in statement:
                        if verb_and_resource_type + get_compartment_name(self.__compartments, oke_cluster['compartment_id']) in statement:
                            have_autoscaling_policy = True
                            break

            if not have_autoscaling_policy:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(oke_cluster)
                dictionary[entry]['failure_cause'].append("Kubernetes cluster does not have any autoscaling enabled")
                dictionary[entry]['mitigations'].append(f"Make sure that the auto scaling is enabled for cluster: \"{oke_cluster['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, oke_cluster['compartment_id'])}\"")

        return dictionary
