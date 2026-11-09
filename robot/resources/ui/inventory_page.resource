*** Settings ***
Documentation       Page object: product list and cart badge.
Resource            common.resource
Library             Collections


*** Variables ***
${PAGE_TITLE}       css:[data-test="title"]
${SORT_SELECT}      css:[data-test="product-sort-container"]
${ITEM_PRICES}      css:[data-test="inventory-item-price"]
${CART_BADGE}       css:[data-test="shopping-cart-badge"]
${CART_LINK}        css:[data-test="shopping-cart-link"]


*** Keywords ***
Inventory Page Should Be Open
    Wait Until Element Is Visible    ${PAGE_TITLE}
    Element Text Should Be    ${PAGE_TITLE}    Products

Add Product To Cart
    [Arguments]    ${product_slug}
    Click Button    css:[data-test="add-to-cart-${product_slug}"]

Cart Badge Should Show
    [Arguments]    ${count}
    Element Text Should Be    ${CART_BADGE}    ${count}

Sort Products By
    [Arguments]    ${option_label}
    Select From List By Label    ${SORT_SELECT}    ${option_label}

Get Product Prices
    ${elements}=    Get WebElements    ${ITEM_PRICES}
    ${prices}=    Evaluate    [float(e.text.lstrip('$')) for e in $elements]
    RETURN    ${prices}

Open Cart
    Click Element    ${CART_LINK}
