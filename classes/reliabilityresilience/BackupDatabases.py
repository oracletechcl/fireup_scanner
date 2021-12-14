# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# BackupDatabases.py
# Description: Implementation of class BackupDatabases based on abstract

from datetime import datetime, timedelta
from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *


class BackupDatabases(ReviewPoint):

    # Class Variables
    __db_systems = []
    __mysql_databases = []

    __mysql_backups = []
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
        mysql_backup_clients = []

        # for region in regions:
        #     region_config = self.config
        #     region_config['region'] = region.region_name
        #     db_system_clients.append(get_database_client(region_config, self.signer))
        #     mysql_clients.append(get_mysql_client(region_config, self.signer))

        # TEMPORARY REPLACEMENT OF ABOVE FOR SINGLE REGION
        region_config = self.config
        region_config['region'] = 'uk-london-1'

        db_system_clients.append(get_database_client(region_config, self.signer))
        mysql_clients.append(get_mysql_client(region_config, self.signer))
        mysql_backup_clients.append(get_mysql_backup_client(region_config, self.signer))
        # TEMPORARY REPLACEMENT OF ABOVE FOR SINGLE REGION

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        args_list = [
            [db_system_clients, compartments, self.__search_compartments, len(compartments), "__db_systems"],
            [mysql_clients, compartments, self.__search_mysql_dbs, len(compartments), "__mysql_databases"],
        ]

        with futures.ThreadPoolExecutor(16) as executor:
            debug_with_date('start')
            processes = [
                executor.submit(parallel_executor, *args)
                for args in args_list
            ]

            futures.wait(processes)

            self.__db_systems = processes[0].result()
            self.__autonomous_databases = processes[1].result()
            self.__mysql_databases = processes[2].result()

            debug_with_date('stop')

        if len(self.__mysql_databases) > 0:
            self.__mysql_backups = parallel_executor(mysql_backup_clients, self.__mysql_databases, self.__search_mysql_backups, len(self.__mysql_databases), "__mysql_backups")

    def analyze_entity(self, entry):
        self.load_entity()

        # debug_with_date(self.__mysql_backups)

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        return dictionary


    def __search_compartments(self, item):
        database_client = item[0]
        compartments = item[1:]

        databases = []

        for compartment in compartments:
            database_data = get_db_system_data(database_client, compartment.id)
            for db in database_data:
                databases.append(db)

        return databases


    def __search_mysql_dbs(self, item):
        mysql_client = item[0]
        compartments = item[1:]

        databases = []

        for compartment in compartments:
            mysql_data = get_db_system_data(mysql_client, compartment.id)
            for mysql_db in mysql_data:
                if "DELETED" not in mysql_db.lifecycle_state:
                    record = {
                        'availability_domain': mysql_db.availability_domain,
                        'compartment_id': mysql_db.compartment_id,
                        'current_placement': mysql_db.current_placement,
                        'defined_tags': mysql_db.defined_tags,
                        'description': mysql_db.description,
                        'display_name': mysql_db.display_name,
                        'endpoints': mysql_db.endpoints,
                        'fault_domain': mysql_db.fault_domain,
                        'heat_wave_cluster': mysql_db.heat_wave_cluster,
                        'id': mysql_db.id,
                        'is_analytics_cluster_attached': mysql_db.is_analytics_cluster_attached,
                        'is_heat_wave_cluster_attached': mysql_db.is_heat_wave_cluster_attached,
                        'is_highly_available': mysql_db.is_highly_available,
                        'lifecycle_state': mysql_db.lifecycle_state,
                        'mysql_version': mysql_db.mysql_version,
                        'time_created': mysql_db.time_created,
                        'time_updated': mysql_db.time_updated,
                    }

                    databases.append(record)

        return databases


    def __search_mysql_backups(self, item):
        mysql_backup_client = item[0]
        mysql_databases = item[1:]

        backups = []
        backup_window = 10

        # Checks that each MySQL DB has a backup within the last `backup_window` days
        for mysql_database in mysql_databases:
            backup_data = get_mysql_backup_data(mysql_backup_client, mysql_database['compartment_id'])
            for backup in backup_data:
                if "DELETED" not in backup.lifecycle_state:
                    if mysql_database['id'] == backup.db_system_id:
                        latest = backup.time_created.replace(tzinfo=None)
                        if datetime.now() < (latest + timedelta(days=backup_window)):
                            break
            else:
                backups.append(mysql_database)
        
        return backups
