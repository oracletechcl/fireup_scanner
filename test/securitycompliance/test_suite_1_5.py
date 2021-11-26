# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# fireup.py
# Description: Main test suite for fireup review tool
# Dependencies: pytest

from os import write
from classes.securitycompliance.FederatedUsers import FederatedUsers
from common.utils.helpers.helper import get_config_and_signer
from common.utils.formatter.printer import debug_with_date
from common.utils import statics
from common.utils.tokenizer.signer import *

  

def __test_suite_log(capsys):
    out, err = capsys.readouterr()
    open("stderr.out", "w").write(err)
    open("stdout.out", "w").write(out)

def test_review_point(capsys):     
    
    result_dictionary = FederatedUsers(statics.__rp_1_6['entry'], 
    statics.__rp_1_6['area'], 
    statics.__rp_1_6['sub_area'], 
    statics.__rp_1_6['review_point'], 
    True, [], get_config_and_signer()[0], 
    get_config_and_signer()[1]
    )

    results_in_fault=0
    dictionary = result_dictionary.analyze_entity(statics.__rp_1_6['entry'])   
    
    for item in dictionary[statics.__rp_1_6['entry']]['findings']:
        debug_with_date(item)
        results_in_fault += 1    

    assert results_in_fault == 22

    __test_suite_log(capsys)