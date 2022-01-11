# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# DBSystemPatch.py
# Description: Implementation of class DBsystemPatch based on abstract



from common.utils.formatter.printer import debug, debug_with_color_date, debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.helpers.WebScrapper import *
import pandas as pd
from operator import itemgetter



class DBSystemPatch(ReviewPoint):

    # Class Variables
    __identity = None

    #DB Full Objects
    __oracle_database_home_objects = []
    __oracle_database_systems_objects = []

   # Patch history 
    __oracle_databases_homes_patches_history = []
    __oracle_database_system_patches_history = []

    # Patched curated objects
    __dbhome_patches = []
    __dbsystem_patches = []


    # Usable DB Objects
    __oracle_databases_homes = []
    __oracle_database_systems = []
    __compartments = []



    # Scrapper variables
    __patches_website = "https://docs.oracle.com/en-us/iaas/Content/Database/Tasks/patchingDB.htm"
    __patches_website_id = "patchingDB_topic-Currently_Available_Patches"
    __last_patch_level = None

  
    


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


        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            db_system_clients.append( (get_database_client(region_config, self.signer), region.region_name, region.region_key.lower()) )

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(tenancy)
        
        self.__oracle_database_home_objects = ParallelExecutor.executor([x[0] for x in db_system_clients], self.__compartments, ParallelExecutor.get_database_homes, len(self.__compartments), ParallelExecutor.db_system_homes)      
        self.__oracle_database_systems_objects = ParallelExecutor.executor([x[0] for x in db_system_clients], self.__compartments, ParallelExecutor.get_database_systems, len(self.__compartments), ParallelExecutor.db_systems)      

        self.__oracle_databases_home_patches_history = ParallelExecutor.executor(db_system_clients, self.__oracle_database_home_objects, ParallelExecutor.get_database_homes_applied_patch_history, len(self.__oracle_database_home_objects), ParallelExecutor.oracle_db_home_patch_history)      
        self.__oracle_database_system_patches_history = ParallelExecutor.executor(db_system_clients, self.__oracle_database_systems_objects, ParallelExecutor.get_database_systems_applied_patch_history, len(self.__oracle_database_systems_objects), ParallelExecutor.oracle_db_system_patch_history)

        self.__last_patch_level = get_db_patches(self.__patches_website, self.__patches_website_id)
              
        # Filling local array object for Oracle Database 
        for dbobject in self.__oracle_database_home_objects:            
            orcl_db_record = {
                'compartment_id': dbobject.compartment_id,
                'display_name': dbobject.display_name,
                'id': dbobject.id,                
            }
            self.__oracle_databases_homes.append(orcl_db_record)

        for dbobject in self.__oracle_database_systems_objects:
            orcl_db_record = {
                'compartment_id': dbobject.compartment_id,
                'display_name': dbobject.display_name,
                'id': dbobject.id,
            }
            self.__oracle_database_systems.append(orcl_db_record)


        self.__dbhome_patches = get_db_home_latest_patching_details(self.__oracle_databases_home_patches_history)
        self.__dbsystem_patches = get_db_system_latest_patching_details(self.__oracle_database_system_patches_history)


        

       
        
     

    def analyze_entity(self, entry):
    
        self.load_entity()    
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        

        # iterate through variable self.__dbhome_patches and self.__last_patch_level. If the versions of the database are the same, then print out the patch level of database and patch applicable to that version
        for dbhome_applied_patches in self.__dbhome_patches:
            for latest_patches_available in self.__last_patch_level:
                if dbhome_applied_patches['db_home_version'] != None: 
                    if latest_patches_available['db_version'][0:2] in dbhome_applied_patches['db_home_version']:
                        if dbhome_applied_patches['db_home_latest_applied_patch'] != None:
                            if get_month_and_year(latest_patches_available['db_home_patch']) not in dbhome_applied_patches['db_home_latest_applied_patch'].lower(): 
                                dbname = self.__get_db_name(dbhome_applied_patches['db_home_id'], "db_home_id")
                                dictionary[entry]['status'] = False
                                dictionary[entry]['findings'].append(dbhome_applied_patches)
                                dictionary[entry]['failure_cause'].append("Oracle DB Home does not have the latest patchset applied")                                   
                                dictionary[entry]['mitigations'].append("Apply Patchset: "+get_month_and_year(latest_patches_available['db_home_patch']) + " to "+ dbname)
                                break                      

                        else:
                                dbname = self.__get_db_name(dbhome_applied_patches['db_home_id'], "db_home")
                                dictionary[entry]['status'] = False
                                dictionary[entry]['findings'].append(dbhome_applied_patches)
                                dictionary[entry]['failure_cause'].append("Oracle DB Home does not have any patches applied")                                   
                                dictionary[entry]['mitigations'].append("Apply Patchset: "+get_month_and_year(latest_patches_available['db_home_patch']) +" to database: "+ dbname)
                                break   
       
        for dbsystem_applied_patches in self.__dbsystem_patches:
            for latest_patches_available in self.__last_patch_level:
                if dbsystem_applied_patches['db_system_version'] != None: 
                    if latest_patches_available['db_version'][0:2] in dbsystem_applied_patches['db_system_version']:   
                        if dbsystem_applied_patches['db_system_latest_applied_patch'] != None and dbsystem_applied_patches['db_system_version'] != None:
                            if get_month_and_year(latest_patches_available['db_system_patch']) not in dbsystem_applied_patches['db_system_latest_applied_patch'].lower(): 
                                dbname = self.__get_db_name(dbsystem_applied_patches['db_system_id'], "db_system")
                                dictionary[entry]['status'] = False
                                dictionary[entry]['findings'].append(dbsystem_applied_patches)
                                dictionary[entry]['failure_cause'].append("Oracle DB System does not have the latest patchset applied")                                   
                                dictionary[entry]['mitigations'].append("Apply Patchset: "+get_month_and_year(latest_patches_available['db_system_patch']) + " to "+ dbname) 
                                break                     

                        else:
                                dbname = self.__get_db_name(dbsystem_applied_patches['db_system_id'], "db_system")
                                dictionary[entry]['status'] = False
                                dictionary[entry]['findings'].append(dbsystem_applied_patches)
                                dictionary[entry]['failure_cause'].append("Oracle DB System does not have any patches applied")                                   
                                dictionary[entry]['mitigations'].append("Apply Patchset: "+get_month_and_year(latest_patches_available['db_system_patch']) +" to dbsystem: "+ dbname)
                                break              
                
                                                     
        return dictionary

    def __get_db_name(self, db_ocid, db_type):
        if db_type == "db_home":
            for db_obj in self.__oracle_databases_homes:
                if db_obj['id'] == db_ocid:
                    return db_obj['display_name']
            return None
        elif db_type == "db_system":
            for db_obj in self.__oracle_database_systems:
                if db_obj['id'] == db_ocid:
                    return db_obj['display_name']
            return None

