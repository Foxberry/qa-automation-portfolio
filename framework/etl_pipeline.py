"""Small ETL job used as the system under test for the data-quality suites.

Loads staging.orders_raw into dwh.fact_orders:
  * keeps only the latest version of each order (by order_ts);
  * normalises email, country, currency and status;
  * converts the amount to USD using ref.currency_rates;
  * writes every row that fails validation to dwh.rejected_orders with a reason.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

from framework import db

SQL_DIR = Path(__file__).resolve().parent.parent / "etl" / "sql"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ALLOWED_STATUSES = {"paid", "shipped", "cancelled"}
COLUMNS = ("order_id", "customer_email", "country", "amount", "currency", "order_ts", "status")


class Rejected(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass
class PipelineResult:
    source_rows: int = 0
    duplicates_dropped: int = 0
    loaded: list[dict] = field(default_factory=list)
    rejected: list[tuple[str | None, str, dict]] = field(default_factory=list)


def prepare_database() -> None:
    """Recreate schemas and load the reference and staging seed data."""
    for script in sorted(SQL_DIR.glob("*.sql")):
        db.run_script(script)


def transform(raw: dict, rates: dict[str, Decimal], today: date) -> dict:
    try:
        order_id = int((raw["order_id"] or "").strip())
    except ValueError:
        raise Rejected("invalid_order_id")

    email = (raw["customer_email"] or "").strip().lower()
    if not EMAIL_RE.match(email):
        raise Rejected("invalid_email")

    country = (raw["country"] or "").strip().upper()
    if not (len(country) == 2 and country.isalpha()):
        raise Rejected("invalid_country")

    try:
        amount = Decimal((raw["amount"] or "").strip().replace(",", "."))
    except InvalidOperation:
        raise Rejected("invalid_amount")
    if amount < 0:
        raise Rejected("negative_amount")

    currency = (raw["currency"] or "").strip().upper()
    if currency not in rates:
        raise Rejected("unknown_currency")

    try:
        order_date = datetime.fromisoformat((raw["order_ts"] or "").strip()).date()
    except ValueError:
        raise Rejected("invalid_date")
    if order_date > today:
        raise Rejected("future_date")

    status = (raw["status"] or "").strip().lower()
    if status not in ALLOWED_STATUSES:
        raise Rejected("invalid_status")

    return {
        "order_id": order_id,
        "customer_email": email,
        "country": country,
        "amount_usd": (amount * rates[currency]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "order_date": order_date,
        "status": status,
    }


def run_pipeline(today: date | None = None) -> PipelineResult:
    today = today or date.today()
    result = PipelineResult()
    rates = {cur.strip(): rate for cur, rate in db.query("SELECT currency, rate_to_usd FROM ref.currency_rates")}
    raw_rows = [dict(zip(COLUMNS, row)) for row in db.query(f"SELECT {', '.join(COLUMNS)} FROM staging.orders_raw")]
    result.source_rows = len(raw_rows)

    latest: dict[str | None, dict] = {}
    for row in raw_rows:
        current = latest.get(row["order_id"])
        if current is None or (row["order_ts"] or "") > (current["order_ts"] or ""):
            latest[row["order_id"]] = row
    result.duplicates_dropped = len(raw_rows) - len(latest)

    for raw in latest.values():
        try:
            result.loaded.append(transform(raw, rates, today))
        except Rejected as exc:
            result.rejected.append((raw["order_id"], exc.reason, raw))

    with db.connection() as conn, conn.transaction():
        conn.execute("TRUNCATE dwh.fact_orders, dwh.rejected_orders")
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO dwh.fact_orders (order_id, customer_email, country, amount_usd, order_date, status) "
                "VALUES (%(order_id)s, %(customer_email)s, %(country)s, %(amount_usd)s, %(order_date)s, %(status)s)",
                result.loaded,
            )
            cur.executemany(
                "INSERT INTO dwh.rejected_orders (order_id, reason, raw_row) VALUES (%s, %s, %s)",
                [(order_id, reason, json.dumps(raw)) for order_id, reason, raw in result.rejected],
            )
    return result
