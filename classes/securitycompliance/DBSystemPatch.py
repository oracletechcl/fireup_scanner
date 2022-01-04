# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# DBSystemPatch.py
# Description: Implementation of class DBsystemPatch based on abstract



from common.utils.formatter.printer import debug, debug_with_color_date, debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor



class DBSystemPatch(ReviewPoint):

    # Class Variables
    __identity = None

    __subnet_objects = []
    __subnets = []
    __oracle_database_objects = []
    __oracle_databases = []
    __oracle_databases_patches = []

    __compartments = []
    __autonomous_database_objects = []
    __autonomous_database_ocids = []

  
    


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
        self.__oracle_databases_patches = ParallelExecutor.executor(db_system_clients, self.__oracle_database_objects, ParallelExecutor.get_database_patches, len(self.__oracle_database_objects), ParallelExecutor.oracle_dbsystems_patches)      
       
        
        
        debug_with_date(self.__oracle_databases_patches)
      
        # Filling local array object for Oracle Database 
        # for dbobject in self.__oracle_database_objects:            
        #     orcl_db_record = {
        #         'compartment_id': dbobject.compartment_id,
        #         'display_name': dbobject.display_name,
        #         'id': dbobject.id,
        #         'subnet_id': dbobject.subnet_id,
        #         'nsg_ids': dbobject.nsg_ids,
                
        #     }
        #     self.__oracle_databases.append(orcl_db_record)
        
       

        
     

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



        