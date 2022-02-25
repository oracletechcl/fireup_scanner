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
    __oracle_database_dicts = []
    __autonomous_database_objects = []
    __autonomous_database_dicts = []
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

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            db_system_clients.append(get_database_client(region_config, self.signer))
            data_safe_clients.append( (get_data_safe_client(region_config, self.signer), region.region_name, region.region_key.lower()) )

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(self.__root_compartment)

        self.__oracle_database_objects = ParallelExecutor.executor(db_system_clients, self.__compartments, ParallelExecutor.get_oracle_dbsystem, len(self.__compartments), ParallelExecutor.oracle_dbsystems)
        self.__autonomous_database_objects = ParallelExecutor.executor(db_system_clients, self.__compartments, ParallelExecutor.get_autonomous_databases, len(self.__compartments), ParallelExecutor.autonomous_databases)

        self.__database_target_summary_objects = ParallelExecutor.executor([x[0] for x in data_safe_clients], [self.__root_compartment], ParallelExecutor.get_database_target_summaries, len(regions), ParallelExecutor.database_target_summaries)
        if len(self.__database_target_summary_objects) > 0:
            self.__database_target_objects = ParallelExecutor.executor(data_safe_clients, self.__database_target_summary_objects, ParallelExecutor.get_database_targets, len(self.__database_target_summary_objects), ParallelExecutor.database_targets)

        for db in self.__oracle_database_objects:
            record = {
                'display_name': db.display_name,
                'compartment_id': db.compartment_id,
                'id': db.id,
                'lifecycle_state': db.lifecycle_state,
            }
            self.__oracle_database_dicts.append(record)

        for adb in self.__autonomous_database_objects:
            record = {
                'display_name': adb.display_name,
                'compartment_id': adb.compartment_id,
                'id': adb.id,
                'lifecycle_state': adb.lifecycle_state,
            }
            self.__autonomous_database_dicts.append(record)

        # Get database IDs associated with targets
        for target in self.__database_target_objects:
            if hasattr(target.database_details, "autonomous_database_id"):
                self.__database_target_ids.append(target.database_details.autonomous_database_id)
            elif hasattr(target.database_details, "db_system_id"):
                self.__database_target_ids.append(target.database_details.db_system_id)


    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for db in self.__oracle_database_dicts:
            if db['id'] not in self.__database_target_ids:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(db)
                dictionary[entry]['failure_cause'].append("Oracle database(s) aren't registerd with Oracle Data Safe")                
                dictionary[entry]['mitigations'].append(f"Consider registering Oracle database: \"{db['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, db['compartment_id'])}\" with Data Safe")

        for adb in self.__autonomous_database_dicts:
            if adb['id'] not in self.__database_target_ids:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(adb)
                dictionary[entry]['failure_cause'].append("Autonmous database(s) aren't registerd with Oracle Data Safe")                
                dictionary[entry]['mitigations'].append(f"Consider registering autonomous database: \"{adb['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, adb['compartment_id'])}\" with Data Safe")

        return dictionary
