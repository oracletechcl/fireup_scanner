# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# printer.py
# Description: Printer decorator for printing to console

from datetime import datetime


def print_to_console(msg):
    """
    Prints a message to the console
    """
    print(msg)

def print_with_date(msg):
    print(get_current_date()+" "+msg)

def get_current_date():
    return str("["+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+"]")

def print_header(msg):
    chars = int(180)
    print("")
    print('#' * chars)
    print("#" + msg.center(chars - 2, " ") + "#")
    print('#' * chars)


def print_report_sub_header():
    print('Num' + "\t" + "Area " + "\t\t\t" + "Sub-Area "
              "\t\t\t\t\t" "Compliant" + "\t\t\t" + "Findings  " + "\t" + 'Review Point')
    print('#' * 180)

def print_report_fields(finding):
    print(finding['Recommendation #'] + "\t" + finding['Area'] + "\t" + finding['Sub Area'] + "\t" + finding['Compliant'] + "\t\t\t\t" + finding['Findings'] + "\t\t" + finding['Review Point'])

def debug_with_date(msg):
    print(get_current_date()+" DEBUG: "+msg)

def debug(msg):
    print("DEBUG: " + msg)