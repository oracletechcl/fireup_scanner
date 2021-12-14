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
    __db_system_homes = []
    __mysql_databases = []

    __db_system_backups = []
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

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            db_system_clients.append( (get_database_client(region_config, self.signer), region.region_name, region.region_key.lower()) )
            mysql_clients.append(get_mysql_client(region_config, self.signer))
            mysql_backup_clients.append(get_mysql_backup_client(region_config, self.signer))

        # TEMPORARY REPLACEMENT OF ABOVE FOR SINGLE REGION
        # region_config = self.config
        # region_config['region'] = 'us-ashburn-1'
        # # uk-london-1, us-ashburn-1, sa-santiago-1

        # db_system_clients.append(get_database_client(region_config, self.signer))
        # mysql_clients.append(get_mysql_client(region_config, self.signer))
        # mysql_backup_clients.append(get_mysql_backup_client(region_config, self.signer))
        # TEMPORARY REPLACEMENT OF ABOVE FOR SINGLE REGION

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        args_list = [
            [[x[0] for x in db_system_clients], compartments, self.__search_compartments, len(compartments), "__db_system_homes"],
            [mysql_clients, compartments, self.__search_mysql_dbs, len(compartments), "__mysql_databases"],
        ]

        with futures.ThreadPoolExecutor(16) as executor:
            processes = [
                executor.submit(parallel_executor, *args)
                for args in args_list
            ]

            futures.wait(processes)

            self.__db_system_homes = processes[0].result()
            self.__mysql_databases = processes[1].result()

        if len(self.__mysql_databases) > 0:
            self.__mysql_backups = parallel_executor(mysql_backup_clients, self.__mysql_databases, self.__search_mysql_backups, len(self.__mysql_databases), "__mysql_backups")

        if len(self.__db_system_homes) > 0:
            self.__db_system_backups = parallel_executor(db_system_clients, self.__db_system_homes, self.__search_db_system_backups, len(self.__db_system_homes), "__db_system_backups")

        return self.__mysql_backups, self.__db_system_backups


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for db, db_home in self.__db_system_backups:
            dictionary[entry]['status'] = False
            dictionary[entry]['findings'].append(db_home)
            dictionary[entry]['failure_cause'].append('Each Database System database should have automatic backup enabled')
            dictionary[entry]['mitigations'].append(f"Make sure database {db.db_name} within database home {db_home['display_name']} has automatic backup enabled.")

        for mysql_database in self.__mysql_backups:
            dictionary[entry]['status'] = False
            dictionary[entry]['findings'].append(mysql_database)
            dictionary[entry]['failure_cause'].append('Each MySQL Database should have automatic backup enabled')
            dictionary[entry]['mitigations'].append(f"Make sure MySQL Database {mysql_database['display_name']} has automatic backup enabled.")

        return dictionary


    def __search_compartments(self, item):
        database_client = item[0]
        compartments = item[1:]

        db_homes = []

        for compartment in compartments:
            database_home_data = get_db_system_home_data(database_client, compartment.id)
            for db_home in database_home_data:
                if "DELETED" not in db_home.lifecycle_state:
                    record = {
                        'compartment_id': db_home.compartment_id,
                        'defined_tags': db_home.defined_tags,
                        'display_name': db_home.display_name,
                        'id': db_home.id,
                        'time_created': db_home.time_created,
                        'db_system_id': db_home.db_system_id,
                        'db_version': db_home.db_version,
                        'lifecycle_state': db_home.lifecycle_state,
                        'vm_cluster_id': db_home.vm_cluster_id,
                        'current_placement': '',
                        'description': '',
                        'endpoints': '',
                        'heat_wave_cluster': '',
                        'mysql_version': '',
                    }

                    db_homes.append(record)

        return db_homes


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
                        'heat_wave_cluster': mysql_db.heat_wave_cluster,
                        'id': mysql_db.id,
                        'is_highly_available': mysql_db.is_highly_available,
                        'lifecycle_state': mysql_db.lifecycle_state,
                        'mysql_version': mysql_db.mysql_version,
                        'time_created': mysql_db.time_created,
                        'db_system_id': '',
                        'db_version': '',
                        'vm_cluster_id': '',
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


    def __search_db_system_backups(self, item):
        database_client = item[0]
        db_system_homes = item[1:]

        disabled_backups = []

        for db_home in db_system_homes:
            region = db_home['id'].split('.')[3]
            if database_client[1] in region or database_client[2] in region:
                databases = database_client[0].list_databases(db_home_id=db_home['id'], system_id=db_home['db_system_id'], compartment_id=db_home['compartment_id']).data
                for db in databases:
                    if not db.db_backup_config.auto_backup_enabled:
                        disabled_backups.append( (db, db_home) )

        return disabled_backups
