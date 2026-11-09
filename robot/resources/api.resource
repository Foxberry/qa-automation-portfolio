*** Settings ***
Documentation       Business-level keywords for the Restful-Booker API built on RequestsLibrary.
Library             RequestsLibrary
Library             Collections
Library             ../libraries/BookingKeywords.py
Variables           framework.config


*** Keywords ***
Open Booker Session
    &{headers}=    Create Dictionary    Accept=application/json    Content-Type=application/json
    Create Session    booker    ${BOOKER_URL}    headers=${headers}    timeout=${HTTP_TIMEOUT}    max_retries=2    verify=${True}

Authenticate As Admin
    ${token}=    Get Auth Token    ${BOOKER_USER}    ${BOOKER_PASSWORD}
    Set Suite Variable    ${TOKEN}    ${token}

Get Auth Token
    [Arguments]    ${username}    ${password}
    &{body}=    Create Dictionary    username=${username}    password=${password}
    ${response}=    POST On Session    booker    /auth    json=${body}
    Dictionary Should Contain Key    ${response.json()}    token    msg=Authentication failed: ${response.text}
    RETURN    ${response.json()}[token]

Create Booking
    [Arguments]    ${payload}
    ${response}=    POST On Session    booker    /booking    json=${payload}
    Response Should Match Schema    ${response.json()}    created booking
    Dictionaries Should Be Equal    ${response.json()}[booking]    ${payload}
    RETURN    ${response.json()}[bookingid]

Booking Should Be
    [Arguments]    ${booking_id}    ${expected}
    ${response}=    GET On Session    booker    /booking/${booking_id}
    Response Should Match Schema    ${response.json()}    booking
    Dictionaries Should Be Equal    ${response.json()}    ${expected}

Booking Should Not Exist
    [Arguments]    ${booking_id}
    GET On Session    booker    /booking/${booking_id}    expected_status=404

Update Booking
    [Arguments]    ${booking_id}    ${payload}    ${token}=${TOKEN}    ${expected_status}=200
    &{headers}=    Create Dictionary    Cookie=token=${token}
    ${response}=    PUT On Session    booker    /booking/${booking_id}
    ...    json=${payload}    headers=${headers}    expected_status=${expected_status}
    RETURN    ${response}

Patch Booking
    [Arguments]    ${booking_id}    ${fields}    ${token}=${TOKEN}    ${expected_status}=200
    &{headers}=    Create Dictionary    Cookie=token=${token}
    ${response}=    PATCH On Session    booker    /booking/${booking_id}
    ...    json=${fields}    headers=${headers}    expected_status=${expected_status}
    RETURN    ${response}

Delete Booking
    [Arguments]    ${booking_id}
    &{headers}=    Create Dictionary    Cookie=token=${TOKEN}
    # The API answers 201 Created on a successful delete.
    DELETE On Session    booker    /booking/${booking_id}    headers=${headers}    expected_status=201

Delete Booking If Exists
    [Arguments]    ${booking_id}
    &{headers}=    Create Dictionary    Cookie=token=${TOKEN}
    DELETE On Session    booker    /booking/${booking_id}    headers=${headers}    expected_status=any
