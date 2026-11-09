*** Settings ***
Documentation       Browser lifecycle for the Sauce Demo UI suites.
Library             SeleniumLibrary    timeout=10s    implicit_wait=5s    run_on_failure=Capture Page Screenshot


*** Variables ***
${SHOP_URL}         https://www.saucedemo.com
${BROWSER}          headlesschrome
# Public demo accounts listed on the Sauce Demo login page.
${STANDARD_USER}    standard_user
${LOCKED_USER}      locked_out_user
${SHOP_PASSWORD}    secret_sauce
# Chrome's password-leak popup blocks clicks on this site, so the password manager is switched off.
${CHROME_OPTIONS}
...                 add_argument("--window-size=1920,1080");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "profile.password_manager_leak_detection": False})


*** Keywords ***
Open Shop
    Open Browser    ${SHOP_URL}    ${BROWSER}    options=${CHROME_OPTIONS}

Go To Login Page
    Go To    ${SHOP_URL}
    Delete All Cookies
    Execute Javascript    window.localStorage.clear()
    Reload Page
