import pytest
from jsonschema import validate

from framework.test_data import BOOKING_SCHEMA, CREATED_BOOKING_SCHEMA, make_booking

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_create_booking_returns_submitted_data(client, token):
    payload = make_booking()

    response = client.create_booking(payload)

    assert response.status_code == 200
    body = response.json()
    validate(body, CREATED_BOOKING_SCHEMA)
    assert body["booking"] == payload
    client.delete_booking(body["bookingid"], token)


def test_get_booking_matches_created(client, booking):
    booking_id, payload = booking

    response = client.get_booking(booking_id)

    assert response.status_code == 200
    validate(response.json(), BOOKING_SCHEMA)
    assert response.json() == payload


def test_search_by_name_finds_booking(client, booking):
    booking_id, payload = booking

    response = client.find_bookings(firstname=payload["firstname"], lastname=payload["lastname"])

    assert response.status_code == 200
    assert {"bookingid": booking_id} in response.json()


def test_full_update_replaces_booking(client, token, booking):
    booking_id, _ = booking
    new_payload = make_booking(additionalneeds="Airport transfer")

    response = client.update_booking(booking_id, new_payload, token)

    assert response.status_code == 200
    assert response.json() == new_payload
    assert client.get_booking(booking_id).json() == new_payload


def test_partial_update_changes_only_given_fields(client, token, booking):
    booking_id, payload = booking
    changes = {"totalprice": payload["totalprice"] + 100, "depositpaid": not payload["depositpaid"]}

    response = client.partial_update_booking(booking_id, changes, token)

    assert response.status_code == 200
    assert response.json() == {**payload, **changes}


@pytest.mark.parametrize("bad_token", [None, "not-a-real-token"], ids=["no-token", "invalid-token"])
def test_update_requires_valid_token(client, booking, bad_token):
    booking_id, payload = booking

    response = client.partial_update_booking(booking_id, {"firstname": "Hacker"}, bad_token)

    assert response.status_code == 403
    assert client.get_booking(booking_id).json()["firstname"] == payload["firstname"]


def test_deleted_booking_is_not_found(client, token):
    booking_id = client.create_booking(make_booking()).json()["bookingid"]

    response = client.delete_booking(booking_id, token)

    # Restful-Booker answers 201 Created on delete; we pin the real contract rather than an assumed one.
    assert response.status_code == 201
    assert client.get_booking(booking_id).status_code == 404


def test_get_unknown_booking_returns_404(client):
    assert client.get_booking(999_999_999).status_code == 404
