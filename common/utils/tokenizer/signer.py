# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# signer.py
# Description: Creates the signer for OCI REST API passwordless authentication
# Dependencies: oci 

import oci
import os

def create_signer(config_profile, is_instance_principals, is_delegation_token):

    # if instance principals authentications
    if is_instance_principals:
        try:
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            config = {'region': signer.region, 'tenancy': signer.tenancy_id}
            return config, signer

        except Exception:
            print("Error obtaining instance principals certificate, aborting")
            raise SystemExit

    # -----------------------------
    # Delegation Token
    # -----------------------------
    elif is_delegation_token:

        try:
            # check if env variables OCI_CONFIG_FILE, OCI_CONFIG_PROFILE exist and use them
            env_config_file = os.environ.get('OCI_CONFIG_FILE')
            env_config_section = os.environ.get('OCI_CONFIG_PROFILE')

            # check if file exist
            if env_config_file is None or env_config_section is None:
                print(
                    "*** OCI_CONFIG_FILE and OCI_CONFIG_PROFILE env variables not found, abort. ***")
                print("")
                raise SystemExit

            config = oci.config.from_file(env_config_file, env_config_section)
            delegation_token_location = config["delegation_token_file"]

            with open(delegation_token_location, 'r') as delegation_token_file:
                delegation_token = delegation_token_file.read().strip()
                # get signer from delegation token
                signer = oci.auth.signers.InstancePrincipalsDelegationTokenSigner(
                    delegation_token=delegation_token)

                return config, signer

        except KeyError:
            print("* Key Error obtaining delegation_token_file")
            raise SystemExit

        except Exception:
            raise

    # -----------------------------
    # config file authentication
    # -----------------------------
    else:
        try:
            config = oci.config.from_file(
                oci.config.DEFAULT_LOCATION,
                (config_profile if config_profile else oci.config.DEFAULT_PROFILE)
            )
            signer = oci.signer.Signer(
                tenancy=config["tenancy"],
                user=config["user"],
                fingerprint=config["fingerprint"],
                private_key_file_location=config.get("key_file"),
                pass_phrase=oci.config.get_config_value_or_default(
                    config, "pass_phrase"),
                private_key_content=config.get("key_content")
            )
            return config, signer
        except Exception:
            print(f""
                  f"  ****************************************************************** CALL TO ACTION ******************************************************************\n"
                  f"  Please finish the configuration of file {oci.config.DEFAULT_LOCATION} \n"               
                  f"  Follow this documentation to finish the CLI configuration: https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#File_Entries\n"    
                  f"  A correct configuration file at {oci.config.DEFAULT_LOCATION} looks like this:\n\n" 
                  f"     [DEFAULT]\n"
                  f"     region = us-ashburn-1\n"
                  f"     tenancy = ocid1.tenancy.oc1..aaaaaaaaw7e6nkszrry6d5hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n"
                  f"     user = ocid1.user.oc1..aaaaaaaayblfepjieoxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n" 
                  f"     fingerprint = 19:1d:7b:3a:17\n"
                  f"     key_file = ~/.oci/oci_api_key.pem\n"
                  f"     \n\n"
                  f"Once file is created, run command: chmod 600 ~/.oci/oci_api_key.pem and run ./fireup.sh script again. \n"
                  f"  \n"
                  f"  ****************************************************************** CALL TO ACTION ******************************************************************\n" )

    

            raise SystemExit