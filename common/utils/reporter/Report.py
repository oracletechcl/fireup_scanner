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
                "Compliant": ('Yes' if recommendation['status'] else 'No'),
                "Findings": str(len(recommendation['findings'])),
                "Review Point": recommendation['review_point']
            }
            # Add record to summary report for CSV output
            summary_report.append(record)

        for finding in summary_report:
            print_report_fields(finding)

        generate_csv_output(report_directory, report_name, dictionary )
    

def generate_csv_output(report_directory, report_name, dictionary):
    for index, recommendation in dictionary.items():        
        __print_to_csv_file(
                report_directory, 
                report_name, 
                recommendation['area'] + "_" + recommendation['sub_area'], 
                recommendation['findings'])


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
            file_name = (file_name.replace(" ", "_")
                         ).replace(".", "-") + ".csv"
            file_path = os.path.join(report_directory, file_name)

            # add start_date to each dictionary
            result = [dict(item, extract_date=__start_time_str)
                      for item in data]

            # generate fields
            fields = [key for key in result[0].keys()]

            with open(file_path, mode='w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fields)

                # write header
                writer.writeheader()

                for row in result:
                    writer.writerow(row)            
            # Used by Uplaoad to
            return file_path

        except Exception as e:
            raise Exception("Error in print_to_csv_file: " + str(e.args))