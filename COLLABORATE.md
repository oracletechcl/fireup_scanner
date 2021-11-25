# Collaboration Guidelines

## Branch and Collaboration

- In order to collaborate:
  - Open new issue on GitHub Fireup repo
  - Fork or branch-out the respository into your own personal account
  - Branch out depending on what kind of issue you are dealing
    - If this is a new review point being introduced, branch creation should follow this naming convention
      - `feature/review_point_name`
        - Avoid including numbers into branch name
    - If this is a bug report, branch creation should follow this naming convention
      - `bug/bug_report_number`
    - Upon first commit, reference the issue number for tracking
    - Once feature or bug is completed and unitary testing is done, create a Pull request against main branch on fireup repository
    - Always mark your PR with the approriate labels for tracking
    - Request review from `dralquinta`  
    - **IMPORTANT** 
      - **NEVER COMMIT TO MAIN BRANCH ON PRIMARY REPOSITORY**
      - **NEVER MERGE CODE. ONLY PROJECT LEAD CAN MERGE AND RELEASE CODE**
      - **ON EACH NEW PULL REQUEST INCLUDE THE RESULTS OF THE UNITARY TEST**


If code is successfull, then PR will be approved and later merged into main
If code contains bugs or enhancements, then PR will be returned to owner for fixing

## How Create new review point

- Locate the review point to create in sprint spreadsheet
- Update the dictionary entry on static definition under [statics.py](./common/utils/statics.py)

    For example: 
     - Review point 1.1: 
  
        ```python
        __rp_X_Y = {
           'entry': '1.1',
            'area': 'Security and Compliance',
            'sub_area': 'Manage Identities and Authorization Policies',
            'review_point': 'Enforce the Use of Multi-Factor Authentication (MFA)',
            'success_criteria': 'Check that MFA is enabled on all users',    
            }
        ```
- Create a new Concrete Class for review point under the framework structure under `classes > main_area > class`

    For example: 
    - Review point 1.1

        - Create class Mfa.py under path [classes > securitycompliance > Mfa.py](./classes/securitycompliance/Mfa.py)

- Concrete class content should look like this: 

```python
 Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# NameOfFile.py
# Description: Class Description

from common.utils.helpers.helper import *
from common.utils.formatter.printer import debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
import oci


class Mfa(ReviewPoint):

    # Class Variables
     #TODO Add here all class variables as follow
     # __class_variable_1  = None
     # __sdk_api_client = None
     # __data_handler = None
     # __tenancy = None



    def __init__(self, entry, area, sub_area, review_point, status, findings, config, signer):
       self.entry = entry
       self.area = area
       self.sub_area = sub_area
       self.review_point = review_point
       self.status = status
       self.findings = findings

       # From here on is the code is not implemented on abstract class
       self.config = config
       self.signer = signer
       self.sdk_api_client = get_api_client(self.config, self.signer)  
       ...
       ...
       ...       
       self.__tenancy = get_tenancy_data(self.__identity, self.config)

    def load_entity(self):       
        data_to_analyze = get_data_to_analyze_data(self.__sdk_api_client, other_args, ... , other_args)        
        for iterator in data_to_analyze:
                record = {
                    'foo': bar,
                    'baz': qux,
                    ...
                    ...
                    ...
                    'bar': foo,
                }
                

                self.__data_handler__.append(record)
        return self.__data_handler
                

    def analyze_entity(self, entry):
        self.load_entity()
        dictionary = ReviewPoint.get_benchmark_dictionary(self)
        for data in self.__data_handler:
         # Here apply all the analysis and conditional logic to determine the Failure status of a review point
             
         # Add the following two entries to compute a failure scenario    
             dictionary[entry]['status'] = False
             dictionary[entry]['findings'].append(user)
        return dictionary
```


**Important Notes**

- You can add as many class variables as required. Always use the convention `__variable_name = FOO` to avoid name conflicts.
- You can add as many imports you require on your Concrete class, however mandatory entries are the following: 
```python
from common.utils.helpers.helper import *
from common.utils.formatter.printer import debug_with_date, print_with_date
from classes.abstract.ReviewPoint import ReviewPoint
from common.utils.tokenizer import *
import oci
```
- When calling `self.sdk_api_client = get_api_client(self.config, self.signer)` if the helper class does not contain the required client, add it in the following way under file `common/utils/helpers/helper.py`:

```python
def get_identity_client(config, signer):
    try:
        identity_client = oci.identity.IdentityClient(config, signer=signer)
    except Exception as e:
        raise RuntimeError("Failed to create identity client: {}".format(e))
    return identity_client
```

  - Above example shows the implementation of the identity client as documented on [API reference](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/api/identity/client/oci.identity.IdentityClient.html)
  - **Structure of composer should always contain:**
    - Try and except for exception control
    - Representative name of client and then execution of API by using `oci.composer.Client()`
    - All methods should receive as arguments: `config` and `signer=signer` to use CLI Authentication