def get_month_and_year(patchset_date):
   # based on patchset date that comes in format Month Year, return the values in Month format of 3 letters in lowercase and the year. example: "October 2021" -> "oct 2021"
    month_year = patchset_date.split(" ")
    if len(month_year[0]) >= 3:
        return month_year[0][0:3].lower() + " " + month_year[1]
    else:
        return month_year[0].lower() + " " + month_year[1]





def get_db_patches(patches_website, patches_website_id):
    db_versions = []
    db_home_patches = []
    db_system_patches = []
    scrapped_db_versions = []
    all_patch_entries = []
    tuple = {}
    results_to_compare = []

    #Get the table to perform webscrapping
    patch_table = scrap_from_website(patches_website, patches_website_id)

    #Call scrapper helpers to get full objects to later iterate
        
    scrapper_db_versions = patch_table.find_all("th", class_="entry")
    scrapper_all_patches = patch_table.find_all("td", class_="entry")
    
    #Assign objects to list for manipulation
    scrapped_db_versions = get_scrapped_list(scrapper_db_versions)
    all_patch_entries = get_scrapped_list(scrapper_all_patches)

    
    #Assign available versions to db_versions array    
    for i in range(3,len(scrapped_db_versions)):
        db_versions.append(scrapped_db_versions[i])
        
    for i in range(0,len(all_patch_entries), 2):
        db_system_patches.append(all_patch_entries[i])

    for i in range(1,len(all_patch_entries), 2):
        db_home_patches.append(all_patch_entries[i])

    

    df = pd.DataFrame({'db_versions': db_versions, 'db_system_patches': db_system_patches, 'db_home_patches': db_home_patches})    
    
   #iterate on dataframe df and get the version of the db and the first entry of db_system_patches and db_home_patches
    for index, row in df.iterrows():
        db_version = row['db_versions']
        db_system_patch = get_first_entry(row['db_system_patches'])
        db_home_patch = get_first_entry(row['db_home_patches'])
        tuple = {'db_version': db_version, 'db_system_patch': db_system_patch, 'db_home_patch': db_home_patch}          
        results_to_compare.append(tuple)

    return results_to_compare


def get_first_entry(list):
    #First entry on documention will always be the latest and greatest patch set level available
    return list.split(",")[0]

def get_latest_patchset_per_db_version(db_version, patch_tuple):
    for tuple in patch_tuple:
        if tuple['db_version'] == db_version:
            return tuple['db_home_patch']


def get_db_home_latest_patching_details(db_home_collection):
   
    db_home_applied_patches = []

    for db_registry in db_home_collection:
        if db_registry['patch_id'] != "" and db_registry['patch_id'] != None:
                latest_applied_patch = get_db_home_patch_details(db_registry['database_client'], db_registry['db_home_ocid'], db_registry['patch_id']).description
                db_home_patches_dict = {
                    'db_home_id': db_registry['db_home_ocid'],
                    'db_home_latest_applied_patch': latest_applied_patch,            
                    'db_home_version': db_registry['db_version']                     
                    }            
        elif db_registry['patch_id'] == None:
                db_home_patches_dict = {
                    'db_home_id': db_registry['db_home_ocid'],
                    'db_home_latest_applied_patch': None,
                    'db_home_version': db_registry['db_version']                     
                    }   
            
        db_home_applied_patches.append(db_home_patches_dict)
      
    return db_home_applied_patches

def get_db_system_latest_patching_details(db_system_collection):
    db_system_applied_patches = []

    for db_registry in db_system_collection:    
        if db_registry['patch_id'] != "" and db_registry['patch_id'] != None:
                latest_applied_patch = get_db_system_patch_details(db_registry['database_client'], db_registry['db_system_ocid'], db_registry['patch_id']).description
                db_home_patches_dict = {
                    'db_system_id': db_registry['db_system_ocid'],
                    'db_system_latest_applied_patch': latest_applied_patch,        
                    'db_system_version': db_registry['db_version']                     
                    }            
        elif db_registry['patch_id'] == None:
                db_home_patches_dict = {
                    'db_system_id': db_registry['db_system_ocid'],
                    'db_system_latest_applied_patch': None,
                    'db_system_version': db_registry['db_version']                     
                    }      
        db_system_applied_patches.append(db_home_patches_dict)
        
       
    return db_system_applied_patches


