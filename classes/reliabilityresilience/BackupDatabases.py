# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# BackupDatabases.py
# Description: Implementation of class BackupDatabases based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *


class BackupDatabases(ReviewPoint):

    # Class Variables
    __db_system_homes = []
    __db_system_home_objects = []
    __mysql_databases = []
    __mysql_database_objects = []

    __db_systems_with_no_backups = []
    __mysql_dbs_with_no_backups = []
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
            mysql_backup_clients.append( (get_mysql_backup_client(region_config, self.signer), region.region_name, region.region_key.lower()) )

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__db_system_home_objects = ParallelExecutor.executor([x[0] for x in db_system_clients], compartments, ParallelExecutor.get_database_homes, len(compartments), ParallelExecutor.db_system_homes)

        for db_home in self.__db_system_home_objects:
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
                'availability_domain': '',
                'is_highly_available': '',
            }
            self.__db_system_homes.append(record)

        self.__mysql_database_objects = ParallelExecutor.executor(mysql_clients, compartments, ParallelExecutor.get_mysql_dbs, len(compartments), ParallelExecutor.mysql_databases)

        for mysql_db in self.__mysql_database_objects:
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
            self.__mysql_databases.append(record)

        if len(self.__mysql_databases) > 0:
            self.__mysql_dbs_with_no_backups = ParallelExecutor.executor(mysql_backup_clients, self.__mysql_databases, ParallelExecutor.get_mysql_dbs_with_no_backups, len(self.__mysql_databases), ParallelExecutor.mysql_dbs_with_no_backups)

        if len(self.__db_system_homes) > 0:
            self.__db_systems_with_no_backups = ParallelExecutor.executor(db_system_clients, self.__db_system_homes, ParallelExecutor.get_db_systems_with_no_backups, len(self.__db_system_homes), ParallelExecutor.db_systems_with_no_backups)

        return self.__mysql_dbs_with_no_backups, self.__db_systems_with_no_backups


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for db, db_home in self.__db_systems_with_no_backups:
            dictionary[entry]['status'] = False
            dictionary[entry]['findings'].append(db_home)
            dictionary[entry]['failure_cause'].append('Each Database System database should have automatic backup enabled')
            dictionary[entry]['mitigations'].append(f"Make sure database {db.db_name} within database home {db_home['display_name']} has automatic backup enabled.")

        for mysql_database in self.__mysql_dbs_with_no_backups:
            dictionary[entry]['status'] = False
            dictionary[entry]['findings'].append(mysql_database)
            dictionary[entry]['failure_cause'].append('Each MySQL Database should have automatic backup enabled')
            dictionary[entry]['mitigations'].append(f"Make sure MySQL Database {mysql_database['display_name']} has automatic backup enabled.")

        return dictionary
