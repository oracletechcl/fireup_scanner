# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# BackupDatabases.py
# Description: Implementation of class BackupDatabases based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *


class BackupDatabases(ReviewPoint):

    # Class Variables
    __databases = []
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
        database_clients = []

        # for region in regions:
        #     region_config = self.config
        #     region_config['region'] = region.region_name
        #     # Create a network client for each region
        #     database_clients.append(get_database_client(region_config, self.signer))

        # TEMPORARY REPLACEMENT OF ABOVE FOR SINGLE REGION
        region_config = self.config
        region_config['region'] = 'us-ashburn-1'

        database_clients.append(get_database_client(region_config, self.signer))
        # TEMPORARY REPLACEMENT OF ABOVE FOR SINGLE REGION

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        debug_with_date('start')
        self.__databases = parallel_executor(database_clients, compartments, self.__search_compartments, len(compartments), "__databases")
        debug_with_date('stop')
        return self.__databases


    def analyze_entity(self, entry):
        self.load_entity()

        debug_with_date(self.__databases)

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        

        return dictionary


    def __search_compartments(self, item):
        database_client = item[0]
        compartments = item[1:]

        databases = []

        for compartment in compartments:
            database_data = get_db_system_data(database_client, compartment.id)
                
            for database in database_data:
                record = {
                    
                }

                databases.append(database)

        return databases
