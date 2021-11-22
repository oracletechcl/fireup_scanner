# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract

from common.utils.formatter.printer import debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *


class Mfa(ReviewPoint):

    def __init__(self, entry, area, sub_area, review_point, status, findings, config, signer):
       self.entry = entry
       self.area = area
       self.sub_area = sub_area
       self.review_point = review_point
       self.status = status
       self.findings = findings
       self.config = config
       self.signer = signer

    def load_entity(self):        
        dict = ReviewPoint.get_benchmark_dictionary(self)
        print(dict)
        

    def analyze_entity(self):
        debug_with_date("Printed from analyze_entity()")
        self.load_entity()
        



    