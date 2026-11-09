*** Settings ***
Documentation       Authentication scenarios for the Sauce Demo shop.
Resource            ../../resources/ui/login_page.resource
Resource            ../../resources/ui/inventory_page.resource
Suite Setup         Open Shop
Suite Teardown      Close All Browsers
Test Setup          Go To Login Page
Test Tags           ui


*** Test Cases ***
Standard User Can Log In
    [Tags]    smoke
    Log In As    ${STANDARD_USER}    ${SHOP_PASSWORD}
    Inventory Page Should Be Open

Locked Out User Sees Explanation
    Log In As    ${LOCKED_USER}    ${SHOP_PASSWORD}
    Login Error Should Be    Epic sadface: Sorry, this user has been locked out.

Invalid Credentials Are Rejected
    [Template]    Login Should Fail With
    ${EMPTY}             ${SHOP_PASSWORD}    Epic sadface: Username is required
    ${STANDARD_USER}     ${EMPTY}            Epic sadface: Password is required
    ${STANDARD_USER}     wrong_password      Epic sadface: Username and password do not match any user in this service
    unknown_user         ${SHOP_PASSWORD}    Epic sadface: Username and password do not match any user in this service


*** Keywords ***
Login Should Fail With
    [Arguments]    ${username}    ${password}    ${expected_error}
    Go To Login Page
    Log In As    ${username}    ${password}
    Login Error Should Be    ${expected_error}
