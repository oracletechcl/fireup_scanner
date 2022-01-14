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
    __autoscaling_configurations = None
    __compute_management_client = None
    __instance_pools = None

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
        self.__autoscaling_client = get_autoscaling_client(self.config, self.signer)
        self.__compute_management_client = get_compute_management_client(self.config, self.signer)
        compute_management_clients = []
        autoscaling_clients = []

        compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))
        regions = get_regions_data(self.__identity, self.config)

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            compute_management_clients.append(get_compute_management_client(region_config, self.signer))
            autoscaling_clients.append(get_autoscaling_client(region_config, self.signer))
      
        self.__autoscaling_configurations = ParallelExecutor.executor(autoscaling_clients, compartments, ParallelExecutor.get_autoscaling_configurations, len(compartments), ParallelExecutor.autoscaling_configurations)     
        self.__instance_pools = ParallelExecutor.executor(compute_management_clients, compartments, ParallelExecutor.get_instance_pool, len(compartments), ParallelExecutor.instance_pools)     
        debug(self.__autoscaling_configurations,color = 'yellow')
        return None

    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        return dictionary
