# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ReviewPoint.py
# Description: Abstract Class for Review Point for later inheritance and customization


from __future__ import print_function
from common.utils.formatter.printer import *
from abc import ABC, abstractmethod
import oci



class ReviewPoint(ABC):
    def __init__(self, entry:str, section:str, recommendation: str, tittle:str, status:bool, level:str, findings:list, config, signer, proxy, report_directory):        
        self.entry = entry
        self.section = section
        self.recommendation = recommendation
        self.tittle = tittle
        self.status = status
        self.level = level
        self.findings = findings
        self.config = config
        self.signer = signer
        self.proxy = proxy
        self.report_directory = report_directory

        try:
            self.__identity = oci.identity.IdentityClient(
                self.__config, signer=self.__signer)
            if proxy:
                self.__identity.base_client.session.proxies = {'https': proxy}           
            
            self.__tenancy = self.__identity.get_tenancy(
                config["tenancy"]).data            
            
        except Exception as e:
            raise RuntimeError(
                "Failed to create service objects" + str(e.args))
          

    @abstractmethod
    def do(self, action):
        pass


    def get_benchmark_dictionary(self):
        return {        
            self.entry: {
                'section': self.section,
                'recommendation_#': self.recommendation, 
                'Title': self.tittle,
                'Status': self.status, 
                'Level': self.level, 
                'Findings': self.findings
                },
        }

        

    def load_entity(self):
        pass    
    

    def analyze_entity(self):
        pass
