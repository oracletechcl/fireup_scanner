# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# FileStorageEncryption.py
# Description: Implementation of class FileStorageEncryption based on abstract



from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor



class FileStorageEncryption(ReviewPoint):

    # Class Variables

    __file_system_objects = []
    __file_systems = []
   
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
       self.__tenancy = get_tenancy_data(self.__identity, self.config)


    def load_entity(self):

        file_storage_clients = []
        identity_clients = []
        
        regions = get_regions_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        # get clients from each region 
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            file_storage_clients.append((get_file_storage_client(region_config, self.signer),region.region_name, region.region_key.lower()))
            identity_clients.append(get_identity_client(region_config, self.signer))

        # Retrieve all availability domains
        # Solution taken from CheckBackupPolicies.py
        availability_domains = ParallelExecutor.get_availability_domains(identity_clients, self.__tenancy.id)

        file_system_clients_with_ADs = []

        for file_storage_client in file_storage_clients:
            for availability_domain in availability_domains:
                if file_storage_client[1][:-2] in availability_domain.lower() or file_storage_client[2] in availability_domain.lower():
                    file_system_clients_with_ADs.append( (file_storage_client[0], availability_domain) )
      
        self.__file_system_objects = ParallelExecutor.executor(file_system_clients_with_ADs, self.__compartments, ParallelExecutor.get_file_systems, len(self.__compartments), ParallelExecutor.file_systems)

        for file_system in self.__file_system_objects:
            record = {
                "compartment_id": file_system.compartment_id,
                "id": file_system.id,
                "kms_key_id": file_system.kms_key_id,
                "display_name": file_system.display_name,
                "availability_domain": file_system.availability_domain
            }
            self.__file_systems.append(record)


    def analyze_entity(self, entry):
    
        self.load_entity()     
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for file_system in self.__file_systems:
                if not file_system['kms_key_id']:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['findings'].append(file_system)
                    dictionary[entry]['failure_cause'].append("The File System is by default encrypted using an Oracle-managed master encryption key.")   
                    dictionary[entry]['mitigations'].append(f"For File System: \"{file_system['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, file_system['compartment_id'])}\" configure your own master encryption key that you store in the Oracle Cloud Infrastructure Vault service.")   
       
        return dictionary
