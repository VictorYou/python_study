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
| @{mylist}      | viyou | lynn | ls |
| ${NDAP}        | https://10.157.169.150 |

| *** Test Cases *** |
| Test |
|    | Create TVNF Workflow |
|    | comment | Create TVNF Object |
|    | comment | Delete TVNF Object |

| *** Keywords *** |
| Create TVNF Object |
|    | Check and Click Image | xpath://img[@alt='Test Cases'] |
|    | Check and Click Link | xpath://a[@class='nav-link' and text()='TVNF Settings'] |
|    | Check and Click Button | xpath://button[text()='Add TVNF'] |
|    | Check and Input Text | xpath://input[@id='tn'] | ${TVNF_DEPLOYMENT_INFO}[0] |
|    | Check and Input Text | xpath://input[@id='tv'] | ${TVNF_DEPLOYMENT_INFO}[1] |
|    | Check and Input Text | xpath://input[@id='ap'] | ${TVNF_DEPLOYMENT_INFO}[2] |
|    | Check and Input Text | xpath://textarea[@id='dn'] | ${TVNF_DEPLOYMENT_INFO}[3] |
|    | Check and Click Button | xpath://button[contains(text(), 'Save TVNF')] | True |
|    | [Teardown] | Click Dashboard |

| Delete TVNF Object |
|    | Check and Click Image | xpath://img[@alt='Test Cases'] |
|    | Check and Click Link | xpath://a[@class='nav-link' and text()='TVNF Settings'] |
|    | Check and Click Button | xpath://h5[contains(text(),'fastpass_tvnf_test')]/button[@id='navbarDropdownMenuLink'] |
|    | Check and Click Element | xpath://h5[contains(text(),'fastpass_tvnf_test')]//a[@data-target='#deleteModal'] |
|    | Check and Click Button | xpath://div[@id="deleteModal"]//button[contains(text(),'Yes, Proceed')] |
|    | [Teardown] | Click Dashboard |

| Create TVNF Workflow |
|    | Check and Click Image | xpath://img[@alt='Products'] |
|    | ${parent_node}= | Set Variable | xpath://h6[contains(text(),'Select a product')]/..// |
|    | : FOR | ${i} | IN RANGE | 0 | 3 |
|    |    | ${index}= | Evaluate | ${i}+1 |
|    |    | Check and Select List Value | ${parent_node}generic-dropdown[${index}]/select/option | ${TVNF_DEPLOYMENT_OPTIONS}[${i}] |
|    | Check and Input Text | ${parent_node}input[@type='text'] | ${FASTPASS_TVNF_WORKFLOW} |
|    | ${create_button}= | Set Variable | ${parent_node}button[contains(text(),'Create Deployment Instance')] |
|    | Wait Until Element Is Enabled | ${create_button} |
|    | Scroll To Element | ${create_button} |
|    | Check and Click Button | ${create_button} |

| Login NDAP |
|    | Run Keyword And Ignore Error | Open Browser | Firefox |
|    | ${status}= | Run Keyword and Return Status | Go To | ${NDAP} |
|    | Run Keyword if | ${status} != True | Close Browser |
|    | Check and Input Text | applicationLoginUsername | admin |
|    | Check and Input Text | applicationLoginPassword | Admin123 |
|    | Check and Click Button | xpath=//*[@id="login"] | True |

| Logout NDAP |
|    | Close Browser |

| Click Dashboard |
|    | Check and Click Link | xpath://a[@href="/dashboard-view"] |
