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
| try list |
|    | ${name}= | Set Variable | NEAC |
|    | ${list}= | Run keyword | Setup ${name} for NE Type |
|    | ${index}= | Get Index From List | ${list} | nemuuser |
|    | ${mylistindex}= | Get Index From List | ${mylist} | lynn |
|    | ${listlength}= | Get Length | ${list} |
|    | ${shouldcontain}= | List Should Contain Value | ${list} | nemuuser |
|    | ${contains}= | Run Keyword And Return Status | List Should Contain Value | ${list} | nemuuser | xx |
|    | #Check Existing Credentials Or Create New | ${list} |
|    | #${mylistlength}= | Get Length | ${mylist} |
|    | #${password_ength}= | Get Length | ${PASSWORDS} |
|    | #${newlist}= | Set Variable | viyou | lynn |
|    | #${newlistindex}= | Get Index From List | ${newlist} | 'lynn' |
|    | #${newlistlength}= | Get Length | ${newlist} |

| try loop |
|    | : FOR | ${i} | IN RANGE | 0 | 5 |
|    |    | ${v}= | Evaluate | ${i}+1 |
|    |    | log | ${v} |

| try browser |
|    | [Tags] | TEST |
|    | ${status} | ${ret}= | Run Keyword And Ignore Error | Open Browser | Firefox |
|    | ${status}= | Run Keyword and Return Status | Go To | https://10.157.169.150 |
|    | Wait Until Element Is Visible | applicationLoginUsername | 5 |
|    | Clear Element Text | applicationLoginUsername |
|    | Input Text | applicationLoginUsername | admin |
|    | Wait Until Element Is Visible | applicationLoginPassword | 5 |
|    | Clear Element Text | applicationLoginPassword |
|    | Input Text | applicationLoginPassword | Admin123 |
|    | #Wait Until Element Is Visible | login | 5 |
|    | Wait Until Element Is Visible | xpath=//*[@id="login"] | 5 |
|    | ${status}= | Run Keyword and Return Status | Click Button | login |
|    | #Wait Until Element Is Visible | testMenu | 10 |
|    | #${status}= | Run Keyword and Return Status | Click Element | testMenu |
|    | ${element}= | Set Variable | xpath://img[@alt='Test Cases'] |
|    | Wait Until Element Is Visible | ${element} | 10 |
|    | ${status}= | Run Keyword and Return Status | Click Image | ${element} |
|    | #Close Browser |

| Test |
|    | Create TVNF Workflow |
|    | comment | Create TVNF Object |
|    | comment | Delete TVNF Object |

| *** Keywords *** |
| Create TVNF Object |
|    | Check and Click Image | xpath://img[@alt='Test Cases'] |
|    | Check and Click Link | xpath://a[@class='nav-link' and text()='TVNF Settings'] |
|    | Check and Click Button | xpath://button[text()='Add TVNF'] |
|    | Check and Input Text | xpath://input[@id='tn'] | ${TVNF_INFO}[0] |
|    | Check and Input Text | xpath://input[@id='tv'] | ${TVNF_INFO}[1] |
|    | Check and Input Text | xpath://input[@id='ap'] | ${TVNF_INFO}[2] |
|    | Check and Input Text | xpath://textarea[@id='dn'] | ${TVNF_INFO}[3] |
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
|    | Check List Value | xpath://h6[contains(text(),'Select a product')]/..//select | NetAct Fast Pass Test VNF |
|    | Check List Value | xpath://h6[contains(text(),'Select a variant')]/..//select | FastPass-TVNF-OpenStack |
|    | Check List Value | xpath://h6[contains(text(),'Select a release')]/..//select | Release 19 |
|    | Check List Value | xpath://h6[contains(text(),'Select a version')]/..//select | 19.0.297 |

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
