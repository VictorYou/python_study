| *** Settings *** |
| Library        | ../libraries/requests_wrapper.py |
| Variables      | ../libraries/dynamic_vars.py |
| Library        | ../libraries/Testvnf_keywords.py |
| Library        | Collections |
| Variables      | ../libraries/vars.py |
| Library        | SeleniumLibrary |

| *** Variables *** |
| ${DEPLOYMENTINFO} | add a sut |
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
|    | Delete TVNF Object |

| *** Keywords *** |
| Setup NEAC for NE Type |
|    | [Return] | @{PASSWORDS} |

| Login NDAP |
|    | ${status} | ${ret}= | Run Keyword And Ignore Error | Open Browser | Firefox |
|    | ${status}= | Run Keyword and Return Status | Go To | ${NDAP} |
|    | Run Keyword if | ${status} != True | Close Browser |
|    | Check and Input Text | applicationLoginUsername | admin |
|    | Check and Input Text | applicationLoginPassword | Admin123 |
|    | Check and Click Button | xpath=//*[@id="login"] |

| Check and Click Button |
|    | [Arguments] | ${element} |
|    | Check and Click | Button | ${element} |

| Check and Click Element |
|    | [Arguments] | ${element} |
|    | Check and Click | Element | ${element} |

| Check and Click Image |
|    | [Arguments] | ${element} |
|    | Check and Click | Image | ${element} |

| Check and Click Link |
|    | [Arguments] | ${element} |
|    | Check and Click | Link | ${element} |

| Check and Click |
|    | [Arguments] | ${type} | ${element} |
|    | Wait Until Element Is Visible | ${element} | 10 |
|    | ${status}= | Run Keyword and Return Status | Click ${type} | ${element} |
|    | Run Keyword if | ${status} != True | Close Browser |

| Check and Input Text |
|    | [Arguments] | ${element} | ${text} |
|    | Wait Until Element Is Visible | ${element} | 5 |
|    | Clear Element Text | ${element} |
|    | Input Text | ${element} | ${text} |

| Create TVNF Object |
|    | Login NDAP |
|    | Check and Click Image | xpath://img[@alt='Test Cases'] |
|    | Check and Click Link | xpath://a[@class='nav-link' and text()='TVNF Settings'] |
|    | Check and Click Button | xpath://button[text()='Add TVNF'] |
|    | Check and Input Text | xpath://input[@id='tn'] | ${TVNF_INFO}[0] |
|    | Check and Input Text | xpath://input[@id='tv'] | ${TVNF_INFO}[1] |
|    | Check and Input Text | xpath://input[@id='ap'] | ${TVNF_INFO}[2] |
|    | Check and Input Text | xpath://textarea[@id='dn'] | ${TVNF_INFO}[3] |
|    | Check and Click Button | xpath://button[contains(text(), 'Save TVNF')] |
|    | Close Browser |

| Delete TVNF Object |
|    | Login NDAP |
|    | Check and Click Image | xpath://img[@alt='Test Cases'] |
|    | Check and Click Link | xpath://a[@class='nav-link' and text()='TVNF Settings'] |
|    | Check and Click Button | xpath://h5[contains(text(),'fastpass_tvnf_test')]/button[@id='navbarDropdownMenuLink'] |
|    | Check and Click Element | xpath://h5[contains(text(),'fastpass_tvnf_test')]//a[@data-target='#deleteModal'] |
|    | Select Window |
|    | Wait Until Element Is Visible | xpath://h5[contains(text(),'Delete TVNF')] | 10 |
