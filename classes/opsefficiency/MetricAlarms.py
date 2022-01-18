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
            
        # region_config = self.config
        # region_config['region'] = 'uk-london-1'
        # monitoring_clients.append(get_monitoring_client(region_config, self.signer))

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))
        debug('start1', "yellow")
        self.__metric_objects = ParallelExecutor.executor(monitoring_clients, self.__compartments, ParallelExecutor.get_metrics, len(self.__compartments), ParallelExecutor.metrics)
        debug('stop1', "yellow")
        debug(self.__metric_objects[1], "red")

        namespaces = []

        for metric in self.__metric_objects:
            if metric.namespace not in namespaces:
                namespaces.append(metric.namespace)

        debug(namespaces, "green")

        metric_namespaces = ['oci_objectstorage', 'oci_lbaas', 'oci_filestorage', 'oci_vcn', 'oci_computeagent', 'oci_compute_infrastructure_health', 
        'oci_compute', 'oci_blockstore', 'oci_nlb', 'oci_bastion', 'oci_managementagent', 'oci_autonomous_database', 'oci_apigateway', 
        'oci_waf', 'oci_healthchecks', 'oci_logging', 'oci_service_connector_hub', 'oci_vpn', 'oracle_appmgmt', 'oci_analytics', 
        'oci_notification', 'oci_cloudevents', 'oci_faas', 'oci_certificates', 'oci_instancepools', 'oci_vss', 'oci_dataintegration', 
        'oci_datascience', 'oci_service_gateway', 'oci_mysql_database', 'oci_oke', 'oci_nat_gateway', 'oci_unifiedagent', 
        'oci_logging_analytics', 'oci_nosql', 'oci_oce']

        return
        debug('start2', "yellow")
        self.__alarm_objects = ParallelExecutor.executor(monitoring_clients, self.__compartments, ParallelExecutor.get_alarms, len(self.__compartments), ParallelExecutor.alarms)
        debug('stop2', "yellow")
        debug(self.__alarm_objects[0], "cyan")

        return 

    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)



        return dictionary
