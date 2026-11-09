"""Custom Robot Framework keywords for booking test data and contract checks."""
from jsonschema import ValidationError, validate
from robot.api import logger
from robot.api.deco import keyword, library

from framework.test_data import BOOKING_SCHEMA, CREATED_BOOKING_SCHEMA, make_booking

SCHEMAS = {"booking": BOOKING_SCHEMA, "created booking": CREATED_BOOKING_SCHEMA}


@library(scope="GLOBAL", auto_keywords=False)
class BookingKeywords:
    @keyword
    def generate_booking(self, **overrides):
        """Returns a valid booking payload with unique names. Top-level fields can be overridden.

        Example: ``${payload}=    Generate Booking    totalprice=${100}``
        """
        payload = make_booking(**overrides)
        logger.info(f"Generated booking: {payload}")
        return payload

    @keyword
    def response_should_match_schema(self, body, schema_name: str):
        """Fails with a readable message if ``body`` does not match the named JSON schema."""
        try:
            validate(body, SCHEMAS[schema_name.lower()])
        except ValidationError as exc:
            path = "/".join(str(p) for p in exc.absolute_path) or "<root>"
            raise AssertionError(f"Schema '{schema_name}' violated at {path}: {exc.message}") from None
