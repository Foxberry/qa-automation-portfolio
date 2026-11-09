# QA Automation Portfolio: Robot Framework + pytest

![tests](../../actions/workflows/tests.yml/badge.svg)

A compact but production-style test automation project that shows how I build test frameworks:
**API, UI and ETL/data-quality testing** with **Robot Framework and pytest sharing one Python core**,
running in **CI** (GitHub Actions and GitLab CI).

> Author: **Anna Egorova**, Lead QA Engineer with 20+ years in testing (QA leadership, automation
> architecture, data/ETL validation). My commercial work is under NDA, so this repository reproduces the same
> approaches on public demo systems.

## What is inside

| Area | System under test | Tools | What it demonstrates |
|------|-------------------|-------|----------------------|
| REST API | [Restful-Booker](https://restful-booker.herokuapp.com/apidoc/index.html) | pytest, requests, jsonschema / Robot Framework + RequestsLibrary | CRUD lifecycle, auth rules, contract (JSON Schema) checks, self-cleaning test data |
| Web UI | [Sauce Demo](https://www.saucedemo.com) | Robot Framework + SeleniumLibrary | Page Object resources, data-driven templates, end-to-end checkout with totals verification |
| ETL / data quality | Included orders pipeline, PostgreSQL in Docker | pytest / Robot Framework custom Python keywords, SQL | Source-to-target reconciliation, deduplication, independent SQL oracle, rejection reasons |
| CI | GitHub Actions, GitLab CI | Postgres service, artifacts, nightly schedule | Lint → parallel test jobs → HTML reports as artifacts |

## Architecture

```
framework/                 # shared Python core, used by BOTH runners
  booking_client.py        #   API client (one place for URLs, headers, auth)
  test_data.py             #   data builders + JSON schemas
  db.py, dq_checks.py      #   PostgreSQL helpers and reusable data-quality queries
  etl_pipeline.py          #   the ETL job under test
tests/                     # pytest suites (api/, etl/)
robot/
  libraries/               # custom keyword libraries written in Python
  resources/               # business-level keywords; ui/ holds page objects
  tests/                   # api/, ui/, etl/ suites
etl/sql/                   # schema + intentionally dirty seed data
```

Design decisions:

- **One core, two runners.** Clients, data builders and DQ queries live in `framework/`, so a pytest test and a
  Robot keyword never diverge in how they talk to the system.
- **Tests own their data.** Each API test creates a booking with unique names and deletes it in teardown, so the
  suite can run in parallel and against a shared environment.
- **Pin the real contract.** Restful-Booker returns `201` on delete and `200` for bad credentials; tests assert
  the actual documented behaviour and say so in a comment, instead of silently "fixing" expectations.
- **Independent oracle for data.** The ETL job is written in Python; the amount check recomputes the result in
  plain SQL. A bug in one implementation cannot hide itself.
- **Every dirty row is intentional.** Each bad record in `etl/sql/02_seed.sql` targets one validation rule, and
  the tests assert the exact rejection reason per row.

## Running locally

Requirements: Python 3.10+, Docker (for ETL tests), Google Chrome (for UI tests).

```bash
make install        # virtualenv + dependencies
make db-up          # PostgreSQL on localhost:5433
make all            # lint + pytest + all Robot suites
make smoke          # fast subset tagged "smoke"
```

Single suites: `make pytest`, `make robot-api`, `make robot-ui`, `make robot-etl`.
Reports appear in `results/` (`log.html` / `report.html` for Robot, JUnit XML for pytest).

Configuration is environment-driven (`framework/config.py`): `BOOKER_URL`, `PG_HOST`, `PG_PORT`, etc.
For UI tests pass `--variable BROWSER:chrome` to watch the browser instead of running headless.

## Coverage summary

- **pytest:** 13 API tests, 11 ETL tests
- **Robot Framework:** 5 API tests, 5 UI tests (with data-driven templates), 8 ETL tests

## Possible next steps

- Allure reporting and publishing reports to GitHub Pages
- Parallel Robot runs with `pabot`
- Testing LLM-powered features (response format, grounding, regression on a golden set)
