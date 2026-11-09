-- Recreated on every test run so the suites are idempotent.
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS ref CASCADE;
DROP SCHEMA IF EXISTS dwh CASCADE;

CREATE SCHEMA staging;
CREATE SCHEMA ref;
CREATE SCHEMA dwh;

-- Raw export from an upstream system: everything is text, nothing is validated.
CREATE TABLE staging.orders_raw (
    order_id        TEXT,
    customer_email  TEXT,
    country         TEXT,
    amount          TEXT,
    currency        TEXT,
    order_ts        TEXT,
    status          TEXT
);

CREATE TABLE ref.currency_rates (
    currency     CHAR(3) PRIMARY KEY,
    rate_to_usd  NUMERIC(10, 4) NOT NULL CHECK (rate_to_usd > 0)
);

CREATE TABLE dwh.fact_orders (
    order_id        INTEGER PRIMARY KEY,
    customer_email  TEXT          NOT NULL,
    country         CHAR(2)       NOT NULL,
    amount_usd      NUMERIC(12, 2) NOT NULL,
    order_date      DATE          NOT NULL,
    status          TEXT          NOT NULL,
    loaded_at       TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE dwh.rejected_orders (
    order_id  TEXT,
    reason    TEXT NOT NULL,
    raw_row   JSONB NOT NULL
);
