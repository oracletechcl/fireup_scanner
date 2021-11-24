# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# printer.py
# Description: Printer decorator for printing to console

from datetime import datetime
from common.utils import statics


def print_to_console(msg):
    """
    Prints a message to the console
    """
    print(msg)

def print_with_date(msg):
    print(get_current_date()+" "+str(msg))

def get_current_date():
    return str("["+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+"]")

def print_header(msg):
    chars = int(statics.__lenght_print__)
    print("")
    print('#' * chars)
    print("#" + msg.center(chars - 2, " ") + "#")
    print('#' * chars)


def print_report_sub_header():
    print('Num' + "\t" + "Area " + "\t\t\t" + "Sub-Area "
              "\t\t\t\t\t" "Compliant" + "\t\t\t" + "Findings  " + "\t" + 'Review Point')
    print('#' * int(statics.__lenght_print__))

def print_report_fields(finding):
    print(finding['Recommendation #'] + "\t" + finding['Area'] + "\t" + finding['Sub Area'] + "\t" + finding['Compliant'] + "\t\t\t\t" + finding['Findings'] + "\t\t" + finding['Review Point'])

def debug_with_date(msg):
    print(get_current_date()+" DEBUG: "+str(msg))

def debug(msg):
    print("DEBUG: " + str(msg))