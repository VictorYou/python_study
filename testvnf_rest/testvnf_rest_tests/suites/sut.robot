| *** Settings *** |
| Suite Setup    | Testvnf Startup |
| Suite Teardown | Testvnf Teardown |
| Library        | ../libraries/requests_wrapper.py |
| Variables      | ../libraries/dynamic_vars.py |
| Library        | ../libraries/Testvnf_keywords.py |
| Library        | Collections |
| Variables      | ../libraries/vars.py |

| *** Variables *** |
| ${DEPLOYMENTINFO} | add a sut |
| @{mylist}      | 'viyou' | 'lynn' | 'ls' |

| *** Test Cases *** |
| add a sut OK |
|    | [Documentation] | get test case from test vnf |
|    | [Tags] | ADD |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | Should Contain | ${ret} | "result":"OK" |
|    | Should Contain | ${ret} | "class":"SetupEnvReq" |

| add a sut NOK |
|    | [Documentation] | get test case from test vnf |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | Should Contain | ${ret} | "result":"NOK" |

| get testcase OK |
|    | [Documentation] | get test case from test vnf |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${response}= | Send HTTPS No Proxy | GET | ${TESTVNF_URL}/suts/${randomsutId} |
|    | Should Contain | ${response} | "result":"OK" |
|    | Should Contain | ${response} | "tc list":[1,2,3] |

| get testcase NOK |
|    | [Documentation] | get test case from test vnf |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${nasutid} | Evaluate | ${randomsutId}+1 |
|    | ${response}= | Send HTTPS No Proxy | GET | ${TESTVNF_URL}/suts/${nasutid} |
|    | Should Contain | ${response} | "result":"NOK" |
|    | Should Not Contain | ${response} | "tc list":[1,2,3] |

| run testcase OK |
|    | [Documentation] | get test case from test vnf |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${response}= | Send HTTPS No Proxy | POST | ${TESTVNF_URL}/suts/${randomsutId}/runTests | -d testcases=[1,2,3] -d sessionId=12345 -d tvnfId=${randomtvnfId} |
|    | Should Contain | ${response} | "result":"OK" |
|    | Should Contain | ${response} | "class":"RunTestcaseReq" |

| remove a sut OK |
|    | [Documentation] | get test case from test vnf |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${ret}= | Remove One SUT | ${randomsutId} |
|    | Should Contain | ${ret} | "result":"OK" |
|    | Should Contain | ${ret} | "class":"ResetReq" |

| remove a sut NOK |
|    | [Documentation] | get test case from test vnf |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${nasutId}= | Evaluate | ${randomsutId}+1 |
|    | ${ret}= | Remove One SUT | ${nasutId} |
|    | Should Contain | ${ret} | "result":"NOK" |

| query tvnf status OK |
|    | [Documentation] | get test case from test vnf |
|    | ${response}= | Send HTTPS No Proxy | GET | ${TESTVNF_URL}/testvnf/v1/status |
|    | Should Contain | ${response} | "result":"OK" |
|    | Should Contain | ${response} | "class":"QueryStateReq" |

| abort test execution OK |
|    | [Documentation] | get test case from test vnf |
|    | ${randomsessionId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${response}= | Send HTTPS No Proxy | POST | ${TESTVNF_URL}/testvnf/v1/abortTests/${randomsessionId}/ |
|    | Should Contain | ${response} | "result":"OK" |
|    | Should Contain | ${response} | "class":"AbortTestExecutionReq" |

| *** Keywords *** |
| Add One SUT |
|    | [Arguments] | ${sutId} | ${tvnfId} |
|    | [Tags] | ADD |
|    | ${response}= | Send HTTPS No Proxy | POST | ${TESTVNF_URL}/suts | -d sutId=${sutId} -d tvnfId=${tvnfId} -d deploymentInfo="${DEPLOYMENTINFO}" |
|    | [Return] | ${response} |

| Remove One SUT |
|    | [Arguments] | ${sutId} |
|    | ${response}= | Send HTTPS No Proxy | DELETE | ${TESTVNF_URL}/suts/${sutId}/ |
|    | [Return] | ${response} |

| Get Service User Types |
|    | Return from keyword if | True | @{PASSWORDS} |

| Setup NEAC For NE Type |
|    | ${service_types}= | Get Service User Types |
|    | Return from keyword if | True | ${service_types} |
