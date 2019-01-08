*** Settings ***
Documentation       Test suite to test lab state service and admin operations
...                 Container name, query, web-url and state-url
...                 can be given in command line to use test suite
...                 in other container
Library             BuiltIn
Library             lab_test_api.py
Suite Setup         Set up actions
Suite Teardown      Tear down actions


*** Variables ***
${WEB-URL}          http://localhost:8000
${STATE-URL}


*** Test Cases ***

Preserve state end to end OK test
    [Tags]      E2E
    when User reserves a lab
    then Lab is reserved
    when User preserves state of reserved lab
    then State information is in database
    when User releases reserved lab
    then Lab is not reserved

Admin operations end to end tests
    when Admin creates lab
    then Created lab is in database
    when Admin deletes empty lab from lab state service
    then lab is deleted from database

Reserve lab NOK when query is wrong
    [Tags]      NOK_RWQ
    User reserves lab with wrong query and reservation fails

Reserve lab NOK when lab is already reserved
    [Tags]      NOK_RAR
    User reserves reserved lab and reservation fails

Release lab NOk when lab is reserved by another user
    [Tags]      NOK_RRA
    User releases lab reserved for another user

Release lab NOK when lab is not reserved
    [Tags]      NOK_RUR
    User releases unreserved lab and fails

Preserve state NOK when lab is not reserved
    [Tags]      NOK_PUR
    User preserves state of unreserved lab and fails

Admin add lab NOK when lab already exists
    Admin adds lab that already exists and fails

Admin remove labs NOK when user tries to remove lab
    User removes lab and fails


*** Keywords ***

User reserves a lab
    [Arguments]
    ${OK_LABNAME}=          user reserves lab py             ${CONTAINER_NAME}       ${QUERY}        ${STATE-URL}
    set suite variable      ${OK_LABNAME}

Lab is reserved
    Test If Lab Is Reserved With Given Labname      ${OK_LABNAME}    ${WEB-URL}

User releases reserved lab
    release lab             ${OK_LABNAME}           ${CONTAINER_NAME}       ${STATE-URL}

Lab is not reserved
    lab is not reserved py      ${OK_LABNAME}       ${WEB-URL}

User preserves state of reserved lab
    preserve lab state      ${CONTAINER_NAME}       ${OK_LABNAME}

State information is in database
    find state information from database            ${OK_LABNAME}           ${WEB-URL}

User reserves lab with wrong query and reservation fails
    User Reserves Lab Whit Wrong Query And Fails Py      ${CONTAINER_NAME}       ${STATE-URL}

User reserves reserved lab and reservation fails
    ${NOK_LABNAME}=    user reserves reserved lab and fails py         ${CONTAINER_NAME}        ${STATE-URL}

User releases lab reserved for another user
    user releases lab reserved for another user and fails       ${CONTAINER_NAME}     ${STATE-URL}

User releases unreserved lab and fails
    user releases unreserved lab and fails py                   ${CONTAINER_NAME}               ${STATE-URL}

User preserves state of unreserved lab and fails
    User preserves state of unreserved lab and fails py     ${CONTAINER_NAME}

Operation should fail
    Compare error message with intended message     ${MSG}      ${INTENDED}

Admin creates lab
    Admin creates lab py                    ${CONTAINER_NAME}

Admin adds lab that already exists and fails
    Admin adds lab that already exists and fails py         ${CONTAINER_NAME}

Admin deletes empty lab from lab state service
    Admin removes lab py                    ${CONTAINER_NAME}

lab is deleted from database
    Lab should not be in database py        ${WEB-URL}

Created lab is in database
    lab_should_be_in_database               ${WEB-URL}

User removes lab and fails
    User removes lab and fails py           ${CONTAINER_NAME}

Set up actions
    ${CONTAINER_NAME}=      get container name
    set suite variable      ${CONTAINER_NAME}
    create test data        ${CONTAINER_NAME}
    ${QUERY}=               find lab query          ${CONTAINER_NAME}
    set suite variable      ${QUERY}

Teardown actions
    clear test data         ${WEB-URL}

