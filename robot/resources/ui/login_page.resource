*** Settings ***
Documentation       Page object: login page.
Resource            common.resource


*** Variables ***
${USERNAME_INPUT}       id:user-name
${PASSWORD_INPUT}       id:password
${LOGIN_BUTTON}         id:login-button
${ERROR_MESSAGE}        css:[data-test="error"]


*** Keywords ***
Log In As
    [Arguments]    ${username}    ${password}
    Input Text    ${USERNAME_INPUT}    ${username}
    Input Password    ${PASSWORD_INPUT}    ${password}
    Click Button    ${LOGIN_BUTTON}

Login Error Should Be
    [Arguments]    ${expected}
    Element Text Should Be    ${ERROR_MESSAGE}    ${expected}
