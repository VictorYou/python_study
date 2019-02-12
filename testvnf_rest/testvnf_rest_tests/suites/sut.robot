| *** Settings *** |
| Library        | ../libraries/requests_wrapper.py |
| Variables      | ../libraries/dynamic_vars.py |
| Library        | ../libraries/Testvnf_keywords.py |

| *** Variables *** |
| ${DEPLOYMENTINFO} | add a sut |

| *** Test Cases *** |
| add one SUT |
|    | [Documentation] | a test suite to add one SUT |
|    | [Tags] | sut |
|    | [Setup] | Testvnf Startup |
|    | [Timeout] | 1 minute |
|    | ${randomtvnfId} | Evaluate | random.randint(0,100000) | modules=random |
|    | ${randomsutId} | Evaluate | random.randint(0,100000) | modules=random |
|    | Set Suite Variable | ${SUTID} | ${randomsutId} |
|    | ${response}= | Send HTTP No Proxy | POST | ${TESTVNF_URL}/suts/ | -d sutId=${randomsutId} -d tvnfId=${randomtvnfId} -d deploymentInfo="${DEPLOYMENTINFO}" |
|    | Should Match Regexp | ${response} | {"sutId":"\\d+"} |
|    | [Teardown] | Testvnf Teardown |

| get testcase |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${response}= | Send Http No Proxy | GET | ${TESTVNF_URL}/suts/${SUTID} |
|    | Should Contain | ${response} | "result":"OK" |
|    | Should Contain | ${response} | "tc list":[1,2,3] |
|    | [Teardown] | Testvnf Teardown |
