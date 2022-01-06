# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# TrafficSteering.py
# Description: Implementation of class TrafficSteering based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class TrafficSteering(ReviewPoint):

    # Class Variables
    __steering_policy_objects = []
    __steering_policies = []
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
        dns_client = get_dns_client(self.config, self.signer)

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        debug_with_date(len(self.__compartments))

        debug_with_date('start')
        self.__steering_policy_objects = ParallelExecutor.executor([dns_client], self.__compartments, ParallelExecutor.get_steering_policies, len(self.__compartments), ParallelExecutor.steering_policies)
        
        # for compartment in self.__compartments:
        #     steering_policy_data = get_steering_policy_data(dns_clients[0], compartment.id)
        #     for steering_policy in steering_policy_data:
        #         self.__steering_policy_objects.append(steering_policy)

        
        debug_with_date('stop')
        # debug_with_color_date(self.__steering_policy_objects[0], "cyan")

        debug_with_color_date(len(self.__steering_policy_objects), "green")
        debug_with_color_date(self.__steering_policy_objects, "green")

        return


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)



        return dictionary
