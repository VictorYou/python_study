| *** Settings *** |
| Suite Setup    | Login NDAP |
| Suite Teardown | Logout NDAP |
| Library        | ../libraries/requests_wrapper.py |
| Variables      | ../libraries/dynamic_vars.py |
| Library        | ../libraries/Testvnf_keywords.py |
| Library        | Collections |
| Variables      | ../libraries/vars.py |
| Library        | SeleniumLibrary |
| Resource       | ../resources/res_common.robot |

| *** Variables *** |

| *** Test Cases *** |
| Set up Test VNF |
|    | Create TVNF Object |
|    | Create TVNF Deployment | ${TVNF_DEPLOYMENT_OPTIONS} | ${TVNF_DEPLOYMENT_NAME} |
|    | Modify Workflow Parameter | ${TVNF_DEPLOYMENT_NAME} | ${WORKFLOW_CREATE} | ${CREATE_PARAMETER_NAME_TVNF_NAME} | ${TVNF_DEPLOYMENT_INFO}[0] |
|    | Modify Workflow Parameter | ${TVNF_DEPLOYMENT_NAME} | ${WORKFLOW_CREATE} | ${CREATE_PARAMETER_NAME_REPOSITORY} | ${PARAMETER_VALUE_REPOSITORY} |
|    | Start Workflow | ${TVNF_DEPLOYMENT_NAME} | ${WORKFLOW_CREATE} |

| Create TVNF Object |
|    | Create TVNF Object |

| Create TVNF Deployment |
|    | Create TVNF Deployment | ${TVNF_DEPLOYMENT_OPTIONS} | ${TVNF_DEPLOYMENT_NAME} |

| Modify Workflow Parameter |
|    | Modify Workflow Parameter | ${TVNF_DEPLOYMENT_NAME} | ${WORKFLOW_CREATE} | ${CREATE_PARAMETER_NAME_TVNF_NAME} | ${TVNF_DEPLOYMENT_INFO}[0] |

| Start Workflow |
|    | Start Workflow | ${TVNF_DEPLOYMENT_NAME} | ${WORKFLOW_NAME} |

| try |
|    | comment | ${list}= | Set Variable | viyou | Lynn |
|    | comment | Should Contain Match | ${list} | v* |
|    | comment | Should Contain Match | ${list} | regexp=Ly.* |
|    | comment | ${length} | Evaluate | len(${list}) |
|    | comment | Log | ${length} |
|    | comment | ${match} | Run Keyword And Return Status | Should Match Regexp | viyou | b.* |
|    | comment | : FOR | ${i} | IN RANGE | 0 | 1 |
|    | comment | Log | ${i} |
|    | comment | Create TVNF Deployment | ${TVNF_DEPLOYMENT_OPTIONS} | ${TVNF_DEPLOYMENT_NAME} |
|    | Run Keyword And Ignore Error | Open Browser | http://example.com | Chrome |

| *** Keywords *** |
| Goto Dashboard |
|    | Go To | ${DASHBOARD_URL} |

| Create TVNF Object |
|    | Check and Click Image | xpath://img[@alt='Test Cases'] |
|    | Check and Click Link | xpath://a[@class='nav-link' and text()='Test Harness Settings'] |
|    | Check and Click Button | xpath://button[text()='Add Test Harness'] |
|    | Check and Input Text | xpath://input[@id='tn'] | ${TVNF_DEPLOYMENT_INFO}[0] |
|    | Check and Input Text | xpath://input[@id='tv'] | ${TVNF_DEPLOYMENT_INFO}[1] |
|    | Check and Input Text | xpath://input[@id='ap'] | ${TVNF_DEPLOYMENT_INFO}[2] |
|    | Check and Input Text | xpath://textarea[@id='dn'] | ${TVNF_DEPLOYMENT_INFO}[3] |
|    | Check and Click Button | xpath://button[contains(text(), 'Save Test Harness')] | True |
|    | [Teardown] | Goto Dashboard |

