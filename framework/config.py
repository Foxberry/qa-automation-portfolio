"""Environment-driven settings. Defaults point at the public demo services and the local Docker DB."""
import os

BOOKER_URL = os.getenv("BOOKER_URL", "https://restful-booker.herokuapp.com")
# Public demo credentials published in the Restful-Booker documentation.
BOOKER_USER = os.getenv("BOOKER_USER", "admin")
BOOKER_PASSWORD = os.getenv("BOOKER_PASSWORD", "password123")

PG_DSN = os.getenv(
    "PG_DSN",
    "host={host} port={port} dbname={db} user={user} password={password}".format(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5433"),
        db=os.getenv("PG_DB", "dwh"),
        user=os.getenv("PG_USER", "qa"),
        password=os.getenv("PG_PASSWORD", "qa"),
    ),
)

HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "20"))
