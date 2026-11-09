*** Settings ***
Documentation       Page objects: cart, checkout information, overview and confirmation.
Resource            common.resource


*** Variables ***
${CHECKOUT_BUTTON}      css:[data-test="checkout"]
${FIRST_NAME_INPUT}     css:[data-test="firstName"]
${LAST_NAME_INPUT}      css:[data-test="lastName"]
${POSTAL_CODE_INPUT}    css:[data-test="postalCode"]
${CONTINUE_BUTTON}      css:[data-test="continue"]
${FINISH_BUTTON}        css:[data-test="finish"]
${CART_ITEM_PRICES}     css:[data-test="inventory-item-price"]
${SUBTOTAL_LABEL}       css:[data-test="subtotal-label"]
${TAX_LABEL}            css:[data-test="tax-label"]
${TOTAL_LABEL}          css:[data-test="total-label"]
${COMPLETE_HEADER}      css:[data-test="complete-header"]


*** Keywords ***
Start Checkout
    Click Button    ${CHECKOUT_BUTTON}

Fill Customer Information
    [Arguments]    ${first_name}    ${last_name}    ${postal_code}
    Input Text    ${FIRST_NAME_INPUT}    ${first_name}
    Input Text    ${LAST_NAME_INPUT}    ${last_name}
    Input Text    ${POSTAL_CODE_INPUT}    ${postal_code}
    Click Button    ${CONTINUE_BUTTON}

Order Totals Should Be Consistent
    [Documentation]    Item total equals the sum of line prices, and total equals item total plus tax.
    ${elements}=    Get WebElements    ${CART_ITEM_PRICES}
    ${lines_sum}=    Evaluate    round(sum(float(e.text.lstrip('$')) for e in $elements), 2)
    ${subtotal}=    Get Amount From Label    ${SUBTOTAL_LABEL}
    ${tax}=    Get Amount From Label    ${TAX_LABEL}
    ${total}=    Get Amount From Label    ${TOTAL_LABEL}
    Should Be Equal As Numbers    ${subtotal}    ${lines_sum}
    Should Be Equal As Numbers    ${total}    ${{ $subtotal + $tax }}    precision=2

Get Amount From Label
    [Arguments]    ${locator}
    ${text}=    Get Text    ${locator}
    ${amount}=    Evaluate    float($text.split('$')[-1])
    RETURN    ${amount}

Finish Order
    Click Button    ${FINISH_BUTTON}

Order Should Be Confirmed
    Element Text Should Be    ${COMPLETE_HEADER}    Thank you for your order!
