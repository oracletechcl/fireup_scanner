# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# Helper.py
# Description: Helper functions for OCI Python SDK

import oci


__identity_client = None
__compartment_id = None
__compartments = None

def get_compartments_data(identity_client, compartment_id): 
        __identity_client = identity_client
        __compartment_id = compartment_id

        return oci.pagination.list_call_get_all_results(
        __identity_client.list_compartments,
        __compartment_id,
        compartment_id_in_subtree=True
    ).data
    
def get_policies_data(identity_client, compartment_id): 
        __identity_client = identity_client
        __compartment_id = compartment_id

        return oci.pagination.list_call_get_all_results(
        __identity_client.list_policies,
        compartment_id
    ).data


def get_user_data(identity_client, compartment_id): 
        __identity_client = identity_client
        __compartment_id = compartment_id

        return oci.pagination.list_call_get_all_results(
        __identity_client.list_users,
        compartment_id
    ).data