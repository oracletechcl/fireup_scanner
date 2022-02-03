# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# TransitRouting.py
# Description: Implementation of class TransitRouting based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class TransitRouting(ReviewPoint):

    # Class Variables
    __identity = None
    __tenancy = None
    __compartments = None
    __regions = None
    __ip_sec_connections_objects = None
    __cross_connections_objects = None
    __topologies_with_cpe_connections_objects = []
    __topologies_with_cpe_connections = []

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

        # From here on the code is not implemented on abstract class
        self.config = config
        self.signer = signer
        self.__identity = get_identity_client(self.config, self.signer)
        self.__tenancy = get_tenancy_data(self.__identity, self.config)



    def load_entity(self):

        network_cleints = []
        vpn_fc_connections_per_compartment = set()

        self.__regions = get_regions_data(self.__identity, self.config)
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        for region in self.__regions:
            
            region_config = self.config
            region_config['region'] = region.region_name     
            network_cleints.append(get_virtual_network_client(region_config, self.signer))

        self.__ip_sec_connections_objects = ParallelExecutor.executor(network_cleints, self.__compartments, ParallelExecutor.get_ip_sec_connections, len(self.__compartments), ParallelExecutor.ip_sec_connections)
        self.__cross_connections_objects = ParallelExecutor.executor(network_cleints, self.__compartments, ParallelExecutor.get_cross_connects, len(self.__compartments), ParallelExecutor.cross_connects)
        
        # find compartment and region with VPN or FastConnect vpn_connections
        for vpn_connections in self.__ip_sec_connections_objects:
            region = vpn_connections[0].id.split('.')[3]
            vpn_fc_connections_per_compartment.add((vpn_connections[0].compartment_id, region))

        for fc_connections in self.__cross_connections_objects:
            region = fc_connections.id.split('.')[3]
            vpn_fc_connections_per_compartment.add((fc_connections[0].compartment_id, region))

        # gather network data with workaround and only from compartments which have CPE connectiity
        for com_region in vpn_fc_connections_per_compartment:
            region_needed = None
            for region in self.__regions:
                if com_region[1] == region.region_key.lower() or com_region[1] == region.region_name.lower() :
                    region_needed = self.config
                    region_needed['region'] = region.region_name

                    n_client = get_virtual_network_client(region_needed, self.signer)
                    n_client.base_client.endpoint = 'https://vnca-api.' + region.region_name + '.oci.oraclecloud.com'
                    self.__topologies_with_cpe_connections_objects.append(get_networking_topology_per_compartment(n_client,com_region[0]))

        for network_topology in self.__topologies_with_cpe_connections_objects:
            record = {
                    "entities": network_topology.entities,
                    "time_created": network_topology.time_created,
                    "relationships": network_topology.relationships,
                    "type": network_topology.type
                     }
            self.__topologies_with_cpe_connections.append(record)
    
    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for network in self.__topologies_with_cpe_connections:

            vpn_connections = []
            virtual_circuts = []
            drg_attachments = []
            vcns = []
            lpgs = []
            drgs = []

            for entity in network['entities']:
                resource = entity['id'].split('.')[1]

                if resource == 'ipsecconnection':
                    vpn_connections.append(resource)
                elif resource == 'localpeeringgateway':
                    lpgs.append(resource)
                elif resource == 'vcn':
                    vcns.append(resource)
                elif resource == 'drgattachment':
                    drg_attachments.append(resource)
                elif resource == 'drg':
                    drgs.append(resource)
                elif resource == 'virtualcircut':
                    virtual_circuts.append(resource)
                       
            # Check number of DRGs
            if len(drgs) == 1:
                # Check if number of drg attachmenets correspond to HUB-and-Spoke pattern
                # This is legacy network if 1 attachment for hub-vcn + number of VPN tunnels(2 per VPN connection) + 1 attachment per virutal circut
                if len(drg_attachments) == 1 + 2*len(vpn_connections) + len(virtual_circuts):
                    # I will ignore case if there is one VCN because maybe application is simple and do not need extended networking pattern.
                    if len(vcns) > 1:
                        # Check if there are LPGs in place for connectivity
                        # There should be 2*(vcn-1) LPGS
                        if len(lpgs) != 2*(len(vcns)-1):
                            dictionary[entry]['status'] = False
                            dictionary[entry]['findings'].append(network)
                            dictionary[entry]['failure_cause'].append('HUB-and-Spoke pattern is not implemented')   
                            dictionary[entry]['mitigations'].append('Network pattern is not optimal in Compartment: '  + get_compartment_name(self.__compartments, network['entities'][0]['compartmentId']) + ' Consider implementing HUB-and-Spoke network topology') 
                else:
                    # This can be a new system with one DRG 
                    # Check if number of attachments equals number of vcns + 2 attachments per vpn + 1 attachment for virtual circut
                    if len(drg_attachments) != len(vcns) + 2*len(vpn_connections) + len(virtual_circuts):
                        dictionary[entry]['status'] = False
                        dictionary[entry]['findings'].append(network)
                        dictionary[entry]['failure_cause'].append('HUB-and-Spoke pattern is not implemented')   
                        dictionary[entry]['mitigations'].append('Network pattern is not optimal in Compartment: '  + get_compartment_name(self.__compartments, network['entities'][0]['compartmentId']) + ' Consider implementing HUB-and-Spoke netowrk topology')
            else:
                dictionary[entry]['status'] = False
                dictionary[entry]['findings'].append(network)
                dictionary[entry]['failure_cause'].append('HUB-and-Spoke pattern is not implemented')   
                dictionary[entry]['mitigations'].append('Network pattern is not optimal in Compartment: '  + get_compartment_name(self.__compartments, network['entities'][0]['compartmentId']) + ' Consider implementing HUB-and-Spoke network topology')

        return dictionary
