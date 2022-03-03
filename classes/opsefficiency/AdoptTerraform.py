# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# AdoptTerraform.py
# Description: Implementation of class AdoptTerraform based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class AdoptTerraform(ReviewPoint):

    # Class Variables   
    __compartments_objects = []
    __compartments = []
    __jobs_objects = []
    __vcns_objects = []

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

        resource_manager_clients = []
        network_clients = []
        
        self.__regions = get_regions_data(self.__identity, self.config)

        for region in self.__regions:
            region_config = self.config
            region_config['region'] = region.region_name
            resource_manager_clients.append(get_resource_manager_client(region_config, self.signer))
            network_clients.append(get_virtual_network_client(region_config, self.signer))

        self.__compartments_objects = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments_objects.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        for compartment in self.__compartments_objects:
            record = {
                "compartment_id": compartment.compartment_id, 
                "description":compartment.description,             
                "id":compartment.id,         
                "name":compartment.name,
                "region": ''
            }
            self.__compartments.append(record)

        self.__jobs_objects = ParallelExecutor.executor(resource_manager_clients, self.__compartments_objects, ParallelExecutor.get_resource_manager_jobs, len(self.__compartments_objects), ParallelExecutor.jobs)
        self.__vcns_objects = ParallelExecutor.executor(network_clients, self.__compartments_objects, ParallelExecutor.get_vcns_in_compartments, len(self.__compartments_objects), ParallelExecutor.vcns)

    def analyze_entity(self, entry):

        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        total = 0
        com_region_with_infrastructure = {}

        # Find unique compartment + region which has infrastructure
        for vcn in self.__vcns_objects:      
            vcn_region = vcn.id.split('.')[3]
            vcn_compartment = vcn.compartment_id
            com_region_with_infrastructure[(vcn_compartment,vcn_region)] = vcn
        # Iterate thru unique com_reg to find if there were
        # any jobs created in the resource manager

        for com_reg in com_region_with_infrastructure:
            debug(f"{get_compartment_name(self.__compartments_objects, com_reg[0])}, {com_reg[1]}", 'red')
            has_resource_manager_in_use = False

            for job in self.__jobs_objects:
                job_region = job[0].id.split('.')[3]

                if com_reg == (job[0].compartment_id, job_region):
                    has_resource_manager_in_use = True
                    break

            if not has_resource_manager_in_use:
                compartment = [x for x in self.__compartments if x['id'] == com_reg[0]][0]

                compartment['region'] = com_reg[1]
                compartment['total'] = total
                total+=1

                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(compartment) 
                dictionary[entry]['failure_cause'].append("Resource Manager is not in use for infrastructure deployment")
                dictionary[entry]['mitigations'].append(f"In compartment: \"{get_compartment_name(self.__compartments_objects, compartment['id'])}\" Region: \"{compartment['region']}\" total = {compartment['total']} Consider managing oci infrastructure with a use of Terraform and Resource Manager. ")
        
        return dictionary


    
