# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract

from common.utils.helpers.helper import *
from common.utils.formatter.printer import debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
import oci


class SeparateCIDRBlocks(ReviewPoint):

    # Class Variables
    __vcns = []
    __groups_to_users = []
    __identity = None
    __tenancy = None
    __regions = None
    __network_clients = []



    def __init__(self, entry, area, sub_area, review_point, status, findings, config, signer):
        self.entry = entry
        self.area = area
        self.sub_area = sub_area
        self.review_point = review_point
        self.status = status
        self.findings = findings

        # From here on is the code is not implemented on abstract class
        self.config = config
        self.signer = signer
        self.__identity = get_identity_client(self.config, self.signer)
        self.__tenancy = get_tenancy_data(self.__identity, self.config)
        self.__regions = get_regions_data(self.__identity, self.config)

        for region in self.__regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            self.__network_clients.append(get_virtual_network_client(region_config, self.signer))
       
       
    def load_entity(self):
        # Gets all compartments including root compartment
        compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        debug_with_date(len(self.__network_clients))

        for network_client in self.__network_clients:
            debug_with_date(network_client)
            for compartment in compartments:
                vcns = get_vcn_data(network_client, compartment.id)
                debug_with_date(vcns)
                for vcn in vcns:
                    record = {
                        'cidr_blocks': vcn.cidr_blocks,
                        'compartment_id': vcn.compartment_id,
                        'default_dhcp_options_id': vcn.default_dhcp_options_id,
                        'default_route_table_id': vcn.default_route_table_id,
                        'default_security_list_id': vcn.default_security_list_id,
                        'defined_tags': vcn.defined_tags,
                        'display_name': vcn.display_name,
                        'dns_label': vcn.dns_label,
                        'freeform_tags': vcn.freeform_tags,
                        'id': vcn.id,
                        'ipv6_cidr_blocks': vcn.ipv6_cidr_blocks,
                        'lifecycle_state': vcn.lifecycle_state,
                        'time_created': vcn.time_created,
                        'vcn_domain_name': vcn.vcn_domain_name,
                    }

                    self.__vcns.append(record)

        return self.__vcns                

    def analyze_entity(self, entry):
        self.load_entity()

        for vcn in self.__vcns:
            debug_with_date(vcn['display_name'])

        debug_with_date(len(self.__vcns))



            # debug_with_date(vcn['display_name'])
        # dictionary = ReviewPoint.get_benchmark_dictionary(self)
        # for user in self.__users:
        #     if user['is_mfa_activated'] == False and user['lifecycle_state'] == 'ACTIVE':
        #         dictionary[entry]['status'] = False
        #         dictionary[entry]['findings'].append(user)          
        # return dictionary



        
        



    