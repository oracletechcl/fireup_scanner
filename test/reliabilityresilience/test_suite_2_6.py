# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# fireup.py
# Description: Main test suite for fireup review tool
# Dependencies: pytest

from os import write
from classes.reliabilityresilience.LowLimits import LowLimits
from common.utils.helpers.helper import get_config_and_signer
from common.utils.formatter.printer import debug
from common.utils.statics import Statics
from common.utils.tokenizer.signer import *

  

def __test_suite_log(capsys):
    out, err = capsys.readouterr()
    open("stderr.out", "w").write(err)
    open("stdout.out", "w").write(out)

def test_review_point(capsys):     
    
    result_dictionary = LowLimits(Statics.__rp_2_6['entry'], 
    Statics.__rp_2_6['area'], 
    Statics.__rp_2_6['sub_area'], 
    Statics.__rp_2_6['review_point'], 
    True, [], [], [], [], 
    get_config_and_signer()[0], 
    get_config_and_signer()[1]
    )

    results_in_fault=0
    dictionary = result_dictionary.analyze_entity(Statics.__rp_2_6['entry'])   

    for item in dictionary[Statics.__rp_2_6['entry']]['findings']:
        debug(item)
        results_in_fault += 1


    assert results_in_fault == 4976



    __test_suite_log(capsys)