*** Settings ***
Documentation       Catalogue and checkout flow for a logged-in customer.
Resource            ../../resources/ui/login_page.resource
Resource            ../../resources/ui/inventory_page.resource
Resource            ../../resources/ui/checkout_page.resource
Suite Setup         Open Shop
Suite Teardown      Close All Browsers
Test Setup          Log In As Standard User
Test Tags           ui


*** Test Cases ***
Customer Can Buy Two Products
    [Tags]    smoke    e2e
    Add Product To Cart    sauce-labs-backpack
    Add Product To Cart    sauce-labs-bolt-t-shirt
    Cart Badge Should Show    2
    Open Cart
    Start Checkout
    Fill Customer Information    Anna    Tester    644000
    Order Totals Should Be Consistent
    Finish Order
    Order Should Be Confirmed

Products Can Be Sorted By Price
    [Template]    Prices Should Be Sorted
    Price (low to high)    ${False}
    Price (high to low)    ${True}


*** Keywords ***
Log In As Standard User
    Go To Login Page
    Log In As    ${STANDARD_USER}    ${SHOP_PASSWORD}
    Inventory Page Should Be Open

Prices Should Be Sorted
    [Arguments]    ${option}    ${descending}
    Sort Products By    ${option}
    ${prices}=    Get Product Prices
    ${expected}=    Evaluate    sorted($prices, reverse=$descending)
    Lists Should Be Equal    ${prices}    ${expected}
