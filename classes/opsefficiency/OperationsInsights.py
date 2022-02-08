# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# OperationsInsights.py
# Description: Implementation of class OperationsInsights based on abstract

from importlib.abc import ResourceLoader
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class OperationsInsights(ReviewPoint):

    # Class Variables
    __compartments = []
    __identity = None
    __db_system_home_objects = []
    __dbs_from_db_homes = []
    __dbs_from_db_homes_dicts = [] 
    __operations_insights_warehouses = []
    __awr_hubs = []

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
        self.__regions = get_regions_data(self.__identity, self.config)

    def load_entity(self):

        db_system_clients = []
        operations_insights_clients = []

        for region in self.__regions:
            region_config = self.config
            region_config['region'] = region.region_name
            db_system_clients.append( (get_database_client(region_config, self.signer), region.region_name, region.region_key.lower()) )
            operations_insights_clients.append( (get_operations_insights_client(region_config, self.signer), region.region_name, region.region_key.lower()) )

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__db_system_home_objects = ParallelExecutor.executor([x[0] for x in db_system_clients], self.__compartments, ParallelExecutor.get_database_homes, len(self.__compartments), ParallelExecutor.db_system_homes)
        
        if len(self.__db_system_home_objects) > 0:
            self.__dbs_from_db_homes = ParallelExecutor.executor(db_system_clients, self.__db_system_home_objects, ParallelExecutor.get_dbs_from_db_homes, len(self.__db_system_home_objects), ParallelExecutor.dbs_from_db_homes)
        
        self.__operations_insights_warehouses = ParallelExecutor.executor([x[0] for x in operations_insights_clients], [self.__tenancy.id], ParallelExecutor.get_operations_insights_warehouses, len(self.__regions), ParallelExecutor.operations_insights_warehouses)         
        
        if len(self.__operations_insights_warehouses) > 0:
            self.__awr_hubs = ParallelExecutor.executor(operations_insights_clients, self.__operations_insights_warehouses, ParallelExecutor.get_awr_hubs, len(self.__operations_insights_warehouses), ParallelExecutor.awr_hubs)

        for db in self.__dbs_from_db_homes:
            record = {
                'id': db.id,
                'db_name': db.db_name,
                'db_system_id': db.db_system_id,
                'db_home_id': db.db_home_id,
                'compartment_id': db.compartment_id,
                'database_management_config': db.database_management_config,                
            }
            self.__dbs_from_db_homes_dicts.append(record)

        return


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        db_regions = []

        for db in self.__dbs_from_db_homes_dicts:
            db_region = db['id'].split('.')[3]
            if db_region not in db_regions:
                db_regions.append(db_region)
            if db['database_management_config'] == None:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(db)
                dictionary[entry]['failure_cause'].append("DB systems doesn't have database management enabled")
                dictionary[entry]['mitigations'].append(f"Make sure database: \"{db['db_name']}\" in compartment: \"{get_compartment_name(self.__compartments, db['compartment_id'])}\" has database management enabled.")

        non_compliant_regions = db_regions[:]

        for region in db_regions:
            for hub in self.__awr_hubs:
                if region == hub.id.split('.')[3] and hub.lifecycle_state == "ACTIVE":
                    non_compliant_regions.remove(region)

        for region in non_compliant_regions:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append("Region with databases should have an operations insight warehouse and hub")
            dictionary[entry]['mitigations'].append(f"Make sure region: \"{region}\" has as operations insight warehouse and hub.")

        return dictionary
