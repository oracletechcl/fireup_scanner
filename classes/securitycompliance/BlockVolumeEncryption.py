# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# BlockVolumeEncryption.py
# Description: Implementation of class BlockVolumeEncryption based on abstract



from common.utils.formatter.printer import debug
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor



class BlockVolumeEncryption(ReviewPoint):

    # Class Variables
    __identity = None
    __tenancy = None
    __compartments = []
    __block_volume_objects = []
    __block_volumes = []
    __block_volume_backups_objects = []
    __block_volume_backups = []
    __block_volume_attachments_objects = []
    __block_volume_attachments = []
    
    
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

        block_volume_clients = []
        compute_clients = []
        regions = get_regions_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

         # get clients from each region 
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            block_volume_clients.append(get_block_storage_client(region_config, self.signer))
            compute_clients.append(get_compute_client(region_config, self.signer))

        self.__block_volume_objects = ParallelExecutor.executor(block_volume_clients, self.__compartments, ParallelExecutor.get_block_volumes, len(self.__compartments), ParallelExecutor.block_volumes)     
        self.__block_volume_backups_objects = ParallelExecutor.executor(block_volume_clients, self.__compartments, ParallelExecutor.get_block_volumes_backups, len(self.__compartments), ParallelExecutor.block_volume_backups)     
        self.__block_volume_attachments_objects = ParallelExecutor.executor(compute_clients, self.__compartments, ParallelExecutor.get_volume_attachements, len(self.__compartments), ParallelExecutor.volume_attachments)     

        for it, volume in enumerate(self.__block_volume_objects + self.__block_volume_backups_objects):
            record = {
                "compartment_id":volume.compartment_id, 
                "id":volume.id, 
                "kms_key_id":volume.kms_key_id, 
                "display_name":volume.display_name
            }          
            if it <= len(self.__block_volume_objects)-1:
                self.__block_volumes.append(record)
            else:
                self.__block_volume_backups.append(record)

        for attachment in self.__block_volume_attachments_objects:
            record = {
                "attachment_type":attachment.attachment_type, 
                "compartment_id":attachment.compartment_id, 
                "display_name":attachment.display_name, 
                "id":attachment.id,
                "instance_id":attachment.instance_id,
                "is_pv_encryption_in_transit_enabled":attachment.is_pv_encryption_in_transit_enabled,
                "lifecycle_state":attachment.lifecycle_state,
                "volume_id":attachment.volume_id
            }
            self.__block_volume_attachments.append(record)

    def analyze_entity(self, entry):
    
        self.load_entity()     
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for volume in self.__block_volumes:
            if not volume['kms_key_id']:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(volume)
                dictionary[entry]['failure_cause'].append("The Block Volume is by default encrypted using an Oracle-managed master encryption key.")   
                dictionary[entry]['mitigations'].append(f"For Block Volume: \"{volume['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, volume['compartment_id'])}\" configure your own master encryption key that you store in the Oracle Cloud Infrastructure Vault service.")   
       
        for backup in self.__block_volume_backups:
            if not backup['kms_key_id']:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(backup)
                dictionary[entry]['failure_cause'].append("The Block Volume Backup is by default encrypted using an Oracle-managed master encryption key.")   
                dictionary[entry]['mitigations'].append(f"For Block Volume Backup: \"{backup['display_name']}\" in compartment: \"{get_compartment_name(self.__compartments, backup['compartment_id'])}\" configure your own master encryption key that you store in the Oracle Cloud Infrastructure Vault service.")   

        for attachment in self.__block_volume_attachments:
            if attachment['lifecycle_state'] == 'ATTACHED':
                if attachment['attachment_type'] == 'paravirtualized':
                    if not attachment['is_pv_encryption_in_transit_enabled']:
                        dictionary[entry]['status'] = False
                        dictionary[entry]['findings'].append(attachment)
                        dictionary[entry]['failure_cause'].append("In transit encryption is not enable for Block Volume")   
                        dictionary[entry]['mitigations'].append(f"For Block Volume: \"{get_block_volume_name(self.__block_volume_objects,attachment['volume_id'])}\" in compartment: \"{get_compartment_name(self.__compartments, attachment['compartment_id'])}\" enable in transit encryption between volume and an instance.")  

        return dictionary
