"""Thin HTTP client for the Restful-Booker demo API (https://restful-booker.herokuapp.com/apidoc)."""
from __future__ import annotations

import requests

from framework import config


class BookingClient:
    def __init__(self, base_url: str = config.BOOKER_URL, timeout: float = config.HTTP_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        # Restful-Booker answers 418 to POST requests without an explicit JSON Accept header.
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    def _request(self, method: str, path: str, token: str | None = None, **kwargs) -> requests.Response:
        headers = kwargs.pop("headers", {})
        if token:
            headers["Cookie"] = f"token={token}"
        return self.session.request(
            method, f"{self.base_url}{path}", headers=headers, timeout=self.timeout, **kwargs
        )

    def authenticate(self, username: str, password: str) -> requests.Response:
        return self._request("POST", "/auth", json={"username": username, "password": password})

    def get_token(self, username: str = config.BOOKER_USER, password: str = config.BOOKER_PASSWORD) -> str:
        response = self.authenticate(username, password)
        response.raise_for_status()
        token = response.json().get("token")
        if not token:
            raise RuntimeError(f"Authentication failed: {response.text}")
        return token

    def create_booking(self, payload: dict) -> requests.Response:
        return self._request("POST", "/booking", json=payload)

    def get_booking(self, booking_id: int) -> requests.Response:
        return self._request("GET", f"/booking/{booking_id}")

    def find_bookings(self, **filters) -> requests.Response:
        return self._request("GET", "/booking", params=filters)

    def update_booking(self, booking_id: int, payload: dict, token: str | None) -> requests.Response:
        return self._request("PUT", f"/booking/{booking_id}", json=payload, token=token)

    def partial_update_booking(self, booking_id: int, fields: dict, token: str | None) -> requests.Response:
        return self._request("PATCH", f"/booking/{booking_id}", json=fields, token=token)

    def delete_booking(self, booking_id: int, token: str | None) -> requests.Response:
        return self._request("DELETE", f"/booking/{booking_id}", token=token)
