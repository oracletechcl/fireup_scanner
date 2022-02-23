# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# EnableDataSafe.py
# Description: Implementation of class EnableDataSafe based on abstract


from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class EnableDataSafe(ReviewPoint):

    # Class Variables
    __identity = None
    __compartments = []
    __oracle_database_objects = []
    __autonomous_database_objects = []
    __database_target_summary_objects = []
    __database_target_objects = []
    __database_target_ids = []


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
       self.__root_compartment = get_root_compartment_data(self.__identity, self.__tenancy.id)


    def load_entity(self):

        regions = get_regions_data(self.__identity, self.config)
        db_system_clients = []
        data_safe_clients = []

        # for region in regions:
        #     region_config = self.config
        #     region_config['region'] = region.region_name
        #     db_system_clients.append(get_database_client(region_config, self.signer))
        #     data_safe_clients.append( (get_data_safe_client(region_config, self.signer), region.region_name, region.region_key.lower()) )

        region_config = self.config
        region_config['region'] = 'uk-london-1'
        db_system_clients.append(get_database_client(region_config, self.signer))
        data_safe_clients.append( (get_data_safe_client(region_config, self.signer), 'uk-london-1', '') )

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(self.__root_compartment)

        # self.__oracle_database_objects = ParallelExecutor.executor(db_system_clients, self.__compartments, ParallelExecutor.get_oracle_dbsystem, len(self.__compartments), ParallelExecutor.oracle_dbsystems)
        self.__autonomous_database_objects = ParallelExecutor.executor(db_system_clients, self.__compartments, ParallelExecutor.get_autonomous_databases, len(self.__compartments), ParallelExecutor.autonomous_databases)

        debug('1', "yellow")
        self.__database_target_summary_objects = ParallelExecutor.executor([x[0] for x in data_safe_clients], [self.__root_compartment], ParallelExecutor.get_database_target_summaries, len(regions), ParallelExecutor.database_target_summaries)
        debug('2', "yellow")
        if len(self.__database_target_summary_objects) > 0:
            self.__database_target_objects = ParallelExecutor.executor(data_safe_clients, self.__database_target_summary_objects, ParallelExecutor.get_database_targets, len(self.__database_target_summary_objects), ParallelExecutor.database_targets)

        debug(self.__database_target_objects[0].database_details.autonomous_database_id, "green")

        debug(self.__autonomous_database_objects[0].id, "blue")

        for target in self.__database_target_objects:
            self.__database_target_ids.append(target.database_details.autonomous_database_id)

        return


    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for adb in self.__autonomous_database_objects:
            if adb.id not in self.__database_target_ids:
                debug('ADB not in targets', 'red')

        return dictionary
