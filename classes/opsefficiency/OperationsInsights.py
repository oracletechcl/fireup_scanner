# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# OperationsInsights.py
# Description: Implementation of class OperationsInsights based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
import common.utils.helpers.ParallelExecutor as ParallelExecutor
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class OperationsInsights(ReviewPoint):

    # Class Variables
    __compartments = []
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
        self.__tenancy = get_tenancy_data(self.__identity, self.config)


    def load_entity(self):

        regions = get_regions_data(self.__identity, self.config)

        operations_insights_clients = []

        # for region in regions:
        #     region_config = self.config
        #     region_config['region'] = region.region_name
        #     operations_insights_clients.append(get_operations_insights_client(region_config, self.signer))
            
        region_config = self.config
        region_config['region'] = 'us-ashburn-1'
        operations_insights_clients.append(get_operations_insights_client(region_config, self.signer))
        region_config['region'] = 'uk-london-1'
        operations_insights_clients.append(get_operations_insights_client(region_config, self.signer))


        # Get all compartments including root compartment
        self.__compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        self.__compartments.append(get_tenancy_data(self.__identity, self.config))

        warehouse = operations_insights_clients[0].list_operations_insights_warehouses(compartment_id=self.__tenancy.id).data

        debug(warehouse, "yellow")

        if len(warehouse.items) > 0:
            debug(warehouse.items[0].id, "red")
            hub = operations_insights_clients[0].list_awr_hubs(operations_insights_warehouse_id=warehouse.items[0].id, compartment_id=self.__tenancy.id).data
            debug(hub, "cyan")

        return 


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)


        return dictionary
