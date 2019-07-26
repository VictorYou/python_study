| *** Settings *** |
| Library        | Collections |
| Library        | SeleniumLibrary |

| *** Variables *** |
| ${DEPLOYMENTINFO} | add a sut |
| @{mylist}      | viyou | lynn | ls |
| ${NDAP}        | https://10.157.169.150 |

| *** Keywords *** |
| Setup NEAC for NE Type |
|    | [Return] | @{PASSWORDS} |

| Check and Click Button |
|    | [Arguments] | ${element} | ${wait}=False |
|    | Check and Click | Button | ${element} | ${wait} |

| Check and Click Element |
|    | [Arguments] | ${element} | ${wait}=False |
|    | Check and Click | Element | ${element} | ${wait} |

| Check and Click Image |
|    | [Arguments] | ${element} | ${wait}=False |
|    | Check and Click | Image | ${element} | ${wait} |

| Check and Click Link |
|    | [Arguments] | ${element} | ${wait}=False |
|    | Check and Click | Link | ${element} |

| Check and Click |
|    | [Arguments] | ${type} | ${element} | ${wait}=False |
|    | Wait Until Element Is Visible | ${element} | 10 |
|    | ${status}= | Run Keyword and Return Status | Click ${type} | ${element} |
|    | Run Keyword if | ${status} != True | Log | Fail to click ${element} |
|    | Run Keyword If | ${wait} == True | Wait Until Page Does Not Contain Element | ${element} | 10 |

| Check and Input Text |
|    | [Arguments] | ${element} | ${text} |
|    | Wait Until Element Is Visible | ${element} | 5 |
|    | Clear Element Text | ${element} |
|    | Input Text | ${element} | ${text} |

| Check List Value |
|    | [Arguments] | ${element} | ${value} |
|    | ${list}= | Get List Items | ${element} |
|    | List Should Contain Value | ${list} | ${value} |

| Create TVNF Object |
|    | Login NDAP |
|    | Check and Click Image | xpath://img[@alt='Test Cases'] |
|    | Check and Click Link | xpath://a[@class='nav-link' and text()='TVNF Settings'] |
|    | Check and Click Button | xpath://button[text()='Add TVNF'] |
|    | Check and Input Text | xpath://input[@id='tn'] | ${TVNF_INFO}[0] |
|    | Check and Input Text | xpath://input[@id='tv'] | ${TVNF_INFO}[1] |
|    | Check and Input Text | xpath://input[@id='ap'] | ${TVNF_INFO}[2] |
|    | Check and Input Text | xpath://textarea[@id='dn'] | ${TVNF_INFO}[3] |
|    | Check and Click Button | xpath://button[contains(text(), 'Save TVNF')] | True |
|    | Logout NDAP |

| Delete TVNF Object |
|    | Login NDAP |
|    | Check and Click Image | xpath://img[@alt='Test Cases'] |
|    | Check and Click Link | xpath://a[@class='nav-link' and text()='TVNF Settings'] |
|    | Check and Click Button | xpath://h5[contains(text(),'fastpass_tvnf_test')]/button[@id='navbarDropdownMenuLink'] |
|    | Check and Click Element | xpath://h5[contains(text(),'fastpass_tvnf_test')]//a[@data-target='#deleteModal'] |
|    | Check and Click Button | xpath://div[@id="deleteModal"]//button[contains(text(),'Yes, Proceed')] |
|    | Logout NDAP |

| Login NDAP |
|    | Run Keyword And Ignore Error | Open Browser | Firefox |
|    | ${status}= | Run Keyword and Return Status | Go To | ${NDAP} |
|    | Run Keyword if | ${status} != True | Close Browser |
|    | Check and Input Text | applicationLoginUsername | admin |
|    | Check and Input Text | applicationLoginPassword | Admin123 |
|    | Check and Click Button | xpath=//*[@id="login"] | True |

| Logout NDAP |
|    | Close Browser |
