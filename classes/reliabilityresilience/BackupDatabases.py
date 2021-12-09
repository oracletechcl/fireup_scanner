# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# BackupDatabases.py
# Description: Implementation of class BackupDatabases based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *


class BackupDatabases(ReviewPoint):

    # Class Variables
    __db_systems = []
    __autonomous_databases = []
    __mysql_databases = []
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


    def load_entity(self):

        regions = get_regions_data(self.__identity, self.config)
        db_system_clients = []
        mysql_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            db_system_clients.append(get_database_client(region_config, self.signer))
            mysql_clients.append(get_mysql_client(region_config, self.signer))

        # TEMPORARY REPLACEMENT OF ABOVE FOR SINGLE REGION
        # region_config = self.config
        # region_config['region'] = 'us-ashburn-1'

        # database_clients.append( (get_database_client(region_config, self.signer), get_mysql_client(region_config, self.signer)) )
        
        # TEMPORARY REPLACEMENT OF ABOVE FOR SINGLE REGION

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        args_list = [
            [db_system_clients, compartments, self.__search_compartments, len(compartments), "__db_systems"],
            [db_system_clients, compartments, self.__search_auto_dbs, len(compartments), "__autonomous_databases"],
            [mysql_clients, compartments, self.__search_mysql_dbs, len(compartments), "__mysql_databases"],
        ]

        with futures.ThreadPoolExecutor(16) as executor:
            debug_with_date('start1')

            values = []

            processes = [
                executor.submit(parallel_executor, *args)
                for args in args_list
            ]

            for p in processes:
                for value in p.result():
                    values.append(value)

            debug_with_date(values)

            futures.wait(processes)
            
            # debug_with_date('start1')
            # self.__db_systems = parallel_executor(db_system_clients, compartments, self.__search_compartments, len(compartments), "__db_systems")
            # debug_with_date('start2')
            # self.__autonomous_databases = parallel_executor(db_system_clients, compartments, self.__search_auto_dbs, len(compartments), "__autonomous_databases")
            # debug_with_date('start3')
            # self.__mysql_databases = parallel_executor(mysql_clients, compartments, self.__search_mysql_dbs, len(compartments), "__mysql_databases")
            debug_with_date('stop')
        return self.__db_systems


    def analyze_entity(self, entry):
        self.load_entity()

        # debug_with_date(self.__db_systems)

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        

        return dictionary


    def __search_compartments(self, item):
        database_client = item[0]
        compartments = item[1:]

        databases = []

        for compartment in compartments:
            # All, 1 region: ~40 sec
            # All, 18 regions: ~50-60 seconds
            database_data = get_db_system_data(database_client, compartment.id) # 18 regions: 34 seconds
            # auto_database_data = get_auto_db_data(database_client, compartment.id)
            # mysql_data = get_db_system_data(mysql_client, compartment.id)
                
            # for database in database_data:
            #     record = {
                    
            #     }

            #     # databases.append(database)

            # for auto_database in auto_database_data:
            #     record = {
                    
            #     }

            #     # databases.append(auto_database)
            
            # for mysql_database in mysql_data:
            #     record = {
                    
            #     }

            #     # databases.append(mysql_database)

        return databases


    def __search_auto_dbs(self, item):
        database_client = item[0]
        compartments = item[1:]

        databases = []

        for compartment in compartments:
            auto_database_data = get_auto_db_data(database_client, compartment.id)

        return databases


    def __search_mysql_dbs(self, item):
        mysql_client = item[0]
        compartments = item[1:]

        databases = []

        for compartment in compartments:
            mysql_data = get_db_system_data(mysql_client, compartment.id)

        return databases
