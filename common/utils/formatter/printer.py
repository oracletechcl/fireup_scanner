# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# printer.py
# Description: Printer decorator for printing to console

from datetime import datetime
from common.utils.statics import Statics
import sys
from termcolor import colored


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
    chars = int(Statics.__lenght_print__)
    print("")
    print('#' * chars)
    print("#" + turn_cyan(msg.center(chars - 2, " ")) + "#")
    print('#' * chars)


def print_report_sub_header():
    print('Num' + "  " + " {:<40}".format(str("Area")) + " {:<70}".format(str("Sub-Area")) +
              " {:<5}".format(str("OK")) + " {:<5}".format(str("Findings")) + "   {:<50}".format(str("Review Point")), flush=True)
    print('#' * int(Statics.__lenght_print__), flush=True)

def print_report_fields(finding):
    if(len(finding['Recommendation #']) == 3 ):    
        print(finding['Recommendation #'] + "   {:<40}".format(finding['Area']) + " {:<70}".format(finding['Sub Area']) + " {:<5}".format(dye_return(finding['Compliant'])) + "   {:<5}".format(finding['Findings']) + "      {:<50}".format(finding['Review Point']), flush=True)
    else:
        print(finding['Recommendation #'] + "  {:<40}".format(finding['Area']) + " {:<70}".format(finding['Sub Area']) + " {:<5}".format(dye_return(finding['Compliant'])) + "   {:<5}".format(finding['Findings']) + "      {:<50}".format(finding['Review Point']), flush=True)


def print_list_of_dicts(list_of_dicts):
    for dict in list_of_dicts:
        print(dict)

def print_mitigation_report_fields(finding):
    print(finding['Recommendation #'] + "\t" + finding['Area'] + "\t" + finding['Sub Area'] + "\t" + finding['Compliant'] + "\t" + finding['Findings'] + "\t\t" + finding['Review Point']+ "\t\t" + print_list_of_dicts(finding['Failure Causes']) +"\t\t"+print_list_of_dicts(finding['Mitigations']))

def debug_with_date(msg):
    print(get_current_date()+" DEBUG: "+str(msg))

def debug(msg):
    print("DEBUG: " + str(msg), flush=True)


def dye_return(msg):
    if(msg == "No"):
        return turn_red(msg)
    elif(msg == "Ok"):
        return turn_green(msg)


def turn_red(msg):
    return colored(msg, 'red')

def turn_green(msg):
    return colored(msg, 'green')

def turn_yellow(msg):
    return colored(msg, 'yellow')

def turn_blue(msg):
    return colored(msg, 'blue')

def turn_magenta(msg):
    return colored(msg, 'magenta')

def turn_cyan(msg):
    return colored(msg, 'cyan')

def turn_white(msg):
    return colored(msg, 'white')