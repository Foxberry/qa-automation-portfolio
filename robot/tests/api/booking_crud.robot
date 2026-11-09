*** Settings ***
Documentation       CRUD lifecycle and authorisation rules of the Restful-Booker API.
Resource            ../../resources/api.resource
Suite Setup         Run Keywords    Open Booker Session    AND    Authenticate As Admin
Test Tags           api


*** Test Cases ***
Created Booking Can Be Read Back
    [Tags]    smoke
    ${payload}=    Generate Booking
    ${id}=    Create Booking    ${payload}
    Booking Should Be    ${id}    ${payload}
    [Teardown]    Delete Booking If Exists    ${id}

Full Update Replaces All Fields
    ${original}=    Generate Booking
    ${id}=    Create Booking    ${original}
    ${updated}=    Generate Booking    additionalneeds=Airport transfer
    ${response}=    Update Booking    ${id}    ${updated}
    Dictionaries Should Be Equal    ${response.json()}    ${updated}
    Booking Should Be    ${id}    ${updated}
    [Teardown]    Delete Booking If Exists    ${id}

Partial Update Changes Only Given Fields
    ${payload}=    Generate Booking
    ${id}=    Create Booking    ${payload}
    &{changes}=    Create Dictionary    totalprice=${999}    additionalneeds=Late checkout
    Patch Booking    ${id}    ${changes}
    ${expected}=    Evaluate    {**$payload, **$changes}
    Booking Should Be    ${id}    ${expected}
    [Teardown]    Delete Booking If Exists    ${id}

Update Without Valid Token Is Forbidden
    [Template]    Update With Token Should Be Forbidden
    ${EMPTY}
    not-a-real-token

Deleted Booking Is No Longer Available
    ${payload}=    Generate Booking
    ${id}=    Create Booking    ${payload}
    Delete Booking    ${id}
    Booking Should Not Exist    ${id}


*** Keywords ***
Update With Token Should Be Forbidden
    [Arguments]    ${token}
    ${payload}=    Generate Booking
    ${id}=    Create Booking    ${payload}
    &{changes}=    Create Dictionary    firstname=Hacker
    Patch Booking    ${id}    ${changes}    token=${token}    expected_status=403
    Booking Should Be    ${id}    ${payload}
    [Teardown]    Delete Booking If Exists    ${id}
