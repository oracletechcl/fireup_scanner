# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# MaxSecurityZoneEnabled.py
# Description: Implementation of class MaxSecurityZoneEnabled based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class MaxSecurityZoneEnabled(ReviewPoint):

    # Class Variables
    __identity = None
    __max_sec_zone = []


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
        network_clients = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            network_clients.append(get_virtual_network_client(region_config, self.signer))

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_root_compartment_data(self.__identity, tenancy.id))

        for comp in compartments:
            comp_max_sec_zone = get_max_security_zone_data(self.__identity, comp.id)
            if "isMaximumSecurityZone" not in comp_max_sec_zone:
                self.__max_sec_zone.append(comp_max_sec_zone)


    def analyze_entity(self, entry):
    
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for msc in self.__max_sec_zone:
            if len(self.__max_sec_zone) > 0:
                dictionary[entry]['status'] = False
                dictionary[entry]['failure_cause'].append("Compartments do not have maximum security zone enabled")
                dictionary[entry]['findings'].append(msc)
                dictionary[entry]['mitigations'].append(f"If compartment: \"{msc['name']}\" contains a production workload, Enable Maximum Security Zone into it")

        return dictionary
