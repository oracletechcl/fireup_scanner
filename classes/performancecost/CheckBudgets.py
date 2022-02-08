# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# CheckBudgets.py
# Description: Implementation of class CheckBudgets based on abstract

from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
from common.utils.helpers.helper import *


class CheckBudgets(ReviewPoint):

    # Class Variables
    __budgets_with_alert_rules = []
    __identity = None

    def __init__(self,
                entry:str, 
                area:str, 
                sub_area:str, 
                review_point: str, 
                status:bool, 
                failure_cause:list, 
                findings:list, 
                mitigations:list, 
                fireup_mapping:list,
                config, 
                signer):
        self.entry = entry
        self.area = area
        self.sub_area = sub_area
        self.review_point = review_point
        self.status = status
        self.failure_cause = failure_cause
        self.findings = findings
        self.mitigations = mitigations
        self.fireup_mapping = fireup_mapping

        # From here on is the code is not implemented on abstract class
        self.config = config
        self.signer = signer
        self.__identity = get_identity_client(self.config, self.signer)
        self.__tenancy = get_tenancy_data(self.__identity, self.config)


    def load_entity(self):

        home_region = get_home_region(self.__identity, self.config)

        region_config = self.config
        region_config['region'] = home_region.region_name
        budget_client = get_budget_client(region_config, self.signer)

        budget_data = get_budget_data(budget_client, self.__tenancy.id)

        for budget in budget_data:
            alert_rules_data = get_budget_alert_rules_data(budget_client, budget.id)
            budget_dict = {
                "display_name": budget.display_name,
                "description": budget.description,
                "lifecycle_state": budget.lifecycle_state,
                "id": budget.id,
                "target_compartment_id": budget.target_compartment_id,
                "target_type": budget.target_type,
                "targets": budget.targets,
            }
            alert_rules = []
            for alert_rule in alert_rules_data:
                alert_rule_dict = {
                    "display_name": alert_rule.display_name,
                    "description": alert_rule.description,
                    "id": alert_rule.id,
                    "lifecycle_state": alert_rule.lifecycle_state,
                    "recipients": alert_rule.recipients,
                    "message": alert_rule.message,
                }
                alert_rules.append(alert_rule_dict)

            self.__budgets_with_alert_rules.append( (budget_dict, alert_rules) )


    def analyze_entity(self, entry):
        self.load_entity()

        dictionary = ReviewPoint.get_benchmark_dictionary(self)

        # Fail review point until a budget with an alert rule is found
        dictionary[entry]['status'] = False

        for budget_dict, alert_rules in self.__budgets_with_alert_rules:
            if len(alert_rules) == 0:
                dictionary[entry]['findings'].append(budget_dict)
                dictionary[entry]['mitigations'].append(f"Make sure Budget \"{budget_dict['display_name']}\" has alert rules tied to it.")
            else:
                for alert_rule in alert_rules:
                    if alert_rule['recipients'] is not "" and alert_rule['message'] is not None:
                        dictionary[entry]['status'] = True
                    else:
                        if budget_dict not in dictionary[entry]['findings']:
                            dictionary[entry]['findings'].append(budget_dict)
                        dictionary[entry]['failure_cause'].append("Ensure that budgets have email recipient(s) and an email message.")
                        dictionary[entry]['mitigations'].append(f"Make sure alert rule: \"{alert_rule['display_name']}\" for budget: \"{budget_dict['display_name']}\" has email recipient(s) and an email message.")

        if not dictionary[entry]['status']:
            dictionary[entry]['failure_cause'].append("Add budgets to your tenancy with alert rules to better monitor your spend.")
            if len(dictionary[entry]['mitigations']) == 0:
                dictionary[entry]['mitigations'].append("Create at least one budget that has an alert rule tied to it")

        return dictionary
