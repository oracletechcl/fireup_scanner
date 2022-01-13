# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# DBKeys.py
# Description: Implementation of class DBKeys based on abstract



from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor
import datetime



class DBKeys(ReviewPoint):

    # Class Variables
    __identity = None

    __adb_entry = []
    __compartments = []
    __autonomous_database_objects = []
    __now = datetime.datetime.now()
    __now_formatted = __now.strftime("%d/%m/%Y %H:%M:%S")

  
    


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
               
        self.__autonomous_database_objects = ParallelExecutor.executor([x[0] for x in db_system_clients], self.__compartments, ParallelExecutor.get_autonomous_databases, len(self.__compartments), ParallelExecutor.autonomous_databases)
        
        
      
        
        # Filling local array object for Autonomous Databases Subnet OCIDS
        for adb in self.__autonomous_database_objects: 
            adb_record = {
                'display_name': adb.display_name,
                'id': adb.id,
                'compartment_id': adb.compartment_id,
                'key_history_entry': adb.key_history_entry,
                'lifecycle_state': adb.lifecycle_state,
            }
            self.__adb_entry.append(adb_record)
        
     

    def analyze_entity(self, entry):
    
        self.load_entity()    
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        
        
        # Cycle Check for Autonomous Database Key Entry
        if len(self.__adb_entry) > 0:            
            for adb in self.__adb_entry:
                if "TERMINATED" not in adb['lifecycle_state'] or "TERMINATING" not in adb['lifecycle_state']:
                    for key_entry in adb['key_history_entry']:
                        time_created = key_entry.time_activated
                        time_now = datetime.datetime.strptime(self.__now_formatted, "%d/%m/%Y %H:%M:%S")
                        time_difference = time_now - time_created.replace(tzinfo=None)
                        id = adb['id']
                        region = id.split('.')[3]
                        if time_difference.days > 90:
                            dictionary[entry]['findings'].append(adb)
                            dictionary[entry]['status'] = False
                            dictionary[entry]['failure_cause'].append('Encryption Key used in ADB is older than 90 days')
                            dictionary[entry]['mitigations'].append('Update Encryption Key of ADB: '+str(adb['display_name'])+' located in compartment: '+ get_compartment_name(self.__compartments, adb['compartment_id'])+' in region: '+region)


     
                                                     
        return dictionary



        