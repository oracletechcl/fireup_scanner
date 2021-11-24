# FireUp Automated check tool
Fireup automated gathering and check tool

[![License: UPL](https://img.shields.io/badge/license-UPL-green)](https://img.shields.io/badge/license-UPL-green) 
[![Github All Releases](https://img.shields.io/github/downloads/oraclecloudbricks/fireup/total.svg)](https://img.shields.io/github/downloads/oraclecloudbricks/fireup/total.svg)



## Introduction

The following tool allows to make an automated analysis of Fireup keypoints, based on Architecture Best Practice Framework Documented under the [following link](https://docs.oracle.com/en/solutions/oci-best-practices/)

The check is currently spread in 4 major areas

- Security and Compliance
- Reliability and Resilience
- Performance and Cost Optimization
- Operational Efficiency

The following is the detail of areas of interest

| Business Goal                     | Key Focus Areas                                                                                                               |
|-----------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Security and compliance           | User authentication                                                                                                           |
|                                   | Resource isolation and access control                                                                                         |
|                                   | Compute security                                                                                                              |
|                                   | Database security                                                                                                             |
|                                   | Data protection                                                                                                               |
|                                   | Network security                                                                                                              |
| Reliability and resilience        | Fault-tolerant network architecture                                                                                           |
|                                   | Service limits and quotas                                                                                                     |
|                                   | Data backup                                                                                                                   |
|                                   | Scaling                                                                                                                       |
| Performance and cost optimization | Compute sizing                                                                                                                |
|                                   | Storage strategy                                                                                                              |
|                                   | Network monitoring and tuning                                                                                                 |
|                                   | Cost tracking and management                                                                                                  |
| Operational efficiency            | Deployment strategy                                                                                                           |
|                                   | Workload monitoring                                                                                                           |
|                                   | OS management                                                                                                                 |
|                                   | Support                                                                                                                       |



## Class Structure

The following is the class structure applied to the Fireup Tool

![Class Structure](./images/fireup_class_diagram.jpeg)

The following design patterns are applied to this project: 

- [Abstract Factory Pattern](https://en.wikipedia.org/wiki/Abstract_factory_pattern)
- [Iterator Pattern](https://en.wikipedia.org/wiki/Iterator_pattern)
- [Decorator Pattern](https://en.wikipedia.org/wiki/Decorator_pattern)

___

## Pre-requisites
- Pre-configured Oracle Cloud Infrastructure (OCI) account
- Pre-configured OCI CLI. For instructions in how to configure CLI, refer to the [following link](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/climanualinst.htm)

## How to use

- Download the release given by your Oracle for Startups Architect
- Unzip the file 
- Execute the script `fireup.sh`
- Once ran, deliver the reports.tar.gz file to your Oracle for Startups Architect for review

## Expected output on console

```shell
########################################################################################################################################################################################################
#                                                                                            Fireup v1.0.0                                                                                             #
########################################################################################################################################################################################################
Num     Area                    Sub-Area                                        Compliant                       Findings        Review Point
########################################################################################################################################################################################################
1.1     Security and Compliance Manage Identities and Authorization Policies    No                              22              Enforce the Use of Multi-Factor Authentication (MFA)
1.2     Security and Compliance Manage Identities and Authorization Policies    No                              1               Don't Use the Tenancy Administrator Account for Day-to-Day Operations
...
...
...

```



___
## Credits

Refer to the following file for [credits and acknowledgements](AUTHORS.md)

## Contributing
This project is open source.  Please submit your contributions by forking this repository and submitting a pull request!  Oracle appreciates any contributions that are made by the open source community.
For rules in how to contribute, refer to the [following link](COLLABORATE.md)

## License
Copyright (c) 2021 Oracle and/or its affiliates.

Licensed under the Universal Permissive License (UPL), Version 1.0.

See [LICENSE](LICENSE) for more details.



