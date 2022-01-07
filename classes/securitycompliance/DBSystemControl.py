# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# SecurityList.py
# Description: Implementation of class SecurityList based on abstract



from common.utils.formatter.printer import debug, debug_with_color_date, debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor



class DBSystemControl(ReviewPoint):

    # Class Variables
    __identity = None

    __subnet_objects = []
    __subnets = []
    __oracle_database_objects = []
    __oracle_database_subnet_ocids = []
    __mysql_database_ocids = []
    __mysql_full_objects = []
    __compartments = []
    __autonomous_database_objects = []
    __autonomous_database_ocids = []
    __autonomous_database_nsgs = []
    __adb_nsg_objects = []
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
        mysql_clients = []
        network_clients = []


        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            db_system_clients.append( (get_database_client(region_config, self.signer), region.region_name, region.region_key.lower()) )
            mysql_clients.append( (get_mysql_client(region_config, self.signer), region.region_name, region.region_key.lower()) )
            network_clients.append( (get_virtual_network_client(region_config, self.signer), region.region_name, region.region_key.lower()) )

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(tenancy)
        
        self.__subnet_objects = ParallelExecutor.executor([x[0] for x in network_clients], self.__compartments, ParallelExecutor.get_subnets_in_compartments, len(self.__compartments), ParallelExecutor.subnets)
        self.__oracle_database_objects = ParallelExecutor.executor([x[0] for x in db_system_clients], self.__compartments, ParallelExecutor.get_oracle_dbsystem, len(self.__compartments), ParallelExecutor.oracle_dbsystems)
        self.__mysql_database_objects = ParallelExecutor.executor([x[0] for x in mysql_clients], self.__compartments, ParallelExecutor.get_mysql_dbs, len(self.__compartments), ParallelExecutor.mysql_dbsystems)
        self.__mysql_full_objects = ParallelExecutor.executor(mysql_clients, self.__mysql_database_objects, ParallelExecutor.get_mysql_dbsystem_full_info, len(self.__mysql_database_objects), ParallelExecutor.mysql_full_data)
        self.__autonomous_database_objects = ParallelExecutor.executor([x[0] for x in db_system_clients], self.__compartments, ParallelExecutor.get_autonomous_databases, len(self.__compartments), ParallelExecutor.autonomous_databases)
        self.__adb_nsg_objects = ParallelExecutor.executor(network_clients, self.__autonomous_database_objects, ParallelExecutor.get_adb_nsgs, len(self.__autonomous_database_objects), ParallelExecutor.adb_nsgs)
        




        # Filling local array object for MySQL Database OCIDS
        for mysqldbobject in self.__mysql_full_objects:           
            mysql_db_record = {
                'compartment_id': mysqldbobject.compartment_id,
                'display_name': mysqldbobject.display_name,
                'id': mysqldbobject.id,
                'subnet_id': mysqldbobject.subnet_id,
            }
            self.__mysql_database_ocids.append(mysql_db_record)

       
        # Filling local array object for Oracle Database Subnet OCIDs
        for dbobject in self.__oracle_database_objects:            
            orcl_db_record = {
                'compartment_id': dbobject.compartment_id,
                'display_name': dbobject.display_name,
                'id': dbobject.id,
                'subnet_id': dbobject.subnet_id,
                'nsg_ids': dbobject.nsg_ids,
                
            }
            self.__oracle_database_subnet_ocids.append(orcl_db_record)
        
        # Filling local array object for Autonomous Databases Subnet OCIDS
        for adb in self.__autonomous_database_objects:   
            record = {
                'display_name': adb.display_name,
                'dataguard_region_type': adb.dataguard_region_type,
                'compartment_id': adb.compartment_id,
                'id': adb.id,
                'time_created': adb.time_created,
                'nsg_ids': adb.nsg_ids,
                'subnet_id': adb.subnet_id,
                'compartment_id': adb.compartment_id,

            }
            self.__autonomous_database_ocids.append(record)

        # Filling local array for NSG contents

        for nsgs, adb in self.__adb_nsg_objects:
            for nsg in nsgs:             
                adb_nsg_record = {
                    'description': nsg.description,
                    'direction': nsg.direction,
                    'is_stateless': nsg.is_stateless,
                    'source': nsg.source,
                    'source_type': nsg.source_type,
                    'adb': adb.display_name,
                    'adb_id': adb.id,
                }
                self.__adb_nsgs.append(adb_nsg_record)

        # Filling local array for Subnet OCIDS and it's corresponding private flag
        for subnet in self.__subnet_objects:
            subnet_record = {
                'cidr_block': subnet.cidr_block,
                'compartment_id': subnet.compartment_id,
                'display_name': subnet.display_name,
                'dns_label': subnet.dns_label,
                'id': subnet.id,
                'lifecycle_state': subnet.lifecycle_state,
                'time_created': subnet.time_created,
                'vcn_id': subnet.vcn_id,
                'prohibit_internet_ingress': subnet.prohibit_internet_ingress,
                'prohibit_public_ip_on_vnic': subnet.prohibit_public_ip_on_vnic,
            }
            self.__subnets.append(subnet_record)
     

    def analyze_entity(self, entry):
    
        self.load_entity()    
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        
        # Cycle Check for MySQL Databases
        for mysql in self.__mysql_database_ocids:
            for subnet in self.__subnets:
               if mysql['subnet_id'] == subnet['id']:
                   if subnet['prohibit_public_ip_on_vnic'] == False:
                       dictionary[entry]['status'] = False
                       dictionary[entry]['findings'].append(mysql)   
                       dictionary[entry]['failure_cause'].append("MySQL Database is in a public subnet")
                       dictionary[entry]['mitigations'].append("MySQL Database: "+mysql['display_name']+ " located in compartment: "+get_compartment_name(self.__compartments, mysql['compartment_id'])+" needs to be in a private subnet")
        
        # Cycle Check for Oracle Databases
        for orcldb in self.__oracle_database_subnet_ocids:
            for subnet in self.__subnets:
               if orcldb['subnet_id'] == subnet['id']:
                   if subnet['prohibit_public_ip_on_vnic'] == False:
                        dictionary[entry]['status'] = False
                        dictionary[entry]['findings'].append(orcldb)                           
                        if orcldb['nsg_ids'] != None:                                     
                            dictionary[entry]['failure_cause'].append("Oracle Database in Public Subnet without NSG Attached")
                            dictionary[entry]['mitigations'].append("Oracle Database: "+orcldb['display_name']+ " located in compartment: "+get_compartment_name(self.__compartments, orcldb['compartment_id'])+" needs to be in a private subnet or attach a NSG")
                        else:
                            dictionary[entry]['failure_cause'].append("Oracle Database is in a public subnet")
                            dictionary[entry]['mitigations'].append("Oracle Database: "+orcldb['display_name']+ " located in compartment: "+get_compartment_name(self.__compartments, orcldb['compartment_id'])+" needs to be in a private subnet")                      

        # Check for empty NSGs into Autonomous Databases
        for adbs in self.__autonomous_database_ocids:
            for nsg_protected_adbs in self.__adb_nsgs:        
                if adbs['id'] == nsg_protected_adbs['adb_id']:
                    break
            else:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(adbs)   
                dictionary[entry]['failure_cause'].append("Autonomous Database protected with an Empty NSG")
                dictionary[entry]['mitigations'].append("NSG of Autonomous Database: "+str(adbs['display_name'])+" located in compartment: "+get_compartment_name(self.__compartments, adbs['compartment_id'])+" is empty")
                                                     
        return dictionary



        