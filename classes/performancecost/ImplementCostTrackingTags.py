# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ImplementCostTrackingTags.py
# Description: Implementation of class ImplementCostTrackingTags based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class ImplementCostTrackingTags(ReviewPoint):
    # Class Variables
    __cost_tracking_tags_objects = []
    __policies = []
    __policy_objects = []
    __cost_tracking_tags = []
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
        tenancy = get_tenancy_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, tenancy.id))

        identity_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            identity_clients.append(get_identity_client(region_config, self.signer))

        self.__cost_tracking_tags_objects = get_cost_tracking_tags(identity_clients[0], root_compartment_id=get_tenancy_data(self.__identity, self.config).id)

        for cost_tracking_tag in self.__cost_tracking_tags_objects:
            record = {
                "compartment_id": cost_tracking_tag.compartment_id,
                "defined_tags": cost_tracking_tag.defined_tags,
                "description": cost_tracking_tag.description,
                "id": cost_tracking_tag.id,
                "is_cost_tracking": cost_tracking_tag.is_cost_tracking,
                "display_name": cost_tracking_tag.name,
                "lifecycle_state": cost_tracking_tag.lifecycle_state,
                "tag_namespace_id": cost_tracking_tag.tag_namespace_id,
                "tag_namespace_name": cost_tracking_tag.tag_namespace_name,
                "time_created": cost_tracking_tag.time_created,
            }
            self.__cost_tracking_tags.append(record)

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

        return self.__cost_tracking_tags, self.__policies


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        if len(self.__cost_tracking_tags) == 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("No Cost Tracking Tags were found in this tenancy")
            dictionary[entry]['mitigations'].append("Consider adding \"Cost Tracking Tags\" to allow for more flexibility in where resources are placed and in how cost data is queried.")

        failure_case = True
        for policy in self.__policies:
            for statement in policy['statements']:
                if 'tag-namespaces'.lower() in statement.lower():
                    failure_case = False

        if failure_case:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("No Policies for securing tagged namespaces were found in this tenancy")
            dictionary[entry]['mitigations'].append("Consider implementing \"Policies\" to protect tagged namespaces & to ensure only \"Tag administrators\" can make changes")

        return dictionary
