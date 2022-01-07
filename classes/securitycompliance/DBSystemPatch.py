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



class DBSystemPatch(ReviewPoint):

    # Class Variables
    __identity = None

    __subnet_objects = []
    __subnets = []
    __oracle_database_objects = []
    __oracle_databases_homes = []
    __oracle_databases_patches = []
    __oracle_databases_patches_history = []

    __compartments = []
    __autonomous_database_objects = []
    __autonomous_database_ocids = []

    __patches_website = "https://docs.oracle.com/en-us/iaas/Content/Database/Tasks/patchingDB.htm"
    __patches_website_id = "patchingDB_topic-Currently_Available_Patches"
    __scrapped_db_versions = []
    __all_patch_entries = []
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
        
        self.__oracle_database_objects = ParallelExecutor.executor([x[0] for x in db_system_clients], self.__compartments, ParallelExecutor.get_database_homes, len(self.__compartments), ParallelExecutor.db_system_homes)      
        #self.__oracle_database_systems = ParallelExecutor.executor([x[0] for x in db_system_clients], self.__compartments, ParallelExecutor.get_database_systems, len(self.__compartments), ParallelExecutor.db_systems)      
        self.__oracle_databases_patches = ParallelExecutor.executor(db_system_clients, self.__oracle_database_objects, ParallelExecutor.get_database_home_patches, len(self.__oracle_database_objects), ParallelExecutor.oracle_dbsystems_patches)      
        self.__oracle_databases_patches_history = ParallelExecutor.executor(db_system_clients, self.__oracle_database_objects, ParallelExecutor.get_database_homes_applied_patch_history, len(self.__oracle_database_objects), ParallelExecutor.oracle_db_home_patch_history)      

        self.__last_patch_level = get_db_patches(self.__patches_website, self.__patches_website_id)
              
               
        #debug_with_color_date(self.__oracle_databases_patches, "green")
        # debug_with_color_date(self.__oracle_database_systems, "green")
        # debug_with_color_date(self.__oracle_database_objects, "red")

        # Filling local array object for Oracle Database 
        for dbobject in self.__oracle_database_objects:            
            orcl_db_record = {
                'compartment_id': dbobject.compartment_id,
                'display_name': dbobject.display_name,
                'id': dbobject.id,                
            }
            self.__oracle_databases_homes.append(orcl_db_record)

        

        debug_with_color_date(self.__last_patch_level, "cyan")
        debug_with_color_date(self.__oracle_databases_homes, "red")
        debug_with_color_date(self.__oracle_databases_patches, "green")
        debug_with_color_date(self.__oracle_databases_patches_history, "blue")
        


       
        
     

    def analyze_entity(self, entry):
    
        self.load_entity()    
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        
       
        # Cycle Check for Oracle Databases
        # for orcldb in self.__oracle_database_subnet_ocids:
        #     for subnet in self.__subnets:
        #        if orcldb['subnet_id'] == subnet['id']:
        #            if subnet['prohibit_public_ip_on_vnic'] == False:
        #                 dictionary[entry]['status'] = False
        #                 dictionary[entry]['findings'].append(orcldb)                           
        #                 if orcldb['nsg_ids'] != None:                                     
        #                     dictionary[entry]['failure_cause'].append("Oracle Database in Public Subnet without NSG Attached")
        #                     dictionary[entry]['mitigations'].append("Oracle Database: "+orcldb['display_name']+ " located in compartment: "+get_compartment_name(self.__compartments, orcldb['compartment_id'])+" needs to be in a private subnet or attach a NSG")
        #                 else:
        #                     dictionary[entry]['failure_cause'].append("Oracle Database is in a public subnet")
        #                     dictionary[entry]['mitigations'].append("Oracle Database: "+orcldb['display_name']+ " located in compartment: "+get_compartment_name(self.__compartments, orcldb['compartment_id'])+" needs to be in a private subnet")                      
   
                                                     
        return dictionary


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
        #print(patch_table.prettify())

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
