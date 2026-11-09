INSERT INTO ref.currency_rates (currency, rate_to_usd) VALUES
    ('USD', 1.0000),
    ('EUR', 1.0800),
    ('GBP', 1.2700);

-- Each "dirty" row exercises one validation rule of the pipeline (see expected reasons in the tests).
INSERT INTO staging.orders_raw (order_id, customer_email, country, amount, currency, order_ts, status) VALUES
    ('1',  '  Alice@Example.com ', 'us',  '120.50', 'USD', '2026-10-01 10:00:00', 'PAID'),
    ('2',  'bob@example.com',      'DE',  '99,90',  'EUR', '2026-10-02 11:30:00', 'paid'),
    ('2',  'bob@example.com',      'DE',  '109,90', 'EUR', '2026-10-04 08:00:00', 'shipped'),  -- newer duplicate wins
    ('3',  'carol@example.com',    'gb',  '45.00',  'GBP', '2026-10-03 09:15:00', 'paid'),
    ('4',  'dave.example.com',     'US',  '30.00',  'USD', '2026-10-03 12:00:00', 'paid'),     -- invalid_email
    ('5',  'erin@example.com',     'FR',  '-10.00', 'EUR', '2026-10-04 13:00:00', 'paid'),     -- negative_amount
    ('6',  'frank@example.com',    'US',  'abc',    'USD', '2026-10-04 14:00:00', 'paid'),     -- invalid_amount
    ('7',  'grace@example.com',    'JP',  '5000',   'JPY', '2026-10-05 09:00:00', 'paid'),     -- unknown_currency
    ('8',  'heidi@example.com',    'US',  '15.00',  'USD', '2026-10-05 10:00:00', 'refunded'), -- invalid_status
    ('10', 'ivan@example.com',     'KZ',  '300',    'USD', '2026-10-06 12:00:00', 'Cancelled'),
    ('11', 'judy@example.com',     'USA', '10',     'USD', '2026-10-06 13:00:00', 'paid'),     -- invalid_country
    ('12', NULL,                   'US',  '10',     'USD', '2026-10-06 14:00:00', 'paid'),     -- invalid_email
    ('13', 'kate@example.com',     'ca',  '20.00',  'usd', '2026-10-07 08:00:00', 'shipped'),
    ('14', 'leo@example.com',      'US',  '50',     'USD', '2099-01-01 00:00:00', 'paid'),     -- future_date
    ('15', 'mia@example.com',      'PL',  '250.00', 'EUR', 'not-a-date',          'paid'),     -- invalid_date
    ('A1', 'nick@example.com',     'US',  '5.00',   'USD', '2026-10-08 08:00:00', 'paid');     -- invalid_order_id
