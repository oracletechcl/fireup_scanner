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

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_root_compartment_data(self.__identity, self.__tenancy.id))

        self.__jobs_objects = ParallelExecutor.executor(resource_manager_clients, self.__compartments, ParallelExecutor.get_resource_manager_jobs, len(self.__compartments), ParallelExecutor.jobs)
        self.__vcns_objects = ParallelExecutor.executor(network_clients, self.__compartments, ParallelExecutor.get_vcns_in_compartments, len(self.__compartments), ParallelExecutor.vcns)


    def analyze_entity(self, entry):

        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        com_region_with_infrastructure = {}

        # Find unique compartment + region which has infrastructure
        for vcn in self.__vcns_objects:      
            vcn_compartment = vcn.compartment_id
            vcn_region = vcn.id.split('.')[3]
            com_region_with_infrastructure[(vcn_compartment,vcn_region)] = vcn

        # Iterate through unique compartment/region to find if there were
        # any jobs created in the Resource Manager 
        for com_reg in com_region_with_infrastructure:
            has_resource_manager_in_use = False

            for job in self.__jobs_objects:
                job_region = job[0].id.split('.')[3]

                if com_reg == (job[0].compartment_id, job_region):
                    has_resource_manager_in_use = True
                    break

            if not has_resource_manager_in_use:
                compartment_name = get_compartment_name(self.__compartments,com_reg[0])
                report_entry = {
                    'Compartment name': compartment_name,
                    'Compartment id': com_reg[0],
                    'Region': com_reg[1]}

                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(report_entry) 
                dictionary[entry]['failure_cause'].append("Terraform with Resource Manager is not in use")
                dictionary[entry]['mitigations'].append(f"In compartment: \"{compartment_name}\" in Region: \"{com_reg[1]}\" Consider managing your infrastructure with the use of Terraform and/or Resource Manager. ")
        
        return dictionary


    
