# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# SecurityList.py
# Description: Implementation of class SecurityList based on abstract



from common.utils.formatter.printer import debug, debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
from collections import defaultdict


class SecurityList(ReviewPoint):

    # Class Variables
    __identity = None
    __non_compliant_sec_list = []




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
        compartments.append(get_tenancy_data(self.__identity, self.config))

        self.__non_compliant_sec_list = parallel_executor(network_clients, compartments, self.__search_sec_lists, len(compartments), "__security_lists")

        return self.__non_compliant_sec_list


    def analyze_entity(self, entry):
    
        self.load_entity()    
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        if len(self.__non_compliant_sec_list) > 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append('Security List contains a wide open \"0.0.0.0/0\" CIDR in ingress rule that needs to be closed')
            for sec_list in self.__non_compliant_sec_list:
                if sec_list not in dictionary[entry]['findings']:
                    dictionary[entry]['findings'].append(sec_list)
                    dictionary[entry]['mitigations'].append('Make sure to reduce access and set more granular permissions into: '+sec_list['display_name'])
                                       
        return dictionary


    def __search_sec_lists(self, item):
        network_client = item[0]
        compartments = item[1:]

        sec_lists = []

        for compartment in compartments:
            sec_list_data = get_security_list_data(network_client, compartment.id)
            for sec_list in sec_list_data:
                sec_list_record = {
                    'compartment_id': sec_list.compartment_id,
                    'defined_tags': sec_list.defined_tags,
                    'display_name': sec_list.display_name,
                    'egress_security_rules': sec_list.egress_security_rules,
                    'id': sec_list.id,
                    'ingress_security_rules': sec_list.ingress_security_rules,
                    'lifecycle_state': sec_list.lifecycle_state,
                    'time_created': sec_list.time_created,
                    'vcn_id': sec_list.vcn_id,
                }
                    
                for ingress in sec_list_record['ingress_security_rules']:
                    if ingress.source == '0.0.0.0/0':
                        sec_lists.append(sec_list_record)
                    break
                else:
                    continue

        return sec_lists