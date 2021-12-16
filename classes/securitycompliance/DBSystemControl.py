# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# SecurityList.py
# Description: Implementation of class SecurityList based on abstract



from common.utils.formatter.printer import debug, debug_with_color_date, debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor



class DBSystemControl(ReviewPoint):

    # Class Variables
    __identity = None

    # __mysql_db_ocids = []
    
    # __odb_dbsystems_subnet_ocids = []
    # __mysql_dbsystems_subnet_ocids = []
    # __vcns = []

    __subnet_objects = []
    __subnets = []
    __oracle_database_objects = []
    __oracle_database_subnet_ocids = []
    __mysql_database_objects = []
    __mysql_database_ocids = []
    __mysql_database_subnet_ocids = []
    


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
        db_system_clients = []
        mysql_clients = []
        mysql_backup_clients = []
        network_clients = []
        placeholder_returner = []
        mysql_ocids = []

        for region in regions:
            region_config = self.config
            region_config['region'] = region.region_name
            db_system_clients.append((get_database_client(region_config, self.signer), region.region_name, region.region_key.lower()))
            mysql_clients.append((get_mysql_client(region_config, self.signer), region.region_name, region.region_key.lower()))
            network_clients.append(get_virtual_network_client(region_config, self.signer))

        tenancy = get_tenancy_data(self.__identity, self.config)

        # Get all compartments including root compartment
        compartments = get_compartments_data(self.__identity, tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        # Using a placeholder returner, which is a ephemeral variable that's discarded. Require this to avoid breaking the paralel
        # execution of threads. All values are stored on global private variables.
        # placeholder_returner = parallel_executor(network_clients, compartments, self.__search_vcns, len(compartments), "__vcns")
        # placeholder_returner = parallel_executor([x[0] for x in db_system_clients], compartments, self.__search_oracledb_dbs_subnet_ocids, len(compartments), "__odb_dbsystems")
        # placeholder_returner = parallel_executor([x[0] for x in mysql_clients], compartments, self.__search_mysql_dbs_ocids, len(compartments), "__mysql_dbsystems_ocids")
        # placeholder_returner = parallel_executor(mysql_clients, self.__mysql_db_ocids, self.__search_mysql_dbs_subnet_ocids, len(self.__mysql_db_ocids), "__mysql_subnets")

        

        self.__subnet_objects = ParallelExecutor.executor(network_clients, compartments, ParallelExecutor.get_subnets_in_compartments, len(compartments), ParallelExecutor.subnets)
        self.__oracle_database_objects = ParallelExecutor.executor([x[0] for x in db_system_clients], compartments, ParallelExecutor.get_oracle_dbsystem, len(compartments), ParallelExecutor.oracle_dbsystems)
        self.__mysql_database_objects = ParallelExecutor.executor([x[0] for x in mysql_clients], compartments, ParallelExecutor.get_mysql_dbsystem, len(compartments), ParallelExecutor.mysql_dbsystems)
        
        # Filling local array object for MySQL Database OCIDS
        for mysqldbobject in self.__mysql_database_objects: 
            #debug_with_color_date(mysqldbobject, "green")           
            mysql_db_record = {
                'compartment_id': mysqldbobject.compartment_id,
                'display_name': mysqldbobject.display_name,
                'id': mysqldbobject.id,
            }
            self.__mysql_database_ocids.append(mysql_db_record)

        self.__mysql_full_objects = ParallelExecutor.executor([x[0] for x in mysql_clients], self.__mysql_database_ocids, ParallelExecutor.get_mysql_dbsystem_full_info, len(self.__mysql_database_ocids), ParallelExecutor.mysql_full_data)

        for mysql in self.__mysql_full_objects:
            debug_with_color_date(mysql, "yellow")
        
        # Filling local array object for Oracle Database Subnet OCIDs
        for dbobject in self.__oracle_database_objects:
            orcl_db_record = {
                'compartment_id': dbobject.compartment_id,
                'subnet_id': dbobject.subnet_id,
                'display_name': dbobject.display_name,
            }
            self.__oracle_database_subnet_ocids.append(orcl_db_record)


        # Filling local array for Subnet OCIDS and it's corresponding private flag
        for subnet in self.__subnet_objects:
            subnet_record = {
                'cidr_block': subnet.cidr_block,
                'compartment_id': subnet.compartment_id,
                'display_name': subnet.display_name,
                'dns_label': subnet.dns_label,
                'id': subnet.id,
                'lifecycle_state': subnet.lifecycle_state,
                'time_created': subnet.time_created,
                'vcn_id': subnet.vcn_id,
                'prohibit_internet_ingress': subnet.prohibit_internet_ingress,
                'prohibit_public_ip_on_vnic': subnet.prohibit_public_ip_on_vnic,
            }
            self.__subnets.append(subnet_record)



        

        #debug_with_color_date(self.__vcns[0], "cyan")
        #debug_with_color_date(self.__odb_dbsystems_subnet_ocids, "yellow")
        #debug_with_color_date(self.__mysql_dbsystems_subnet_ocids, "cyan")
     


    def analyze_entity(self, entry):
    
        self.load_entity()    
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        
                                       
        return dictionary

    

    def __search_mysql_dbs_ocids(self, item):
        mysql_client = item[0]
        compartments = item[1:]       
 
        # This subroutinte adds for each valid MySQL Database, it's OCID into a list. 
        # Value is stored in a global variable given multi-threading corruption
        for compartment in compartments:            
            dbdata = get_db_system_data(mysql_client, compartment.id)
            if (len(dbdata) > 0):
                for db in dbdata:           
                  if db.lifecycle_state == "ACTIVE":
                      self.__mysql_db_ocids.append(db.id)                         
        
        return self.__mysql_db_ocids

    def __search_mysql_dbs_subnet_ocids(self, item):
        mysql_client = item[0]
        mysql_ocids = item[1:]

        # Using recommendation listed here: https://github.com/oracle/oci-python-sdk/issues/408#issuecomment-994956936
        for db_ocid in mysql_ocids:
            region = db_ocid['id'].split('.')[3]
            if mysql_client[1] in region or mysql_client[2] in region:
                mysqldbdata = get_mysql_dbsystem_data(mysql_client[0], db_ocid)
                for dbdata in mysqldbdata:
                    record = {
                        'display_name': dbdata.display_name,
                        'subnet_id': dbdata.subnet_id,
                    }
                    self.__mysql_dbsystems_subnet_ocids.append(record)

        return self.__mysql_dbsystems_subnet_ocids



    def __search_vcns(self, item):
        network_client = item[0]
        compartments = item[1:]


        vcns = []

        for compartment in compartments:
            vcn_data = get_vcn_data(network_client, compartment.id)
            for vcn in vcn_data:
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