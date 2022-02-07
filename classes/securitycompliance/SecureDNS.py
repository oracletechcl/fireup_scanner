# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# SecureDNS.py
# Description: Implementation of class SecureDNS based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *


class SecureDNS(ReviewPoint):
    # Class Variables
    __policy_objects = []
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


    def load_entity(self):

        tenancy = get_tenancy_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

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

        return self.__policies


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        criteria = ['dns-zones', 'dns-records']
        failure_case = True
        for policy in self.__policies:
            for statement in policy['statements']:
                for criterion in criteria:
                    if criterion.lower() in statement.lower():
                        failure_case = False

        if failure_case:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("No Policies for securing dns-zones or dns-records")
            dictionary[entry]['mitigations'].append("Add \"dns-zones\" and/or \"dns-records\" policies into the tenancy to enforce DNS protection.")

        return dictionary
