| *** Settings *** |
| Library        | ../libraries/requests_wrapper.py |
| Variables      | ../libraries/dynamic_vars.py |
| Library        | ../libraries/Testvnf_keywords.py |

| *** Test Cases *** |
| add one SUT |
|    | [Documentation] | a test suite to add one SUT |
|    | [Setup] | Testvnf Startup |
|    | [Timeout] | 1 minute |
|    | ${response}= | Send HTTP No Proxy | POST | ${TESTVNF_URL}/suts/suts/ |
|    | Should Contain | ${response} | sutId |
|    | [Teardown] | Testvnf Teardown |
