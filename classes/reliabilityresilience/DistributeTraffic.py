# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# DistributeTraffic.py
# Description: Implementation of class DistributeTraffic based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class DistributeTraffic(ReviewPoint):
    # Class Variables
    __steering_policy_objects = []
    __steering_policies = []
    __load_balancer_objects = []
    __dns_zone_objects = []
    __compartments = []
    __identity = None

    def __init__(self,
                 entry: str,
                 area: str,
                 sub_area: str,
                 review_point: str,
                 status: bool,
                 failure_cause: list,
                 findings: list,
                 mitigations: list,
                 fireup_mapping: list,
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

        dns_clients = []
        load_balancer_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            dns_clients.append(get_dns_client(self.config, self.signer))
            load_balancer_clients.append(get_load_balancer_client(region_config, self.signer))

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__steering_policy_objects = ParallelExecutor.executor(dns_clients, self.__compartments,
                                                                   ParallelExecutor.get_steering_policies,
                                                                   len(self.__compartments),
                                                                   ParallelExecutor.steering_policies)
        self.__load_balancer_objects = ParallelExecutor.executor(load_balancer_clients, self.__compartments,
                                                                 ParallelExecutor.get_load_balancers,
                                                                 len(self.__compartments),
                                                                 ParallelExecutor.load_balancers)
        self.__dns_zone_objects = ParallelExecutor.executor(dns_clients, self.__compartments,
                                                            ParallelExecutor.get_dns_zones, len(self.__compartments),
                                                            ParallelExecutor.dns_zones)

        return self.__steering_policy_objects

    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        if len(self.__steering_policy_objects) == 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append('No steering policies found but in this tenancy')
            dictionary[entry]['mitigations'].append('Consider using steering policies if workload is split across '
                                                    'multiple regions.')

        if len(self.__load_balancer_objects) == 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append('No load balancers were found but in this tenancy')
            dictionary[entry]['mitigations'].append('Consider using load balancers to improves resource utilization, '
                                                    'scaling, and ensure high availability')

        if len(self.__dns_zone_objects) == 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append('No DNS Zones were found but in this tenancy')
            dictionary[entry]['mitigations'].append('Consider using DNS Zones to handle your DNS queries for better '
                                                    'resource distribution.')

        return dictionary
