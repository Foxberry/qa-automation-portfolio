from decimal import Decimal

import pytest

from framework import db, dq_checks

pytestmark = pytest.mark.etl

EXPECTED_REJECTIONS = {
    "4": "invalid_email",
    "5": "negative_amount",
    "6": "invalid_amount",
    "7": "unknown_currency",
    "8": "invalid_status",
    "11": "invalid_country",
    "12": "invalid_email",
    "14": "future_date",
    "15": "invalid_date",
    "A1": "invalid_order_id",
}


@pytest.mark.smoke
def test_every_source_order_is_loaded_or_rejected(etl_run):
    counts = dq_checks.source_target_reconciliation()

    assert counts["loaded"] + counts["rejected"] == counts["source_distinct"], counts


def test_duplicates_keep_latest_version(etl_run):
    assert etl_run.duplicates_dropped == 1
    assert dq_checks.duplicate_keys("dwh.fact_orders", "order_id") == []
    assert db.scalar("SELECT status FROM dwh.fact_orders WHERE order_id = 2") == "shipped"


def test_mandatory_columns_are_filled(etl_run):
    columns = ["order_id", "customer_email", "country", "amount_usd", "order_date", "status"]

    assert dq_checks.null_values("dwh.fact_orders", columns) == []


def test_amounts_match_independent_sql_calculation(etl_run):
    assert dq_checks.amount_mismatches() == []


@pytest.mark.parametrize(
    "order_id, expected_usd",
    [(1, "120.50"), (2, "118.69"), (3, "57.15"), (13, "20.00")],
)
def test_currency_conversion(etl_run, order_id, expected_usd):
    assert db.scalar("SELECT amount_usd FROM dwh.fact_orders WHERE order_id = %s", (order_id,)) == Decimal(expected_usd)


def test_values_are_normalised(etl_run):
    assert dq_checks.non_normalised_emails() == []
    assert db.query("SELECT order_id FROM dwh.fact_orders WHERE country <> UPPER(country)") == []
    assert {row[0] for row in db.query("SELECT DISTINCT status FROM dwh.fact_orders")} <= {"paid", "shipped", "cancelled"}


def test_no_orders_from_the_future(etl_run):
    assert db.query("SELECT order_id FROM dwh.fact_orders WHERE order_date > CURRENT_DATE") == []


def test_invalid_rows_are_rejected_with_reason(etl_run):
    assert dq_checks.rejection_reasons() == EXPECTED_REJECTIONS
