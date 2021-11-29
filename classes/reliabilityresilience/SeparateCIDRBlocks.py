# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract

from concurrent.futures import process
from common.utils.helpers.helper import *
from common.utils.formatter.printer import debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *


class SeparateCIDRBlocks(ReviewPoint):

    # Class Variables
    __vcns = []
    __identity = None

    def __init__(self, entry, area, sub_area, review_point, status, findings, config, signer):
        self.entry = entry
        self.area = area
        self.sub_area = sub_area
        self.review_point = review_point
        self.status = status
        self.findings = findings

        # From here on is the code is not implemented on abstract class
        self.config = config
        self.signer = signer
        self.__identity = get_identity_client(self.config, self.signer)


    def load_entity(self):

        self.__vcns = get_all_vcns(self.__identity, self.config, self.signer)

        return self.__vcns                


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        debug_with_date(dictionary)

        for vcn in self.__vcns:
            debug_with_date(vcn['display_name'])

