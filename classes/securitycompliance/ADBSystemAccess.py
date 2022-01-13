# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ADBSystemAccess.py
# Description: Implementation of class ADBSystemAccess based on abstract



from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor




class ADBSystemAccess(ReviewPoint):

    # Class Variables
    __identity = None

    __subnet_objects = []
    __subnets = []
    __adbs = []
    __compartments = []
    __autonomous_database_objects = []
    __adb_nsgs = []

  
    


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
        # mysql_clients = []
        network_clients = []


        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            db_system_clients.append(get_database_client(region_config, self.signer))       
            network_clients.append( (get_virtual_network_client(region_config, self.signer), region.region_name, region.region_key.lower()) )

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(tenancy)        
             
        self.__autonomous_database_objects = ParallelExecutor.executor(db_system_clients, self.__compartments, ParallelExecutor.get_autonomous_databases, len(self.__compartments), ParallelExecutor.autonomous_databases)
        self.__adb_nsg_objects = ParallelExecutor.executor(network_clients, self.__autonomous_database_objects, ParallelExecutor.get_adb_nsgs, len(self.__autonomous_database_objects), ParallelExecutor.adb_nsgs)
        

        
      
        #Filling autonomous database object

        for adbobject in self.__autonomous_database_objects:
            adb_record = {
                "display_name": adbobject.display_name,
                "id": adbobject.id,
                "nsg_ids": adbobject.nsg_ids,
                "private_endpoint": adbobject.private_endpoint,
                "private_endpoint_ip": adbobject.private_endpoint_ip,
                "subnet_id": adbobject.subnet_id,
                "compartment_id": adbobject.compartment_id,
            }
            self.__adbs.append(adb_record)

    # Fill NSG Data
        for nsgs, adb in self.__adb_nsg_objects:         

            for nsg in nsgs:             
                adb_nsg_record = {
                    'description': nsg.description,
                    'direction': nsg.direction,
                    'is_stateless': nsg.is_stateless,
                    'protocol': nsg.protocol,
                    'tcp_options': nsg.tcp_options,
                    'udp_options': nsg.udp_options,
                    'source': nsg.source,
                    'source_type': nsg.source_type,
                    'adb': adb.display_name,
                    'adb_id': adb.id,
                    
                }
                self.__adb_nsgs.append(adb_nsg_record)    
     

    def analyze_entity(self, entry):
    
        self.load_entity()    
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        # Check if ADBs have private endpoints. If not, then check if they are located on a private subnet

        for adb in self.__adbs:
            if adb['private_endpoint'] == None:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(adb)   
                dictionary[entry]['failure_cause'].append("ADB has no private endpoint")
                dictionary[entry]['mitigations'].append("ADB Database: "+adb['display_name']+ " located in compartment: "+get_compartment_name(self.__compartments, adb['compartment_id'])+" doesn't contain a private endpoint. Ensure that the ADB has the proper restrictions for access")                                    
            else: 
                # Check that ADB is associated to an NSG which contains a stateless ingress rule with protocol TCP and destination port 1521 or 1522.
                for adb_nsg in self.__adb_nsgs:
                    if adb_nsg['adb_id'] == adb['id']:
                        if adb_nsg['direction'] == 'INGRESS' and adb_nsg['protocol'] == '6' and (adb_nsg['source'] == '1521' or adb_nsg['source'] == '1522'):
                            dictionary[entry]['status'] = True                            
                            break
                        else:
                            dictionary[entry]['status'] = False
                            dictionary[entry]['findings'].append(adb)
                            dictionary[entry]['failure_cause'].append("ADB does not contain a valid NSG Ingress configuration")
                            dictionary[entry]['mitigations'].append("ADB Database: "+adb['display_name']+ " located in compartment: "+get_compartment_name(self.__compartments, adb['compartment_id'])+" should contain a restrictive stateless Ingress Rule with Protocol TCP and Destination Port equal to the Database Listener Port (1521 and 1522)")
                            break
                # Check that ADB is associated to an NSG wehich contains a stateless egress rule with Protocol TCP which has any CIDR block as destination
                for adb_nsg in self.__adb_nsgs:
                    if adb_nsg['adb_id'] == adb['id']:
                        if adb_nsg['direction'] == 'EGRESS' and adb_nsg['protocol'] == '6': 
                            dictionary[entry]['status'] = True                            
                            break
                        else:
                            dictionary[entry]['status'] = False
                            dictionary[entry]['findings'].append(adb)
                            dictionary[entry]['failure_cause'].append("ADB does not contain a valid NSG Egress configuration")
                            dictionary[entry]['mitigations'].append("ADB Database: "+adb['display_name']+ " located in compartment: "+get_compartment_name(self.__compartments, adb['compartment_id'])+" should contain a restrictive stateless Egress Rule with Protocol TCP and Destination as Consumer Subnet CIDR Block ")
                            break
      
        
                
        
                                                     
        return dictionary



        