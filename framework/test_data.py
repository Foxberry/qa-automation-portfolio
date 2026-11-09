"""Test data builders and JSON schemas for the booking API."""
from __future__ import annotations

import copy
import random
import uuid
from datetime import date, timedelta

BOOKING_SCHEMA = {
    "type": "object",
    "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
    "properties": {
        "firstname": {"type": "string", "minLength": 1},
        "lastname": {"type": "string", "minLength": 1},
        "totalprice": {"type": "integer", "minimum": 0},
        "depositpaid": {"type": "boolean"},
        "bookingdates": {
            "type": "object",
            "required": ["checkin", "checkout"],
            "properties": {
                "checkin": {"type": "string", "format": "date"},
                "checkout": {"type": "string", "format": "date"},
            },
        },
        "additionalneeds": {"type": "string"},
    },
}

CREATED_BOOKING_SCHEMA = {
    "type": "object",
    "required": ["bookingid", "booking"],
    "properties": {"bookingid": {"type": "integer"}, "booking": BOOKING_SCHEMA},
}


def unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def make_booking(**overrides) -> dict:
    """Build a valid booking payload with unique names so parallel runs don't collide."""
    checkin = date.today() + timedelta(days=random.randint(10, 60))
    booking = {
        "firstname": f"Anna{unique_suffix()}",
        "lastname": f"QA{unique_suffix()}",
        "totalprice": random.randint(50, 900),
        "depositpaid": random.choice([True, False]),
        "bookingdates": {
            "checkin": checkin.isoformat(),
            "checkout": (checkin + timedelta(days=random.randint(1, 14))).isoformat(),
        },
        "additionalneeds": random.choice(["Breakfast", "Late checkout", "Parking"]),
    }
    return deep_merge(booking, overrides)


def deep_merge(base: dict, overrides: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
