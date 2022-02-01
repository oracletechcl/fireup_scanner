# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Report.py
# Description: Abstract Class for creating the report related to a specific review point

from common.utils.formatter.printer import *
import csv
import os
import datetime


# CLASS VARIABLES
__start_time_str = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def generate_on_screen_report(dictionary, report_directory, report_name):
    # Creating summary report
    summary_report = []
    for key, recommendation in dictionary.items():
        record = {
            "Recommendation #": key,
            "Area": recommendation['area'],
            "Sub Area": recommendation['sub_area'],                                
            "Compliant": ('Ok' if recommendation['status'] else 'No'),
            "Findings": str(len(recommendation['findings'])),
            "Review Point": recommendation['review_point']
        }
        # Add record to summary report for CSV output
        summary_report.append(record)

    for finding in summary_report:
        print_report_fields(finding)

    generate_csv_output(report_directory, report_name, dictionary)
    

def generate_mitigation_report(dictionary, report_directory, report_name, fireup_mapping):
    # Creating summary report
    dictionary = dictionary[list(dictionary.keys())[0]]

    failure_causes = []

    for failure_cause in dictionary['failure_cause']:
        if failure_cause not in failure_causes:
            failure_causes.append(failure_cause)

    failure_causes = ' | '.join(failure_causes)

    # for finding in summary_report:
    __print_mitigation_report(
        report_directory,
        report_name, 
        dictionary['mitigations'],
        fireup_mapping, 
        failure_causes)


def generate_csv_output(report_directory, report_name, dictionary):
    for index, recommendation in dictionary.items():        
        __print_to_csv_file(
                report_directory, 
                report_name, 
                recommendation['area'] + "_" + recommendation['sub_area'], 
                recommendation['findings'])


def __print_mitigation_report(report_directory, report_name,  mitigation_list, fireup_mapping, failure_causes):
    
    try:
        # Creating report directory
        report_directory=report_directory+"/reports"            
        if not os.path.isdir(report_directory):
            os.mkdir(report_directory)

    except Exception as e:
        raise Exception(
            "Error in creating report directory: " + str(e.args))

    try:
        # if no data
        if len(mitigation_list) == 0:
            return None

        # get the file name of the log file

        file_name = report_name
        file_name = (file_name.replace(" ", "_")
                        ).replace(".", "-") + ".log"
        file_path = os.path.join(report_directory, file_name)

        file = open(file_path, "w", newline='')
        file.write(report_name + "\n\n")
        # print the contents of fireup_mapping one by one in the log file
        file.write("Fireup Mapping tasks: \n")
        for x in range(len(fireup_mapping)):
            file.write(fireup_mapping[x] + "\n")
        file.write("\n")
        file.write("For a full list of FireUp Tasks, refer to FIREUP_TASKS.md\n")
        file.write("Failure Cause: " + failure_causes + "\n\n")
        file.write("The following are the mitigations to be applied: \n")
        file.write("----------------------------------------------------------------------------------------------------------------------\n")
        for row in mitigation_list:
            file.write(row + "\n")
        file.close()                       
        
        return file_path

    except Exception as e:
        raise Exception("Error in creating mitigation log file: " + str(e.args))
            

def __print_to_csv_file(report_directory, header, file_subject, data):
    
    try:
        # Creating report directory
        report_directory=report_directory+"/reports"            
        if not os.path.isdir(report_directory):
            os.mkdir(report_directory)

    except Exception as e:
        raise Exception(
            "Error in creating report directory: " + str(e.args))

    try:
        # if no data
        if len(data) == 0:
            return None

        # get the file name of the CSV

        file_name = header + "_" + file_subject
        file_name = (file_name.replace(" ", "_")).replace(".", "-") + ".csv"
        file_path = os.path.join(report_directory, file_name)

        # add start_date to each dictionary
        results = [
            dict(item, extract_date=__start_time_str)
            for item in data
        ]

        # generate fields
        fields = set()
        for result in results:
            for key in result.keys():
                fields.add(key)

        with open(file_path, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields)

            # write header
            writer.writeheader()

            for row in results:
                writer.writerow(row)

        # Used by Upload to
        return file_path

    except Exception as e:
        raise Exception("Error in print_to_csv_file: " + str(e.args))
