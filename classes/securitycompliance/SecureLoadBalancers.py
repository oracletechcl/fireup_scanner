# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# SecureLoadBalancers.py
# Description: Implementation of class LBaaSHealthChecks based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *


class SecureLoadBalancers(ReviewPoint):
    # Class Variables
    __load_balancer_objects = []
    __load_balancers = []
    __compartments = []
    __identity = None
    __policies = []
    __policy_objects = []


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

        tenancy = get_tenancy_data(self.__identity, self.config)
        regions = get_regions_data(self.__identity, self.config)
        load_balancer_clients = []

        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))


        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            load_balancer_clients.append(get_load_balancer_client(region_config, self.signer))

        self.__load_balancer_objects = ParallelExecutor.executor(load_balancer_clients, self.__compartments, ParallelExecutor.get_load_balancers, len(self.__compartments), ParallelExecutor.load_balancers)

        for load_balancer in self.__load_balancer_objects:
            record = {
                'display_name': load_balancer.display_name,
                'id': load_balancer.id,
                'compartment_id': load_balancer.compartment_id,
                'listeners': load_balancer.listeners,
                'lifecycle_state': load_balancer.lifecycle_state,
                'time_created': load_balancer.time_created,
            }
            self.__load_balancers.append(record)

        self.__policy_objects = ParallelExecutor.executor([self.__identity], self.__compartments, ParallelExecutor.get_policies, len(self.__compartments), ParallelExecutor.policies)
        
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

        return self.__policies,self.__load_balancers


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        criteria = 'load-balancers'
        failure_case = True
        for policy in self.__policies:
            for statement in policy['statements']:
                if criteria.lower() in statement.lower():
                    failure_case = False

        if failure_case == True:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("No Policies for securing load balancers have been detected")
            dictionary[entry]['mitigations'].append("Add load-balancer policies into the tenancy to enforce load balancer protection.")

        for load_balancer in self.__load_balancers:
            for listener in load_balancer['listeners']:
                if load_balancer['listeners'][listener].ssl_configuration is None:
                    if load_balancer not in dictionary[entry]['findings']:
                        dictionary[entry]['status'] = False
                        dictionary[entry]['findings'].append(load_balancer)
                        dictionary[entry]['failure_cause'].append('Application load balancer listeners should use SSL encryption.')
                        dictionary[entry]['mitigations'].append(f"Application load balancer: \"{load_balancer['display_name']}\" located in \"{get_compartment_name(self.__compartments, load_balancer['compartment_id'])}\" has a listener without SSL enabled.")

        return dictionary
