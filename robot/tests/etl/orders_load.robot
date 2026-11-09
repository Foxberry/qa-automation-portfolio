*** Settings ***
Documentation       Data-quality checks for the staging → DWH orders load.
...                 Requires PostgreSQL (``docker compose up -d``).
Library             Collections
Library             ../../libraries/EtlKeywords.py
Suite Setup         Run Keywords    Prepare Orders Database    AND    Run Orders Pipeline
Test Tags           etl


*** Variables ***
&{EXPECTED_REJECTIONS}
...    4=invalid_email    5=negative_amount    6=invalid_amount    7=unknown_currency
...    8=invalid_status    11=invalid_country    12=invalid_email    14=future_date
...    15=invalid_date    A1=invalid_order_id


*** Test Cases ***
Every Source Order Is Loaded Or Rejected
    [Tags]    smoke
    Source And Target Should Reconcile

Fact Table Has No Duplicate Orders
    Query Should Return No Rows
    ...    SELECT order_id FROM dwh.fact_orders GROUP BY order_id HAVING COUNT(*) > 1

Latest Version Of A Duplicated Order Wins
    ${status}=    Query Value    SELECT status FROM dwh.fact_orders WHERE order_id = 2
    Should Be Equal    ${status}    shipped

Mandatory Columns Are Filled
    ${sql}=    Catenate
    ...    SELECT * FROM dwh.fact_orders
    ...    WHERE customer_email IS NULL OR country IS NULL OR amount_usd IS NULL
    ...    OR order_date IS NULL OR status IS NULL
    Query Should Return No Rows    ${sql}

Amounts Match Independent SQL Calculation
    Amounts Should Match Independent Calculation

Values Are Normalised
    [Template]    Query Should Return No Rows
    SELECT order_id FROM dwh.fact_orders WHERE customer_email <> LOWER(TRIM(customer_email))
    SELECT order_id FROM dwh.fact_orders WHERE country <> UPPER(country)
    SELECT order_id FROM dwh.fact_orders WHERE status NOT IN ('paid', 'shipped', 'cancelled')

No Orders From The Future
    Query Should Return No Rows    SELECT order_id FROM dwh.fact_orders WHERE order_date > CURRENT_DATE

Invalid Rows Are Rejected With Expected Reason
    ${actual}=    Get Rejection Reasons
    Dictionaries Should Be Equal    ${actual}    ${EXPECTED_REJECTIONS}
