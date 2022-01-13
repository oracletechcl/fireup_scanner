# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# NetworkSources.py
# Description: Implementation of class NetworkSources based on abstract



from common.utils.formatter.printer import debug, debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *
import common.utils.helpers.ParallelExecutor as ParallelExecutor


class NetworkSources(ReviewPoint):

    # Class Variables
    __identity = None
    __tenancy = None
    __network_sources = []
    __policy_statements = set()
    __identity_client = None
    __authentication_policy = None

     
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
        self.__identity_client = get_identity_client(self.config,self.signer)
        network_sources = get_network_sources(self.__identity_client,self.__tenancy.id)
       
        for n_source in network_sources:
            record = {
                "compartment_id": n_source.compartment_id,
                "defined_tags": n_source.defined_tags,
                "description": n_source.description,
                "freeform_tags": n_source.freeform_tags,
                "id": n_source.id,
                "name": n_source.name,
                "public_source_list": n_source.public_source_list,
                "services": n_source.services,
                "time_created": n_source.time_created,
                "virtual_source_list": n_source.virtual_source_list
            }
            self.__network_sources.append(record)

        self.__authentication_policy = get_authentication_policy(self.__identity_client, self.__tenancy.id)

        compartments = get_compartments_data(self.__identity, self.__tenancy.id)
        compartments.append(get_tenancy_data(self.__identity, self.config))

        policy_data = ParallelExecutor.executor([self.__identity_client], compartments, ParallelExecutor.get_policies_per_compartment, len(compartments), ParallelExecutor.policies)

        for record in policy_data:
            for policy in record:
                for statement in policy.statements:
                    self.__policy_statements.add(statement)

    def analyze_entity(self, entry):
    
        self.load_entity()     
        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        if self.__network_sources:
            # check if created network sources are in use                   
            for n_source in self.__network_sources:
                present = False
                for statement in self.__policy_statements:              
                    if f"request.networkSource.name='{n_source['name']}'" in statement:
                        present = True
                        break
                if not present:
                    dictionary[entry]['status'] = False
                    dictionary[entry]['findings'].append(n_source)
                    dictionary[entry]['failure_cause'].append(f'Network source is created but currently not in use')   
                    dictionary[entry]['mitigations'].append(f'Network source named : "{n_source["name"]}" is available but is not currently in use. '
                                                            'Make sure to attach it to a policy.')   
                
        else:
            dictionary[entry]['status'] = False
            dictionary[entry]['failure_cause'].append('Network sources are not created')   
            dictionary[entry]['mitigations'].append('Create network sources to restrict access to resources. '
                                                    'Then specify the network source in an IAM policy to control access based on the originating IP address.')   

        # Check network source restrictions for signing in to the OCI Console
        if not self.__authentication_policy.network_policy.network_source_ids:
                dictionary[entry]['status'] = False
                dictionary[entry]['failure_cause'].append(f'Users can sign-in to the OCI Console from any IP')   
                dictionary[entry]['mitigations'].append(f'Specify the network source in your tenancy\'s authentication settings to restrict sign in to the OCI Console.')   

        return dictionary

