import pytest

from framework.booking_client import BookingClient
from framework.etl_pipeline import prepare_database, run_pipeline
from framework.test_data import make_booking


@pytest.fixture(scope="session")
def client() -> BookingClient:
    return BookingClient()


@pytest.fixture(scope="session")
def token(client: BookingClient) -> str:
    return client.get_token()


@pytest.fixture
def booking(client: BookingClient, token: str):
    """A freshly created booking, removed after the test whatever its outcome."""
    payload = make_booking()
    response = client.create_booking(payload)
    assert response.status_code == 200, response.text
    booking_id = response.json()["bookingid"]
    yield booking_id, payload
    client.delete_booking(booking_id, token)


@pytest.fixture(scope="session")
def etl_run():
    prepare_database()
    return run_pipeline()