| Create TVNF Deployment |
|    | [Arguments] | ${deployment_options} | ${workflow_name} |
|    | Check and Click Image | xpath://img[@alt='Products'] |
|    | ${parent_node}= | Set Variable | xpath://h6[contains(text(),'Select a product')]/..// |
|    | ${len} | Evaluate | len(${deployment_options}) |
|    | : FOR | ${i} | IN RANGE | 0 | 4 |
|    |    | ${index}= | Evaluate | ${i}+1 |
|    |    | Check and Select List Value | ${parent_node}generic-dropdown[${index}]/select/option | ${deployment_options}[${i}] |
|    | Check and Input Text | ${parent_node}input[@type='text'] | ${workflow_name} |
|    | ${create_button}= | Set Variable | ${parent_node}button[contains(text(),'Create Deployment Instance')] |
|    | Wait Until Element Is Enabled | ${create_button} |
|    | Scroll To Element | ${create_button} |
|    | Check and Click Button | ${create_button} |
|    | [Teardown] | Goto Dashboard |

| Delete TVNF Object |
|    | Check and Click Image | xpath://img[@alt='Test Cases'] |
|    | Check and Click Link | xpath://a[@class='nav-link' and text()='TVNF Settings'] |
|    | Check and Click Button | xpath://h5[contains(text(),'fastpass_tvnf_test')]/button[@id='navbarDropdownMenuLink'] |
|    | Check and Click Element | xpath://h5[contains(text(),'fastpass_tvnf_test')]//a[@data-target='#deleteModal'] |
|    | Check and Click Button | xpath://div[@id="deleteModal"]//button[contains(text(),'Yes, Proceed')] |
|    | [Teardown] | Goto Dashboard |

| Login NDAP |
|    | Run Keyword And Ignore Error | Open Browser | Firefox |
|    | ${status}= | Run Keyword and Return Status | Go To | ${NDAP} |
|    | Run Keyword if | ${status} != True | Close Browser |
|    | Check and Input Text | xpath=//input[@name='username'] | general_admin |
|    | Check and Input Text | xpath=//input[@name='password'] | Admin123$ |
|    | Check and Click Button | xpath=//input[@name="login"] | True |

| Logout NDAP |
|    | Close Browser |

| Modify Workflow Parameter |
|    | [Arguments] | ${deployment_name} | ${workflow_name} | ${element} | ${value} |
|    | Check and Click Image | xpath://img[@alt='Deployments'] |
|    | ${deployment_link}= | Set Variable | xpath://a[contains(text(),'${deployment_name}')] |
|    | Wait Until Element Is Visible | ${deployment_link} | 10 |
|    | Scroll To Element | ${deployment_link} |
|    | Wait For Workflow Start Button | ${deployment_name} | ${workflow_name} |
|    | ${workflow_link}= | Set Variable | xpath://a[contains(text(),'${deployment_name}')]/../../..//a[contains(text(),'${workflow_name}')] |
|    | Check and Click Link | ${workflow_link} |
|    | Check and Click Button | xpath://button[contains(text(),'Edit')] |
|    | Check and Click Element | xpath://span[contains(text(),'Parameters')] |
|    | Check and Input Text | ${element} | ${value} |
|    | Check and Click Element | xpath://span[contains(text(),'Details')] |
|    | Check and Click Element | xpath://button[contains(text(),'Save Changes')] |
|    | [Teardown] | Goto Dashboard |

| Start Workflow |
|    | [Arguments] | ${deployment_name} | ${workflow_name} |
|    | Check and Click Image | xpath://img[@alt='Deployments'] |
|    | ${start_workflow_button}= | Wait For Workflow Start Button | ${deployment_name} | ${workflow_name} |
|    | Check and Click Element | ${start_workflow_button} |
|    | [Teardown] | Goto Dashboard |
