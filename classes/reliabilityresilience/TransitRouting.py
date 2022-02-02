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
    __networking_topology_objects = None
    __ip_sec_connections_objects = None
    __compartments = None
    __virutal_circuits_objects = None
    __cross_connections_objects = None
    __regions = None
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

        network_clients = []
        ip_sec_clients = []
        self.__regions = get_regions_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        for region in self.__regions:
            
            region_config = self.config
            region_config['region'] = region.region_name
            
        
            ip_sec_clients.append(get_virtual_network_client(region_config, self.signer))

        # self.__networking_topology_objects = ParallelExecutor.executor(network_clients, self.__compartments, ParallelExecutor.get_networking_topology_1, len(self.__compartments), ParallelExecutor.networking_topology)     
        self.__ip_sec_connections_objects = ParallelExecutor.executor(ip_sec_clients, self.__compartments, ParallelExecutor.get_ip_sec_connections, len(self.__compartments), ParallelExecutor.ip_sec_connections)
        # virtual circuts wychodzi 0 at this moment.
        # self.__virutal_circuits_objects = ParallelExecutor.executor(ip_sec_clients, self.__compartments, ParallelExecutor.get_virtual_circuits, len(self.__compartments), ParallelExecutor.virtual_circuits)
        self.__cross_connections_objects = ParallelExecutor.executor(ip_sec_clients, self.__compartments, ParallelExecutor.get_cross_connects, len(self.__compartments), ParallelExecutor.cross_connects)
      
    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)


        vpn_fc_connections_per_compartment = set()
        # find com/reg with connections
        for vpn_connections in self.__ip_sec_connections_objects:
            region = vpn_connections[0].id.split('.')[3]
            vpn_fc_connections_per_compartment.add((vpn_connections[0].compartment_id, region))

        for fc_connections in self.__cross_connections_objects:
            region = fc_connections.id.split('.')[3]
            vpn_fc_connections_per_compartment.add((fc_connections[0].compartment_id, region))
    
        topologies_with_connections = []

        for com_region in vpn_fc_connections_per_compartment:
            region_needed = None
            for region in self.__regions:
                if com_region[1] == region.region_key.lower() or com_region[1] == region.region_name.lower() :
                    region_needed = self.config
                    region_needed['region'] = region.region_name
                    n_client = get_virtual_network_client(region_needed, self.signer)
                    n_client.base_client.endpoint = 'https://vnca-api.' + region.region_name + '.oci.oraclecloud.com'
                    topologies_with_connections.append(get_networking_topology_per_compartment(n_client,com_region[0]))
    
        # Gather all needed data from a topology
        for topology in topologies_with_connections:
            debug('££££££££££££££££££££££££££££££££ TOPOLOGY £££££££££££££££££££££££££££')
            connections = []
            drg_attachments = []
            vcns = []
            lpgs = []
            drgs = []
            virtual_circuts = []

            for entity in topology.entities:

                resource = entity['id'].split('.')[1]
                if resource == 'ipsecconnection':
                    connections.append(resource)
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
                

            debug(f'number of connections: {len(connections)}', color ='blue')
            debug(f'number of drg attachments: {len(drg_attachments)}', color ='blue')
            debug(f'number of vcns: {len(vcns)}', color ='blue')
            debug(f'number of lpgs: {len(lpgs)}', color ='blue')
            debug(f'number of drgs: {len(drgs)}', color ='blue')
            debug(f'number of virtual circuts: {len(virtual_circuts)}', color ='blue')
            
            # Check how many drgs is there
            if len(drgs) == 1:
                # check how many drg attachements
                # This is legacy topology if 1 attachment for hub-vcn, number of tunnels(2 per connection) + 1 per virutal circut
                if len(drg_attachments) == 1 + 2*len(connections) + len(virtual_circuts):
                    # If there is just one VCN then maybe this is enough for the application to work there is no hub and spoke in place but maybe it is not needed
                    if len(vcns) > 1:
                        # Check if there are LPGS in place for connectivity
                        # There should be 2*(vcn-1) LPGS
                        if len(lpgs) == 2*(len(vcns)-1):
                            debug('Looks like numbers are right for legacy topology, maybe worth to check HOW lpgs are connected just to be sure',color = 'yellow')
                        else:
                            debug('not enough lpgs, or too many lpgs in comparison to vcns',color = 'red')
                    else:
                        debug('Hub and spoke not in place, check if it is really needed.',color = 'red')
                else:
                    # This can be a new system with one drg and many attachments
                    # Check if number of vcns equals number of attachements + 2 attachements per vpn + 1 for fastconnect
                    if len(drg_attachments) == len(vcns) + 2*len(connections) + len(virtual_circuts):
                        debug('the topology for hub and spoke is in place',color = 'yellow')
                    else:
                        debug('There are too many or too little attachments to the drg, the hub and spoke pattern is not in place',color = 'red')
            else:
                debug('More drgs than required. consider hub and spoke topology',color = 'red')

        return dictionary
