# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ComputeLimits.py
# Description: Implementation of class ComputeLimits based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class ComputeLimits(ReviewPoint):

    # Class Variables
    __limit_value_objects = []
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
        limits_clients = []

        # for region in regions:
        #     region_config = self.config
        #     region_config['region'] = region.region_name
        #     limits_clients.append(get_limits_client(region_config, self.signer))

        region_config = self.config
        region_config['region'] = 'uk-london-1'
        limits_clients.append(get_limits_client(region_config, self.signer))
        region_config['region'] = 'us-ashburn-1'
        limits_clients.append(get_limits_client(region_config, self.signer))

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        # self.__load_balancer_objects = ParallelExecutor.executor(load_balancer_clients, self.__compartments, ParallelExecutor.get_load_balancers, len(self.__compartments), ParallelExecutor.load_balancers)

        # self.__limit_value_objects = ParallelExecutor.executor(load_balancer_clients, self.__compartments, ParallelExecutor.get_load_balancers, len(self.__compartments), ParallelExecutor.load_balancers)

        limit_value_objects1 = list_limit_value_data(limits_clients[0], tenancy.id, "compute")
        limit_value_objects2 = list_limit_value_data(limits_clients[1], tenancy.id, "compute")

        # test = limits_clients[1].get_resource_availability(service_name="compute", limit_name="standard2-core-count", compartment_id=tenancy.id, availability_domain="oDQF:US-ASHBURN-AD-1").data

        test2 = limits_clients[0].list_services(tenancy.id).data

        debug_with_color_date(test2, "green")

        
        # for limit_value in limit_value_objects1 + limit_value_objects2:
        #     if "gpu3-count" in limit_value.name:
        #         debug_with_color_date(limit_value, "green")


        return 


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        

        return dictionary
