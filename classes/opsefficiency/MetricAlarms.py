# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# MetricAlarms.py
# Description: Implementation of class MetricAlarms based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class MetricAlarms(ReviewPoint):

    # Class Variables
    __compartments = []
    __alarm_objects = []
    __metric_objects = []
    __namespaces = []
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
        self.__tenancy = get_tenancy_data(self.__identity, self.config)


    def load_entity(self):

        regions = get_regions_data(self.__identity, self.config)

        monitoring_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            monitoring_clients.append(get_monitoring_client(region_config, self.signer))

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__metric_objects = ParallelExecutor.executor(monitoring_clients, self.__compartments, ParallelExecutor.get_metrics, len(self.__compartments), ParallelExecutor.metrics)
        self.__alarm_objects = ParallelExecutor.executor(monitoring_clients, self.__compartments, ParallelExecutor.get_alarms, len(self.__compartments), ParallelExecutor.alarms)

        for metric in self.__metric_objects:
            if metric.namespace not in self.__namespaces:
                self.__namespaces.append(metric.namespace)

        return self.__metric_objects, self.__alarm_objects


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for alarm in self.__alarm_objects:
            if alarm.namespace in self.__namespaces:
                self.__namespaces.remove(alarm.namespace)

        if len(self.__namespaces) > 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Consider adding alarms for each namespace used within the tenancy.")
            dictionary[entry]['mitigations'].append(f"Suggest adding alarm(s) to manage the following namespaces: {self.__namespaces}.")

        return dictionary