- To do the analysis of the information retrieved from API, always use the wrapper extracted object declared as class variable. Never use the direct json object coming from API.  
- Once both abstract methods are implemented, update the [Orchestrate.py](./common/orchestrator/Orchestrate.py)
- Make sure to import your concreteClass into the imports with a class alias
  - The entries on `Orchestrate.py` are the following: 
    - The entry point for execution should follow the naming convention `__call_X_Y`, where `X` and `Y` correspond to the review entry point on dictionary and on spreadsheet
    - The content of the function should always be: 
```python
def __call_X_Y(config, signer, report_directory)
    concreteclassinlowercase = ConcreteClass(statics.__rp_X_Y['entry'], statics.__rp_X_Y['area'], statics.__rp_X_Y['sub_area'], statics.__rp_X_Y['review_point'], True, [], config, signer)
    __classvariableconcreteclass = concreteclassinlowercase.analyze_entity(statics.__rp_X_Y['entry'])   
    generate_on_screen_report(__classvariableconcreteclass, report_directory, statics.__rp_X_Y['entry'])
``` 

Example: 
```python
def __call_1_1(config,signer, report_directory):       
    mfa = Mfa(statics.__rp_1_1['entry'], statics.__rp_1_1['area'], statics.__rp_1_1['sub_area'], statics.__rp_1_1['review_point'], True, [], config, signer)
    __mfa_dictionary = mfa.analyze_entity(statics.__rp_1_1['entry'])   
    generate_on_screen_report(__mfa_dictionary, report_directory, statics.__rp_1_1['entry'])
```
   
   - Update function `main_orchestrator()` as follows:

```python
  def main_orchestrator(config,signer, report_directory):
    print_header("Fireup "+statics.__version__)
    print_report_sub_header()
    __call_1_1(config, signer, report_directory)
    __call_1_2(config, signer, report_directory)
    ...
    ...
    ...
    __call_X_Y(config, signer, report_directory) 
    
```


## Unitary Testing

***This approach uses Test Driven Development Model, for which an initial successful result in findings needs to be pre-established, so later after module creation, this matches with this value.***

***The test modules are located in the `test` directory***

***The testing process is supported by pytest module***

In order to use test module, follow this methodology: 

- Determine first how many results will return a successful entry point. This value will be knowned as `ASSERTION_VALUE_FOR_CORRECT_RESULTS`
- Once determined, go to directory `test` and inside pertaining directory (see areas) create a test suite file, named `test_suite_X_Y.py` where `X_Y` is the corresponding review point. 
- The content of the file is determined by the following logic: 

File: `test_suite_X_Y.py`

```python
# Copyright (c) 2021 Oracle and/or its affiliates.
# All rights reserved. The Universal Permissive License (UPL), Version 1.0 as shown at http://oss.oracle.com/licenses/upl
# fireup.py
# Description: Main test suite for fireup review tool
# Dependencies: pytest

from os import write
from common.utils.helpers.helper import get_config_and_signer
from common.utils.formatter.printer import debug_with_date
from classes.AREA.CONCRETECLASS import ConcreteClass
from common.utils import statics
from common.utils.tokenizer.signer import *

  

def __test_suite_log(capsys):
    out, err = capsys.readouterr()
    open("stderr.out", "w").write(err)
    open("stdout.out", "w").write(out)

def test_review_point(capsys):     
    
    result_dictionary = ConcreteClass(statics.__rp_X_Y['entry'], 
    statics.__rp_X_Y['area'], 
    statics.__rp_X_Y['sub_area'], 
    statics.__rp_X_Y['review_point'], 
    True, [], get_config_and_signer()[0], 
    get_config_and_signer()[1]
    )

    results_in_fault=0
    dictionary = result_dictionary.analyze_entity(statics.__rp_X_Y['entry'])   
    
    for item in dictionary[statics.__rp_X_Y['entry']]['findings']:
        debug_with_date(item)
        results_in_fault += 1
    
    assert results_in_fault == ASSERTION_VALUE_FOR_CORRECT_RESULTS


    

    __test_suite_log(capsys)

```

To run the unitary testing, run script `unitary_test.sh`. 

- Expected results under successful test is: 

