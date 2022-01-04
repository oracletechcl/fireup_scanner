# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# SecureFileStorage.py
# Description: Implementation of class SecureFileStorage based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
# from oci.file_storage.models import MountTarget
from oci.exceptions import ServiceError


class SecureFileStorage(ReviewPoint):
    # Class Variables
    __file_system_objects = []
    __identity = None
    __sec_list_objects = []
    __non_compliant_sec_list = []

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
        # file_system_clients_with_ADs = []

        tenancy = get_tenancy_data(self.__identity, self.config)

        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            # Create a network client for each region
            network_clients.append(get_virtual_network_client(region_config, self.signer))
            file_storage_clients.append(
                (get_file_storage_client(region_config, self.signer), region.region_name, region.region_key.lower()))
            identity_clients.append(get_identity_client(region_config, self.signer))

        file_system_clients_with_ADs = []
        availability_domains = ParallelExecutor.get_availability_domains(identity_clients, tenancy.id)

        for file_storage_client in file_storage_clients:
            for availability_domain in availability_domains:
                if file_storage_client[1][:-2] in availability_domain.lower() or file_storage_client[2] in availability_domain.lower():
                    file_system_clients_with_ADs.append((file_storage_client[0], availability_domain))

        mount_targets_info_objects = ParallelExecutor.executor(file_system_clients_with_ADs, compartments,
                                                               ParallelExecutor.get_mounts, len(compartments),
                                                               ParallelExecutor.mount_targets)

        # print(mount_targets_info_objects)

        export_set_ids = []
        subnet_ids = []
        compartment_ids = []
        subnet_infos = []
        security_list_ids = []
        security_lists = []
        export_lists = []
        for mount_target in mount_targets_info_objects:
            export_set_id = mount_target.export_set_id
            export_set_ids.append(export_set_id)
            subnet_id = mount_target.subnet_id
            subnet_ids.append(subnet_id)
            compartment_ids.append(mount_target.compartment_id)

        for subnet in subnet_ids:
            for network_client in network_clients:
                try:
                    subnet_info = network_client.get_subnet(subnet_id=subnet)
                    subnet_infos.append(subnet_info.data)
                    security_list_ids.append(subnet_info.data.security_list_ids)
                except ServiceError as e:
                    pass

        for security_list in security_list_ids:
            for network_client in network_clients:
                try:
                    security_list_info = network_client.get_security_list(security_list_id=security_list)
                    security_lists.append(security_list_info.data)
                except ServiceError as e:
                    pass

        for export_set_id in export_set_ids:
            for file_storage_client in file_storage_clients:
                try:
                    export_info = file_storage_client[0].list_exports(export_set_id=export_set_id)
                    if len(export_info.data) != 0:
                        export_details = file_storage_client[0].get_export(export_id=export_info.data[0].id)
                        # print(export_details.data)
                        export_lists.append(export_details.data)
                except ServiceError as e:
                    pass

        # print(security_lists)
        tcp_ports_list = [111, 2048, 2049, 2050]
        for sec_list in security_lists:
            for ingress in sec_list.ingress_security_rules:
                if ingress.tcp_options is None:
                    sec_list_record = {
                        'compartment_id': sec_list.compartment_id,
                        'display_name': sec_list.display_name,
                        'id': sec_list.id,
                        'ingress_tcp_options': ingress.tcp_options,
                        'ingress_udp_options': ingress.udp_options,
                    }
                    self.__non_compliant_sec_list.append(sec_list_record)
                elif ingress.tcp_options.destination_port_range is None:
                    sec_list_record = {
                        'compartment_id': sec_list.compartment_id,
                        'display_name': sec_list.display_name,
                        'id': sec_list.id,
                        'ingress_tcp_options': ingress.tcp_options,
                        'ingress_udp_options': ingress.udp_options,
                    }
                    self.__non_compliant_sec_list.append(sec_list_record)

                elif ingress.tcp_options.destination_port_range.max not in tcp_ports_list:
                    sec_list_record = {
                        'compartment_id': sec_list.compartment_id,
                        'display_name': sec_list.display_name,
                        'id': sec_list.id,
                        'ingress_tcp_options': ingress.tcp_options,
                        'ingress_udp_options': ingress.udp_options,
                    }
                    # print(sec_list_record)
                    self.__non_compliant_sec_list.append(sec_list_record)

        # print(self.__non_compliant_sec_list)
        # print(len(self.__non_compliant_sec_list))
        # print(security_lists)
        # print(len(security_lists))
        # print(export_lists)
        # print(len(export_lists))
        return security_lists, export_lists

    def analyze_entity(self, entry):

        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        if len(self.__non_compliant_sec_list) > 0:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append(
                'Stateful ingress from ALL ports in source CIDR block does not go to TCP ports 111, 2048, 2049, and 2050.')
            for sec_list in self.__non_compliant_sec_list:
                if sec_list not in dictionary[entry]['findings']:
                    dictionary[entry]['findings'].append(sec_list)
                    dictionary[entry]['mitigations'].append(
                        'Make sure to reduce access and set more granular permissions into: ' + sec_list[
                            'display_name'])
        return dictionary
