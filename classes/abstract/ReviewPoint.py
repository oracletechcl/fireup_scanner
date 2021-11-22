# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# ReviewPoint.py
# Description: Abstract Class for Review Point for later inheritance and customization


from __future__ import print_function
from common.utils.formatter.printer import *
from abc import ABC, abstractmethod
import oci



class ReviewPoint(ABC):    
    def __init__(self, entry:str, area:str, sub_area:str, review_point: str, status:bool, findings:list):        
        self.entry = entry
        self.area = area
        self.sub_area = sub_area
        self.review_point = review_point
        self.status = status
        self.findings = findings


    def get_benchmark_dictionary(self):
        return {        
            self.entry: {
                'area': self.area,
                'sub_area': self.sub_area,
                'review_point': self.review_point,
                'status': self.status,
                'findings': self.findings               
                },
        }

        
    @abstractmethod
    def load_entity(self):
        pass    
    
    @abstractmethod
    def analyze_entity(self):
        pass
