"""Robot Framework keywords for ETL runs and data-quality checks against PostgreSQL."""
from robot.api import logger
from robot.api.deco import keyword, library

from framework import db, dq_checks
from framework.etl_pipeline import prepare_database, run_pipeline


@library(scope="SUITE", auto_keywords=False)
class EtlKeywords:
    def __init__(self):
        self.last_run = None

    @keyword
    def prepare_orders_database(self):
        """Recreates schemas and loads seed data into staging and reference tables."""
        prepare_database()

    @keyword
    def run_orders_pipeline(self):
        self.last_run = run_pipeline()
        logger.info(
            f"Source rows: {self.last_run.source_rows}, loaded: {len(self.last_run.loaded)}, "
            f"rejected: {len(self.last_run.rejected)}, duplicates dropped: {self.last_run.duplicates_dropped}"
        )
        return self.last_run

    @keyword
    def query_should_return_no_rows(self, sql: str):
        rows = db.query(sql)
        if rows:
            raise AssertionError(f"Expected no rows, got {len(rows)}:\n" + "\n".join(map(str, rows[:20])))

    @keyword
    def query_value(self, sql: str):
        return db.scalar(sql)

    @keyword
    def source_and_target_should_reconcile(self):
        counts = dq_checks.source_target_reconciliation()
        logger.info(f"Reconciliation: {counts}")
        if counts["loaded"] + counts["rejected"] != counts["source_distinct"]:
            raise AssertionError(f"Rows lost or invented during load: {counts}")

    @keyword
    def amounts_should_match_independent_calculation(self):
        mismatches = dq_checks.amount_mismatches()
        if mismatches:
            raise AssertionError(f"amount_usd differs from SQL recalculation: {mismatches}")

    @keyword
    def get_rejection_reasons(self):
        return dq_checks.rejection_reasons()
