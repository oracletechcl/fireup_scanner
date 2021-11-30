# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Mfa.py
# Description: Implementation of class MFA based on abstract

from concurrent.futures import process
from common.utils.helpers.helper import *
from common.utils.formatter.printer import debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from itertools import combinations
import ipaddr


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

        pairs = combinations(self.__vcns, 2)

        for vcn1, vcn2 in pairs:
            for cidr1 in vcn1['cidr_blocks']:
                for cidr2 in vcn2['cidr_blocks']:
                    # If the VCN is not compliant, add it to findings if it hasn't already been added
                    if ipaddr.IPNetwork(cidr1).overlaps(ipaddr.IPNetwork(cidr2)):
                        dictionary[entry]['status'] = False
                        if vcn1 not in dictionary[entry]['findings']:
                            dictionary[entry]['findings'].append(vcn1)

        return dictionary
