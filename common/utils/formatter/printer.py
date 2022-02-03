# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# printer.py
# Description: Printer decorator for printing to console

from datetime import datetime
from common.utils.statics import Statics
from termcolor import colored
from inspect import getframeinfo, stack
import os.path


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
    print('% Completion'+"            "+'RP' + "   " + " {:<40}".format(str("Area")) + " {:<70}".format(str("Sub-Area")) +
              " {:<5}".format(str("OK")) + "{:<5}".format(str("Findings")) + "   {:<50}".format(str("Review Point")), flush=True)
    print('#' * int(Statics.__lenght_print__), flush=True)

def print_report_fields(finding):

    #Type 1
    type_1 = ['1.1','1.2','1.3','1.4','1.5','1.6','1.7','1.8','1.9']    
    type_2 = ['1.10']
    type_3 = ['2.1','2.2','2.3','2.4','2.5','2.6','2.7','2.8','2.9','3.1','3.2','3.3','3.4','3.5','3.6','3.7','3.8','3.9','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9']    
    if finding['Recommendation #'] in type_1:    
        print(" " +finding['Recommendation #'] + "   {:<40}".format(finding['Area']) + " {:<70}".format(finding['Sub Area']) + " {:<5}".format(dye_return(finding['Compliant'])) + "   {:<5}".format(finding['Findings']) + "      {:<50}".format(finding['Review Point']), flush=True)    
    #Type 2
    elif finding['Recommendation #'] in type_2:
        print(finding['Recommendation #'] + "  {:<40}".format(finding['Area']) + " {:<70}".format(finding['Sub Area']) + " {:<5}".format(dye_return(finding['Compliant'])) + "   {:<5}".format(finding['Findings']) + "      {:<50}".format(finding['Review Point']), flush=True)    
    #Type 3
    elif finding['Recommendation #'] in type_3:
        print(finding['Recommendation #'] + "   {:<40}".format(finding['Area']) + " {:<70}".format(finding['Sub Area']) + " {:<5}".format(dye_return(finding['Compliant'])) + "   {:<5}".format(finding['Findings']) + "      {:<50}".format(finding['Review Point']), flush=True)
    else:
    #Type 4    
        print(finding['Recommendation #'] + "  {:<40}".format(finding['Area']) + " {:<70}".format(finding['Sub Area']) + " {:<5}".format(dye_return(finding['Compliant'])) + "   {:<5}".format(finding['Findings']) + "      {:<50}".format(finding['Review Point']), flush=True)   

def print_list_of_dicts(list_of_dicts):
    for dict in list_of_dicts:
        print(dict)

def print_mitigation_report_fields(finding):
    print(finding['Recommendation #'] + "\t" + finding['Area'] + "\t" + finding['Sub Area'] + "\t" + finding['Compliant'] + "\t" + finding['Findings'] + "\t\t" + finding['Review Point']+ "\t\t" + print_list_of_dicts(finding['Failure Causes']) +"\t\t"+print_list_of_dicts(finding['Mitigations']))

def debug(msg, color=None):
    frame = getframeinfo(stack()[1][0])
    filename = os.path.splitext(os.path.basename(frame.filename))[0]
    lineno = str(frame.lineno)    

    debug_exp = get_current_date()+" DEBUG: "+filename+".py:"+lineno+" - "+str(msg)

    if (color == "red"):
        print(turn_red(debug_exp), flush=True)
    elif (color == "green"):
        print(turn_green(debug_exp), flush=True)
    elif (color == "yellow"):
        print(turn_yellow(debug_exp), flush=True)
    elif (color == "blue"):
        print(turn_blue(debug_exp), flush=True)
    elif (color == "magenta"):
        print(turn_magenta(debug_exp), flush=True)
    elif (color == "cyan"):
        print(turn_cyan(debug_exp), flush=True)
    elif (color == "grey"):
        print(turn_grey(debug_exp), flush=True)
    else:
        print(turn_white(debug_exp), flush=True)



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

def turn_grey(msg):
    return colored(msg, 'grey')