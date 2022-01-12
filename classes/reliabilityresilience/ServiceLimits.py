# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ServiceLimits.py
# Description: Implementation of class ServiceLimits based on abstract

from concurrent import futures
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class ServiceLimits(ReviewPoint):

    # Class Variables
    __limit_data_objects = []
    __compute_limits = []
    __non_compliant_compute_limits = dict()
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

        tenancy = get_tenancy_data(self.__identity, self.config)

        limits_clients = []
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            limits_clients.append(get_limits_client(region_config, self.signer))

        services = []
        # LBaaS - Region only
        # Block Volumes - Both
        # MySQL - Both
        # Database - Both
        # Kubernetes - Region only

        # Specialised parallel execution method for getting the limits in each region
        with futures.ThreadPoolExecutor(len(limits_clients)) as executor:
            processes = [
                executor.submit(get_limits_data, limits_client, tenancy.id)
                for limits_client in limits_clients
            ]

            futures.wait(processes)

            for p in processes:
                self.__limit_data_objects.append(p.result())



        return 


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

  
        return dictionary


def get_limits_data(limits_client, tenancy_id):

    limits_value_data = list_limit_value_data(limits_client, tenancy_id, "compute")

    limits_definition_data = list_limit_definition_data(limits_client, tenancy_id, "compute")

    return (limits_value_data, limits_definition_data)
