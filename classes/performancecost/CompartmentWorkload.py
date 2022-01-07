# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CompartmentWorkload.py
# Description: Implementation of class CompartmentWorkload based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class CompartmentWorkload(ReviewPoint):

    # Class Variables
    __block_volume_objects = []
    __boot_volume_objects = []
    __block_storages = []
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
        self.__tenancy = get_tenancy_data(self.__identity, self.config)


    def load_entity(self):

        regions = get_regions_data(self.__identity, self.config)
        network_clients = []
        compute_clients = []
        load_balancer_clients = []
        network_load_balancer_clients = []
        db_system_clients = []
        container_engine_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            compute_clients.append(get_compute_client(region_config, self.signer))
            network_clients.append(get_virtual_network_client(region_config, self.signer))
            load_balancer_clients.append(get_load_balancer_client(region_config, self.signer))
            network_load_balancer_clients.append(get_network_load_balancer_client(region_config, self.signer))
            db_system_clients.append(get_database_client(region_config, self.signer))
            container_engine_clients.append(get_container_engine_client(region_config, self.signer))

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__vcn_objects = ParallelExecutor.executor(network_clients, self.__compartments, ParallelExecutor.get_vcns_in_compartments, len(self.__compartments), ParallelExecutor.vcns)
        self.__instance_objects = ParallelExecutor.executor(compute_clients, self.__compartments, ParallelExecutor.get_instances, len(self.__compartments), ParallelExecutor.instances)
        self.__load_balancer_objects = ParallelExecutor.executor(load_balancer_clients, self.__compartments, ParallelExecutor.get_load_balancers, len(self.__compartments), ParallelExecutor.load_balancers)
        self.__network_load_balancer_objects = ParallelExecutor.executor(network_load_balancer_clients, self.__compartments, ParallelExecutor.get_network_load_balancers, len(self.__compartments), ParallelExecutor.network_load_balancers)
        self.__oracle_database_objects = ParallelExecutor.executor(db_system_clients, self.__compartments, ParallelExecutor.get_oracle_dbsystem, len(self.__compartments), ParallelExecutor.oracle_dbsystems)
        self.__autonomous_database_objects = ParallelExecutor.executor(db_system_clients, self.__compartments, ParallelExecutor.get_autonomous_databases, len(self.__compartments), ParallelExecutor.autonomous_databases)
        self.__oke_cluster_objects = ParallelExecutor.executor(container_engine_clients, self.__compartments, ParallelExecutor.get_oke_cluster, len(self.__compartments), ParallelExecutor.oke_clusters)


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        aggregate_items = self.__vcn_objects + self.__instance_objects + self.__load_balancer_objects + self.__network_load_balancer_objects
        aggregate_items += self.__oracle_database_objects + self.__autonomous_database_objects + self.__oke_cluster_objects

        # Copy compartments list
        empty_compartments = self.__compartments[:]

        # Checks all items against compartments and remove those that have workload within them
        for item in aggregate_items:
            for compartment in empty_compartments:
                if item.compartment_id == compartment.id:
                    empty_compartments.remove(compartment)

        # If less that 3 compartments are being utilised (including root), fail.
        if len(self.__compartments) - len(empty_compartments) < 3:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append('Use additional compartments than just root to holster your workload.')
            for compartment in empty_compartments:
                compartment_record = {
                    "id": compartment.id,
                    "compartment_id": compartment.compartment_id,
                    "description": compartment.description,
                    "lifecycle_state": compartment.lifecycle_state,
                }
                dictionary[entry]['findings'].append(compartment_record)
                dictionary[entry]['mitigations'].append(f"Compartment {get_compartment_name(self.__compartments, compartment.id)}, appears to house no workload.")

        return dictionary
