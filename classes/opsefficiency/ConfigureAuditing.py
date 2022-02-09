# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ConfigureAuditing.py
# Description: Implementation of class ConfigureAuditing based on abstract


from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *


class ConfigureAuditing(ReviewPoint):
    # Class Variables
    __tenancy_data = []
    __identity = None
    __audit_client = None
    __tenancy = None
    __policies = []
    __policy_objects = []
    __service_connectors_objects = []
    __service_connectors = []
    __retention_rules_list = []
    __bucket_objects = []
    __bucket_dicts = []


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
        self.__tenancy = get_tenancy_data(self.__identity, self.config)
        self.__audit_client = get_audit_client(self.config, self.signer)


    def load_entity(self):

        tenancy = get_tenancy_data(self.__identity, self.config)
        regions = get_regions_data(self.__identity, self.config)
        namespace = get_object_storage_client(self.config, self.signer).get_namespace().data

        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        audit_data = get_audit_configuration_data(self.__audit_client, self.__tenancy.id)

        tenancy_data = {
            "tenancy_id": self.__tenancy.id,
            "tenancy_name": self.__tenancy.name,
            "tenancy_description": self.__tenancy.description,
            "tenancy_region_key": self.__tenancy.home_region_key,
            "audit_retention_period_days": audit_data.retention_period_days
        }
        self.__tenancy_data.append(tenancy_data)

        service_clients = []
        object_storage_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            service_clients.append(get_service_client(region_config, self.signer))
            object_storage_clients.append( (get_object_storage_client(region_config, self.signer), namespace, region.region_name, region.region_key.lower()) )

        self.__service_connectors_objects = ParallelExecutor.executor(service_clients, self.__compartments, ParallelExecutor.get_service_connectors_info, len(self.__compartments), ParallelExecutor.service_connectors)

        for service_connector in self.__service_connectors_objects:
            record = {
                "compartment_id": service_connector.compartment_id,
                "defined_tags": service_connector.defined_tags,
                "description": service_connector.description,
                "display_name": service_connector.display_name,
                "id": service_connector.id,
                "lifecycle_state": service_connector.lifecycle_state,
                "time_created": service_connector.time_created,
                "time_updated": service_connector.time_updated,
            }
            self.__service_connectors.append(record)

        self.__bucket_objects = ParallelExecutor.executor(object_storage_clients, self.__compartments, ParallelExecutor.get_buckets, len(self.__compartments), ParallelExecutor.buckets)

        for bucket in self.__bucket_objects:
            record = {
                "compartment_id": bucket.compartment_id,
                "id": bucket.id,
                "display_name": bucket.name,
            }
            self.__bucket_dicts.append(record)

        self.__retention_rules_list = ParallelExecutor.executor(object_storage_clients, self.__bucket_objects, ParallelExecutor.get_bucket_retention_rules_info, len(self.__bucket_objects), ParallelExecutor.bucket_retention_rules)

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

        return self.__tenancy_data, self.__service_connectors, self.__retention_rules_list, self.__policies, self.__bucket_dicts


    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for tenancy in self.__tenancy_data:
            if tenancy['audit_retention_period_days'] != 365:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(tenancy)
                dictionary[entry]['failure_cause'].append("Audit retention is not set to 365 Days")
                dictionary[entry]['mitigations'].append("Set audit retention to 365 days on tenancy")

        if len(self.__service_connectors) < 1:
            dictionary[entry]['status'] = True
            dictionary[entry]['failure_cause'].append("No Service Connectors were found in this tenancy")
            dictionary[entry]['mitigations'].append("If you have third party tools that must access \"OCI Audit\" data configure a Service Connector to copy the OCI Audit data to Oracle Cloud Infrastructure Object Storage.")

        if len(self.__retention_rules_list) != len(self.__bucket_dicts):
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Some buckets do not have a retention period in place")
            for bucket in self.__bucket_dicts:
                for retention_rule in self.__retention_rules_list:
                    if bucket['id'] != retention_rule['bucket_id']:
                        dictionary[entry]['findings'].append(bucket)
                        dictionary[entry]['mitigations'].append(f"Consider adding retention a period on the following storage bucket: \"{bucket['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, bucket['compartment_id'])}\"")

        criteria = 'loganalytics'
        failure_case = True
        for policy in self.__policies:
            for statement in policy['statements']:
                if criteria.lower() in statement.lower():
                    failure_case = False

        if failure_case:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("OCI Log Analytics were not enabled on this tenancy")
            dictionary[entry]['mitigations'].append("Consider Enabling \"OCI Log Analytics\" for better insight and detailed analysis of patterns and trends.")

        return dictionary
