# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Report.py
# Description: Abstract Class for creating the report related to a specific review point

from common.utils.formatter.printer import *


def generate_report(self):
       print_with_date("TODO: Here develop logic to print out csv and reports")



def generate_report(self, reviewpoint_collection):
        # This function reports generates CSV reports

        # Collecting all the tenancy data
        self.__report_collect_tenancy_data()

        # Analyzing Data in reports
        self.__report_analyze_tenancy_data()

        # Creating summary report
        summary_report = []
        for key, recommendation in reviewpoint_collection.items():
            record = {
                "Recommendation #": key,
                "Section": recommendation['section'],
                "Level": str(recommendation['Level']),
                "Compliant": ('Yes' if recommendation['Status'] else 'No'),
                "Findings": str(len(recommendation['Findings'])),
                "Title": recommendation['Title']
            }
            # Add record to summary report for CSV output
            summary_report.append(record)

        # Screen output for fireup_security Summary Report
        print_header("Fireup Security Benchmark 1.1 Summary Report")
        print('Num' + "\t" + "Level " +
              "\t" "Compliant" + "\t" + "Findings  " + "\t" + 'Title')
        print('#' * 90)
        for finding in summary_report:
            # If print_to_screen is False it will only print non-compliant findings
            if not(self.__print_to_screen) and finding['Compliant'] == 'No':
                print(finding['Recommendation #'] + "\t" +
                      finding['Level'] + "\t" + finding['Compliant'] + "\t\t" +
                      finding['Findings'] + "\t\t" + finding['Title'])
            elif self.__print_to_screen:
                print(finding['Recommendation #'] + "\t" +
                      finding['Level'] + "\t" + finding['Compliant'] + "\t\t" +
                      finding['Findings'] + "\t\t" + finding['Title'])

        # Generating Summary report CSV
        print_header("Writing reports to CSV")
        summary_file_name = self.__print_to_csv_file(
            self.__report_directory, "fireup_security", "summary_report", summary_report)
        # Out putting to a bucket if I have one
        if summary_file_name and self.__output_bucket:
            self.__os_copy_report_to_object_storage(
                self.__output_bucket, summary_file_name)

        for key, recommendation in self.security_foundation_benchmark.items():
            report_file_name = self.__print_to_csv_file(
                self.__report_directory, "fireup_security", recommendation['section'] + "_" + recommendation['recommendation_#'], recommendation['Findings'])
            if report_file_name and self.__output_bucket:
                self.__os_copy_report_to_object_storage(
                    self.__output_bucket, report_file_name)

def __report_collect_tenancy_data(self):

        print_header("Processing Tenancy Data for " +
                            self.__tenancy.name + "...")

     

        self.__identity_read_users()