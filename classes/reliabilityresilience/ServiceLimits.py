# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ServiceLimits.py
# Description: Implementation of class ServiceLimits based on abstract

from common.utils.helpers.helper import *
from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *


class ServiceLimits(ReviewPoint):

    # Class Variables
    __limit_value_objects = []
    __limit_value_dicts = []
    __non_compliant_limits = dict()
    __identity = None


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

        tenancy = get_tenancy_data(self.__identity, self.config)

        limits_clients = []
        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            limits_clients.append( (get_limits_client(region_config, self.signer), tenancy.id, region.region_name) )

        services = limits_clients[0][0].list_services(tenancy.id).data

        self.__limit_value_objects = ParallelExecutor.executor(limits_clients, services, ParallelExecutor.get_limit_values, len(services), ParallelExecutor.limit_values_with_regions)

        required_services = ['block-storage', 'container-engine', 'database', 'load-balancer', 'mysql']

        for limit in self.__limit_value_objects:
            if limit[1] in required_services:
                record = {
                    "region": limit[0],
                    "availability_domain": limit[2].availability_domain,
                    "name": limit[2].name,
                    "service_name": limit[1],
                    "scope_type": limit[2].scope_type,
                    "value": limit[2].value,
                }
                self.__limit_value_dicts.append(record)

        return self.__limit_value_dicts


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        for limit in self.__limit_value_dicts:
            try:
                expected_value = service_limits[limit['name']]
                if limit['value'] != expected_value:
                    dictionary[entry]['findings'].append(limit)
                    location = limit['region']
                    if "AD" in limit['scope_type']:
                        location = limit['availability_domain'][5:]
                    if (limit['name'], expected_value) in self.__non_compliant_limits:
                        for i, value in enumerate(self.__non_compliant_limits[(limit['name'], expected_value)]):
                            if location[:-1] in value:
                                self.__non_compliant_limits[(limit['name'], expected_value)][i] = f"{value}/{location[-1]}"
                                break
                        else:
                            self.__non_compliant_limits[(limit['name'], expected_value)].append(location)
                    else:
                        self.__non_compliant_limits[(limit['name'], expected_value)] = [location]
            except KeyError:
                new_limit = f"New limit found that's not in dictionary: \"{limit['name']}\""
                if new_limit not in dictionary[entry]['mitigations']:
                    dictionary[entry]['mitigations'].append(new_limit)

        for key, value in self.__non_compliant_limits.items():
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append('Limits should be correctly configured to what is required for the workload.')
            dictionary[entry]['mitigations'].append(f"Limit name: \"{key[0]}\", is different to expected default of: \"{key[1]}\" in: {value}")

        return dictionary


service_limits = {
    "lb-100mbps-count": 300,
    "lb-10mbps-count": 300,
    "lb-10mbps-micro-count": 10,
    "lb-400mbps-count": 10,
    "lb-8000mbps-count": 10,
    "lb-flexible-bandwidth-sum": 5000,
    "lb-flexible-count": 50,

    "backup-count": 100000,
    "free-backup-count": 10,
    "total-free-storage-gb-regional": 10,

    "total-free-storage-gb": 200,
    "total-storage-gb": 400000,
    "volume-count": 100000,
    "volumes-per-group": 32,

    "mysql-manual-backup-count": 1200,

    "mysql-analytics-bm-standard-e2-64-count": 0,
    "mysql-analytics-vm-standard-e3-count": 0,
    "mysql-bm-standard-e2-64-count": 0,
    "mysql-database-for-analytics-vm-standard-e3-count": 0,
    "mysql-database-for-heatwave-bm-standard-e3-count": 2,
    "mysql-database-for-heatwave-vm-standard-e3-count": 20,
    "mysql-heatwave-vm-standard-e3-count": 100,
    "mysql-total-storage-gb": 100000,
    "mysql-vm-standard-e2-1-count": 5,
    "mysql-vm-standard-e2-2-count": 5,
    "mysql-vm-standard-e2-4-count": 5,
    "mysql-vm-standard-e2-8-count": 5,
    "mysql-vm-standard-e3-1-16gb-count": 100,
    "mysql-vm-standard-e3-1-8gb-count": 100,
    "mysql-vm-standard-e3-16-256gb-count": 100,
    "mysql-vm-standard-e3-2-32gb-count": 100,
    "mysql-vm-standard-e3-24-384gb-count": 100,
    "mysql-vm-standard-e3-32-512gb-count": 100,
    "mysql-vm-standard-e3-4-64gb-count": 100,
    "mysql-vm-standard-e3-48-768gb-count": 100,
    "mysql-vm-standard-e3-64-1024gb-count": 100,
    "mysql-vm-standard-e3-8-128gb-count": 100,

    "adb-free-count": 1,
    "adw-ocpu-count": 160,
    "adw-total-storage-tb": 130,
    "ajd-ocpu-count": 8,
    "ajd-total-storage-tb": 8,
    "apex-ocpu-count": 128,
    "apex-total-storage-tb": 128,
    "atp-ocpu-count": 135,
    "atp-total-storage-tb": 130,
    "ex-cdb-count": 20000,
    "ex-non-cdb-count": 20000,
    "ex-pdb-count": 20000,

    "adw-dedicated-ocpu-count": 0,
    "adw-dedicated-total-storage-tb": 0,
    "atp-dedicated-ocpu-count": 0,
    "atp-dedicated-total-storage-tb": 0,
    "bm-dense-io1-36-count": 0,
    "bm-dense-io2-52-count": 50,
    "exadata-base-48-count": 0,
    "exadata-database-server-x8m-count": 0,
    "exadata-full1-336-x6-count": 0,
    "exadata-full2-368-x7-count": 0,
    "exadata-full3-400-x8-count": 0,
    "exadata-half1-168-x6-count": 0,
    "exadata-half2-184-x7-count": 0,
    "exadata-half3-200-x8-count": 0,
    "exadata-quarter1-84-x6-count": 0,
    "exadata-quarter2-92-x7-count": 0,
    "exadata-quarter3-100-x8-count": 0,
    "exadata-storage-server-x8m-count": 0,
    "vm-block-storage-gb": 150000,
    "vm-standard1-ocpu-count": 0,
    "vm-standard2-ocpu-count": 300,

    "cluster-count": 15,
    "node-count": 1000,
}