```shell
[opc@dalquintdevhubscl test]$ ./unitary_test.sh 
running pytest
running egg_info
writing fireup.egg-info/PKG-INFO
writing dependency_links to fireup.egg-info/dependency_links.txt
writing requirements to fireup.egg-info/requires.txt
writing top-level names to fireup.egg-info/top_level.txt
reading manifest file 'fireup.egg-info/SOURCES.txt'
writing manifest file 'fireup.egg-info/SOURCES.txt'
running build_ext
=========================================================================================== test session starts ============================================================================================
platform linux -- Python 3.6.8, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /home/opc/REPOS/OCIBE/MY_PROJECTS/fireup/test
collected 5 items                                                                                                                                                                                          

securitycompliance/test_suite_1_1.py .                                                                                                                                                               [ 20%]
securitycompliance/test_suite_1_2.py .                                                                                                                                                               [ 40%]
securitycompliance/test_suite_1_3.py .                                                                                                                                                               [ 60%]
securitycompliance/test_suite_1_4.py .                                                                                                                                                               [ 80%]
securitycompliance/test_suite_1_5.py .                                                                                                                                                               [100%]

============================================================================================ 5 passed in 4.94s =============================================================================================
```

- Expected results under failed test is: 

```shell
[opc@dalquintdevhubscl test]$ ./unitary_test.sh 
running pytest
running egg_info
writing fireup.egg-info/PKG-INFO
writing dependency_links to fireup.egg-info/dependency_links.txt
writing requirements to fireup.egg-info/requires.txt
writing top-level names to fireup.egg-info/top_level.txt
reading manifest file 'fireup.egg-info/SOURCES.txt'
writing manifest file 'fireup.egg-info/SOURCES.txt'
running build_ext
=========================================================================================== test session starts ============================================================================================
platform linux -- Python 3.6.8, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /home/opc/REPOS/OCIBE/MY_PROJECTS/fireup/test
collected 5 items                                                                                                                                                                                          

securitycompliance/test_suite_1_1.py .                                                                                                                                                               [ 20%]
securitycompliance/test_suite_1_2.py F                                                                                                                                                               [ 40%]
securitycompliance/test_suite_1_3.py .                                                                                                                                                               [ 60%]
securitycompliance/test_suite_1_4.py .                                                                                                                                                               [ 80%]
securitycompliance/test_suite_1_5.py .                                                                                                                                                               [100%]

================================================================================================= FAILURES =================================================================================================
____________________________________________________________________________________________ test_review_point _____________________________________________________________________________________________

capsys = <_pytest.capture.CaptureFixture object at 0x7f2d12e2b160>

    def test_review_point(capsys):
    
        result_dictionary = Admin(statics.__rp_1_2['entry'],
        statics.__rp_1_2['area'],
        statics.__rp_1_2['sub_area'],
        statics.__rp_1_2['review_point'],
        True, [], get_config_and_signer()[0],
        get_config_and_signer()[1]
        )
    
        results_in_fault=0
        dictionary = result_dictionary.analyze_entity(statics.__rp_1_2['entry'])
    
        for item in dictionary[statics.__rp_1_2['entry']]['findings']:
            debug_with_date(item)
            results_in_fault += 1
    
>       assert results_in_fault == 10
E       assert 1 == 10

securitycompliance/test_suite_1_2.py:38: AssertionError
------------------------------------------------------------------------------------------- Captured stdout call -------------------------------------------------------------------------------------------
[25/11/2021 19:40:21] DEBUG: {'compartment_id': 'ocid1.tenancy.oc1..aaaaaaaaoqdygmiidrabhv3y4hkr3rb3z6dpmgotvq2scffra6jt7rubresa', 'defined_tags': {'default_namespace': {'creator': 'oracleidentitycloudservice/muthuvel.balasubramanian@oracle.com'}}, 'description': 'For Vulnerability Scanning', 'freeform_tags': {}, 'id': 'ocid1.policy.oc1..aaaaaaaatytjyeej43ehzzor6tfshjgauuaf4fpf5n4ovlmrbfr6zqjtukwa', 'lifecycle_state': 'ACTIVE', 'name': 'vss-bmuthuv', 'statements': ['Allow service vulnerability-scanning-service to manage instances in compartment  bmuthuv', 'Allow service vulnerability-scanning-service to read compartments in compartment bmuthuv', 'Allow service vulnerability-scanning-service to read vnics in compartment bmuthuv', 'Allow service vulnerability-scanning-service to read vnic-attachments in compartment bmuthuv', 'Allow dynamic-group bmuthuv-ca-dg to use keys in compartment bmuthuv'], 'time_created': datetime.datetime(2021, 11, 24, 6, 50, 50, 35000, tzinfo=tzutc()), 'version_date': None}
========================================================================================= short test summary info ==========================================================================================
FAILED securitycompliance/test_suite_1_2.py::test_review_point - assert 1 == 10
```

**Failed Status**: This will show the test that's failing and the results the dictionary is returning as failed status. As the value of the assertion is already expected under `ASSERTION_VALUE_FOR_CORRECT_RESULTS`, this allows for quick evaluation of error and fix on implementation

For convenience, the standard output and standard error are also captured and stored in files `stdout.out` and `stderr.out`


**IMPORTANT**
If you have any question, slack or email denny.alquinta@oracle.com before doing any PR or commit

