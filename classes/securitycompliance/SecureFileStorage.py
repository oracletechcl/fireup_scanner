# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# SecureFileStorage.py
# Description: Implementation of class SecureFileStorage based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from oci.exceptions import ServiceError


class SecureFileStorage(ReviewPoint):
    # Class Variables
    __identity = None
    __non_compliant_sec_list = []
    __non_compliant_export_list = []
    __mount_targets_info_objects = []
    __non_compliant_open_sec_list = []
    __security_lists_from_mount_targets = []
    __export_options = []
    __compartments = []


    def __init__(self,
                 entry: str,
                 area: str,
                 sub_area: str,
                 review_point: str,
                 status: bool,
                 failure_cause: list,
                 findings: list,
                 mitigations: list,
                 fireup_mapping: list,
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
        file_storage_clients = []
        identity_clients = []
        file_system_clients_with_ADs = []

        tenancy = get_tenancy_data(self.__identity, self.config)

        self.__compartments = get_compartments_data(self.__identity, tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            network_clients.append((get_virtual_network_client(region_config, self.signer), region.region_name,region.region_key.lower()))
            file_storage_clients.append(
                (get_file_storage_client(region_config, self.signer), region.region_name, region.region_key.lower()))
            identity_clients.append(get_identity_client(region_config, self.signer))

        availability_domains = ParallelExecutor.get_availability_domains(identity_clients, tenancy.id)

        for file_storage_client in file_storage_clients:
            for availability_domain in availability_domains:
                if file_storage_client[1][:-2] in availability_domain.lower() or file_storage_client[2] in availability_domain.lower():
                    file_system_clients_with_ADs.append((file_storage_client[0], availability_domain))

        self.__mount_targets_info_objects = ParallelExecutor.executor(file_system_clients_with_ADs, self.__compartments,ParallelExecutor.get_mounts, len(self.__compartments),ParallelExecutor.mount_targets)
        self.__security_lists_from_mount_targets = ParallelExecutor.executor(network_clients, self.__mount_targets_info_objects, ParallelExecutor.get_security_lists_from_mounts, len(self.__mount_targets_info_objects), ParallelExecutor.security_lists_from_mount_targets)
        self.__export_options = ParallelExecutor.executor(file_storage_clients, self.__mount_targets_info_objects, ParallelExecutor.get_export_options, len(self.__mount_targets_info_objects), ParallelExecutor.export_options)

        tcp_ports_list = [111, 2048, 2049, 2050]
        upd_ports_list = [111, 2048]

        for sec_list in self.__security_lists_from_mount_targets:
            tcp_ports = []
            udp_ports = []
            for ingress in sec_list.ingress_security_rules:
                if ingress.protocol == '6' and ingress.source == '0.0.0.0/0' and ingress.tcp_options is None:
                    open_sec_list_record = {
                        'compartment_id': sec_list.compartment_id,
                        'display_name': sec_list.display_name,
                        'vcn_id': sec_list.vcn_id,
                        'id': sec_list.id,
                        'ingress_tcp_options': ingress.tcp_options,
                        'ingress_udp_options': ingress.udp_options,
                    }
                    self.__non_compliant_open_sec_list.append(open_sec_list_record)
                if ingress.protocol == '17' and ingress.source == '0.0.0.0/0' and ingress.udp_options is None:
                    open_sec_list_record = {
                        'compartment_id': sec_list.compartment_id,
                        'display_name': sec_list.display_name,
                        'vcn_id': sec_list.vcn_id,
                        'id': sec_list.id,
                        'ingress_tcp_options': ingress.tcp_options,
                        'ingress_udp_options': ingress.udp_options,
                    }
                    self.__non_compliant_open_sec_list.append(open_sec_list_record)

            for ingress in sec_list.ingress_security_rules:
                if ingress.tcp_options is not None:
                    if ingress.tcp_options.destination_port_range is not None:
                        min = ingress.tcp_options.destination_port_range.min
                        max = ingress.tcp_options.destination_port_range.max
                        if min == max:
                            tcp_ports.append(ingress.tcp_options.destination_port_range.max)
                        else:
                            for i in range(min,max + 1):
                                tcp_ports.append(i)
                if ingress.udp_options is not None:
                    if ingress.udp_options.destination_port_range is not None:
                        min = ingress.udp_options.destination_port_range.min
                        max = ingress.udp_options.destination_port_range.max
                        if min == max:
                            udp_ports.append(ingress.udp_options.destination_port_range.max)
                        else:
                            for i in range(min,max + 1):
                                udp_ports.append(i)
            if tcp_ports not in tcp_ports_list or udp_ports not in upd_ports_list:
                sec_list_record = {
                        'compartment_id': sec_list.compartment_id,
                        'display_name': sec_list.display_name,
                        'vcn_id': sec_list.vcn_id,
                        'id': sec_list.id,
                        'ingress_tcp_options': ingress.tcp_options,
                        'ingress_udp_options': ingress.udp_options,
                }
                self.__non_compliant_sec_list.append(sec_list_record)

        for export_details in self.__export_options:
            if export_details.export_options[0].identity_squash == 'NONE' or export_details.export_options[0].identity_squash == 'ROOT':
                for file_storage_client in file_storage_clients:
                    region = export_details.file_system_id.split('.')[3]
                    if file_storage_client[1] in region or file_storage_client[1].replace('-', '_') in region or file_storage_client[2] in region:
                        file_name = file_storage_client[0].get_file_system(file_system_id = export_details.file_system_id).data
                        export_list_record = {
                            'compartment_id': file_name.compartment_id,
                            'export_set_id': export_details.export_set_id,
                            'file_system_id': export_details.file_system_id,
                            'id': export_details.id,
                            'path': export_details.path,
                            'identity_squash': export_details.export_options[0].identity_squash,
                        }
                        self.__non_compliant_export_list.append(export_list_record)
        return self.__non_compliant_sec_list, self.__non_compliant_export_list, self.__non_compliant_open_sec_list

    def analyze_entity(self, entry):

        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        if len(self.__non_compliant_sec_list) > 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append(
                'Stateful ingress from ALL ports in source CIDR block does not go to TCP ports 111, 2048, 2049, '
                'and 2050 or Stateful ingress from ALL ports in source CIDR block does not go to UDP ports 111 or '
                '2048')
            for sec_list in self.__non_compliant_sec_list:
                if sec_list not in dictionary[entry]['findings']:
                    dictionary[entry]['findings'].append(sec_list)
                    dictionary[entry]['mitigations'].append(
                        'Make sure to alter destination port range to the required ports: ' + sec_list[
                            'display_name'] + ('Compartment name: ' + str(get_compartment_name(self.__compartments,sec_list['compartment_id']))))

        if len(self.__non_compliant_export_list) > 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append(
                'NFS all_squash option does not map all the users to ALL')
            for export in self.__non_compliant_export_list:
                if export not in dictionary[entry]['findings']:
                    dictionary[entry]['findings'].append(export)
                    dictionary[entry]['mitigations'].append(
                        'Make sure to set squash options to ALL: ' + (str(export['path'])) + ' ' + ('Compartment name: ' + str(get_compartment_name(self.__compartments,export['compartment_id']))))

        if len(self.__non_compliant_open_sec_list) > 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append(
                'An all in rule is in place where destination ports are open')
            for source in self.__non_compliant_open_sec_list:
                if source not in dictionary[entry]['findings']:
                    dictionary[entry]['findings'].append(source)
                    dictionary[entry]['mitigations'].append(
                        'Consider closing this to a micro-segmented CIDR Block: ' + source[
                            'display_name'] + ('Compartment name: ' + str(get_compartment_name(self.__compartments,source['compartment_id']))))

        return dictionary
