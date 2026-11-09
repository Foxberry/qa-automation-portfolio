import pytest

from framework import config

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_valid_credentials_return_token(client):
    response = client.authenticate(config.BOOKER_USER, config.BOOKER_PASSWORD)

    assert response.status_code == 200
    assert response.json()["token"]


@pytest.mark.parametrize(
    "username, password",
    [
        pytest.param(config.BOOKER_USER, "wrong-password", id="wrong-password"),
        pytest.param("unknown-user", config.BOOKER_PASSWORD, id="unknown-user"),
        pytest.param("", "", id="empty-credentials"),
    ],
)
def test_invalid_credentials_are_rejected(client, username, password):
    response = client.authenticate(username, password)

    # The API reports bad credentials with HTTP 200 and a reason instead of 401 (documented behaviour).
    assert response.status_code == 200
    assert response.json() == {"reason": "Bad credentials"}
