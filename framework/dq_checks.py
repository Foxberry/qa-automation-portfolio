"""Reusable data-quality queries. Each returns the offending rows, so an empty list means "check passed"."""
from __future__ import annotations

from framework import db


def duplicate_keys(table: str, key: str) -> list[tuple]:
    return db.query(f"SELECT {key}, COUNT(*) FROM {table} GROUP BY {key} HAVING COUNT(*) > 1")


def null_values(table: str, columns: list[str]) -> list[tuple]:
    condition = " OR ".join(f"{col} IS NULL" for col in columns)
    return db.query(f"SELECT * FROM {table} WHERE {condition}")


def source_target_reconciliation() -> dict:
    """Every distinct source order must end up either loaded or rejected — nothing lost, nothing invented."""
    return {
        "source_distinct": db.scalar("SELECT COUNT(DISTINCT order_id) FROM staging.orders_raw"),
        "loaded": db.scalar("SELECT COUNT(*) FROM dwh.fact_orders"),
        "rejected": db.scalar("SELECT COUNT(*) FROM dwh.rejected_orders"),
    }


def amount_mismatches() -> list[tuple]:
    """Recompute amount_usd in SQL, independently of the Python pipeline, and compare."""
    return db.query(
        """
        WITH latest AS (
            SELECT DISTINCT ON (order_id) *
            FROM staging.orders_raw
            ORDER BY order_id, order_ts DESC
        )
        SELECT f.order_id, f.amount_usd,
               ROUND(REPLACE(TRIM(l.amount), ',', '.')::numeric * r.rate_to_usd, 2) AS expected
        FROM dwh.fact_orders f
        JOIN latest l ON l.order_id = f.order_id::text
        JOIN ref.currency_rates r ON r.currency = UPPER(TRIM(l.currency))
        WHERE f.amount_usd <> ROUND(REPLACE(TRIM(l.amount), ',', '.')::numeric * r.rate_to_usd, 2)
        """
    )


def non_normalised_emails() -> list[tuple]:
    return db.query("SELECT order_id, customer_email FROM dwh.fact_orders WHERE customer_email <> LOWER(TRIM(customer_email))")


def rejection_reasons() -> dict[str, str]:
    return dict(db.query("SELECT order_id, reason FROM dwh.rejected_orders"))
