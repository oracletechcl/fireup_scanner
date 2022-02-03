# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ResourceMonitoring.py
# Description: Implementation of class ResourceMonitoring based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class ResourceMonitoring(ReviewPoint):

    # Class Variables    
    __compartments = []
    __alarm_objects = []
    __metric_objects = []
    __notification_objects = []
    __metrics = []
    __alarms = []
    __notifications = []
    __identity = None
    __tenancy = None



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
        notification_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            monitoring_clients.append(get_monitoring_client(region_config, self.signer))
            notification_clients.append(get_notification_control_plane_client(region_config, self.signer))

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__metric_objects = ParallelExecutor.executor(monitoring_clients, self.__compartments, ParallelExecutor.get_metrics, len(self.__compartments), ParallelExecutor.metrics)
        self.__alarm_objects = ParallelExecutor.executor(monitoring_clients, self.__compartments, ParallelExecutor.get_alarms, len(self.__compartments), ParallelExecutor.alarms)
        self.__notification_objects = ParallelExecutor.executor(notification_clients, self.__compartments, ParallelExecutor.get_notifications, len(self.__compartments), ParallelExecutor.notifications)

        #sorting through json for metric
        for metric in self.__metric_objects:
            record = {
                'name': metric.name,
                'namespace': metric.namespace,
                'compartment_id': metric.compartment_id,
                'dimensions': metric.dimensions,
            }
            self.__metrics.append(record)

        #sorting through json for alarm
        for alarm in self.__alarm_objects:
            record = {
                'compartment_id': alarm.compartment_id,
                'display_name': alarm.display_name,
                'is_enabled': alarm.is_enabled,
                'namespace': alarm.namespace,
                'lifecycle_state': alarm.lifecycle_state,
                'metric_compartment_id': alarm.metric_compartment_id,
                'query' : alarm.query,
                'destinations': alarm.destinations
            }
            self.__alarms.append(record)
        
        #sorting through json for notification
        for notification in self.__notification_objects:
            record = {
                'compartment_id': notification.compartment_id,
                'lifecycle_state': notification.lifecycle_state,
                'name': notification.name,
                'topic_id': notification.topic_id
            }
            self.__notifications.append(record)
        


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        #namespaces of metrics for compute instances, bare metal instances, functions, and databases
        names_compute = ['oci_computeagent','oci_blockstore', 'oci_vcn','oci_instancepools', 'oci_compute']
        names_bare_metal = ['oci_compute_infrastructure_health'] 
        names_functions = ['oci_faas']
        names_database = ['oci_autonomous_database', 'oracle_external_database','oracle_oci_database']
    
        counted_metrics = []
        counted_alarms = []
        alarm_namespaces = []

        for alarm in self.__alarms:
            if alarm['namespace'] not in alarm_namespaces:
                alarm_namespaces.append(alarm['namespace'])

        for metric in self.__metrics:
            #compute instances
            if metric['namespace'] in names_compute and metric['name'] not in counted_metrics:
                if metric['namespace'] not in alarm_namespaces:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['failure_cause'].append('No alarms enabled for compute instance metric.')
                    dictionary[entry]['mitigations'].append(f"Suggest creating alarms for compute instance metric\"{metric['name']}\" in namespace \"{metric['namespace']}\".")
                    counted_metrics.append(metric['name'])
                else:  
                    for alarm in self.__alarms:
                        if metric['namespace'] == alarm['namespace'] and alarm not in counted_alarms:
                            if alarm['is_enabled'] == False:
                                dictionary[entry]['status'] = False
                                dictionary[entry]['failure_cause'].append('Alarm for compute instance not enabled.')
                                dictionary[entry]['mitigations'].append(f"Suggest re-enabling alarm: \"{alarm['display_name']}\" in\"{alarm['namespace']}\".")  
                            if not alarm['destinations']:
                                dictionary[entry]['status'] = False
                                dictionary[entry]['failure_cause'].append('Alarm for compute instance not connected to notification topic.')
                                dictionary[entry]['mitigations'].append(f"Suggest adding a notification to the alarm: \"{alarm['display_name']}\" in compartment: \"{alarm['compartment_id']}\". ")  
                        counted_metrics.append(metric['name'])
                        counted_alarms.append(alarm)
            #bare metal
            elif metric['namespace'] in names_bare_metal and metric['name'] not in counted_metrics:
                if metric['namespace'] not in alarm_namespaces:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['failure_cause'].append('No alarms enabled for bare metal metric.')
                    dictionary[entry]['mitigations'].append(f"Suggest creating alarms for bare metal metric\"{metric['name']}\" in namespace \"{metric['namespace']}\".")
                    counted_metrics.append(metric['name'])
                else:  
                    for alarm in self.__alarms:
                        if metric['namespace'] == alarm['namespace'] and alarm not in counted_alarms:
                            if alarm['is_enabled'] == False:
                                dictionary[entry]['status'] = False
                                dictionary[entry]['failure_cause'].append('Alarm for bare metal instance not enabled.')
                                dictionary[entry]['mitigations'].append(f"Suggest re-enabling alarm: \"{alarm['display_name']}\" in\"{alarm['namespace']}\".")  
                            if not alarm['destinations']:
                                dictionary[entry]['status'] = False
                                dictionary[entry]['failure_cause'].append('Alarm for bare metal instance not connected to notification topic.')
                                dictionary[entry]['mitigations'].append(f"Suggest adding a notification to the alarm: \"{alarm['display_name']}\" in compartment: \"{alarm['compartment_id']}\". ")  
                        counted_metrics.append(metric['name'])
                        counted_alarms.append(alarm)
            #functions
            elif metric['namespace'] in names_functions and metric['name'] not in counted_metrics:
                if metric['namespace'] not in alarm_namespaces:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['failure_cause'].append('No alarms enabled for function metric.')
                    dictionary[entry]['mitigations'].append(f"Suggest creating alarms for function metric\"{metric['name']}\" in namespace \"{metric['namespace']}\".")
                    counted_metrics.append(metric['name'])
                else:  
                    for alarm in self.__alarms:
                        if metric['namespace'] == alarm['namespace'] and alarm not in counted_alarms:
                            if alarm['is_enabled'] == False:
                                dictionary[entry]['status'] = False
                                dictionary[entry]['failure_cause'].append('Alarm for function metric not enabled.')
                                dictionary[entry]['mitigations'].append(f"Suggest re-enabling alarm: \"{alarm['display_name']}\" in\"{alarm['namespace']}\".")  
                            if not alarm['destinations']:
                                dictionary[entry]['status'] = False
                                dictionary[entry]['failure_cause'].append('Alarm for function not connected to notification topic.')
                                dictionary[entry]['mitigations'].append(f"Suggest adding a notification to the alarm: \"{alarm['display_name']}\" in compartment: \"{alarm['compartment_id']}\". ")  
                        counted_metrics.append(metric['name'])
                        counted_alarms.append(alarm)
            #databases
            elif metric['namespace'] in names_database and metric['name'] not in counted_metrics:
                if metric['namespace'] not in alarm_namespaces:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['failure_cause'].append('No alarms enabled for database metric.')
                    dictionary[entry]['mitigations'].append(f"Suggest creating alarms for database metric\"{metric['name']}\" in namespace \"{metric['namespace']}\".")
                    counted_metrics.append(metric['name'])
                else:  
                    for alarm in self.__alarms:
                        if metric['namespace'] == alarm['namespace'] and alarm not in counted_alarms:
                            if alarm['is_enabled'] == False:
                                dictionary[entry]['status'] = False
                                dictionary[entry]['failure_cause'].append('Alarm for database not enabled.')
                                dictionary[entry]['mitigations'].append(f"Suggest re-enabling alarm: \"{alarm['display_name']}\" in\"{alarm['namespace']}\".")  
                            if not alarm['destinations']:
                                dictionary[entry]['status'] = False
                                dictionary[entry]['failure_cause'].append('Alarm for database not connected to notification topic.')
                                dictionary[entry]['mitigations'].append(f"Suggest adding a notification to the alarm: \"{alarm['display_name']}\" in compartment: \"{alarm['compartment_id']}\". ")  
                        counted_metrics.append(metric['name'])
                        counted_alarms.append(alarm)
            else:
                pass

        debug(dictionary, "cyan")
        return dictionary

