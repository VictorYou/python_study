| *** Settings *** |
| Library        | ../libraries/requests_wrapper.py |
| Variables      | ../libraries/dynamic_vars.py |
| Library        | ../libraries/Testvnf_keywords.py |

| *** Variables *** |
| ${DEPLOYMENTINFO} | add a sut |

| *** Test Cases *** |
| add a sut OK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | Should Contain | ${ret} | "result":"OK" |
|    | [Teardown] | Testvnf Teardown |

| add a sut NOK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | Should Contain | ${ret} | "result":"NOK" |
|    | [Teardown] | Testvnf Teardown |

| get testcase OK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${response}= | Send Http No Proxy | GET | ${TESTVNF_URL}/suts/${randomsutId} |
|    | Should Contain | ${response} | "result":"OK" |
|    | Should Contain | ${response} | "tc list":[1,2,3] |
|    | [Teardown] | Testvnf Teardown |

| get testcase NOK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${nasutid} | Evaluate | ${randomsutId}+1 |
|    | ${response}= | Send Http No Proxy | GET | ${TESTVNF_URL}/suts/${nasutid} |
|    | Should Contain | ${response} | "result":"NOK" |
|    | Should Not Contain | ${response} | "tc list":[1,2,3] |
|    | [Teardown] | Testvnf Teardown |

| run testcase OK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${response}= | Send Http No Proxy | POST | ${TESTVNF_URL}/suts/${randomsutId}/runTests/ | -d testcases=[1,2,3] -d sessionId=12345 -d tvnfId=${randomtvnfId} |
|    | Should Contain | ${response} | "result":"OK" |
|    | [Teardown] | Testvnf Teardown |

| *** Keywords *** |
| Add One SUT |
|    | [Arguments] | ${sutId} | ${tvnfId} |
|    | ${response}= | Send HTTP No Proxy | POST | ${TESTVNF_URL}/suts/ | -d sutId=${sutId} -d tvnfId=${tvnfId} -d deploymentInfo="${DEPLOYMENTINFO}" |
|    | [Return] | ${response} |
