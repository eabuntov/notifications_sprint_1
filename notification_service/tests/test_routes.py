from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Adjust import according to your project structure
from notification_api.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    TestClient intended to be used inside Docker.
    Assumes the app uses a test database configured via environment variables.
    """
    return TestClient(app)


def _assert_notification_response(resp):
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "notification_id" in body
    assert body["notification_id"]
    assert "status" in body
    assert isinstance(body["status"], str)


def test_create_instant_notification_success(client: TestClient):
    payload = {
        "event_key": "user.registered",
        "user_id": str(uuid4()),
        "payload": {"email": "test@example.com"},
        "idempotency_key": str(uuid4()),
    }

    response = client.post("/v1/notifications/instant", json=payload)
    _assert_notification_response(response)


def test_create_instant_notification_idempotent(client: TestClient):
    idempotency_key = str(uuid4())
    payload = {
        "event_key": "user.password_reset",
        "user_id": str(uuid4()),
        "payload": {"ip": "127.0.0.1"},
        "idempotency_key": idempotency_key,
    }

    first_response = client.post("/v1/notifications/instant", json=payload)
    second_response = client.post("/v1/notifications/instant", json=payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_body = first_response.json()
    second_body = second_response.json()

    # Expect same notification_id for same idempotency_key
    assert first_body["notification_id"] == second_body["notification_id"]
    assert first_body["status"] == second_body["status"]


def test_create_scheduled_notification_success(client: TestClient):
    scheduled_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    payload = {
        "event_key": "report.generate",
        "user_id": str(uuid4()),
        "payload": {"format": "pdf"},
        "scheduled_at": scheduled_at,
        "idempotency_key": str(uuid4()),
    }

    response = client.post("/v1/notifications/scheduled", json=payload)
    _assert_notification_response(response)


def test_create_periodic_notification_success(client: TestClient):
    start_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    repeat_until = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    payload = {
        "event_key": "subscription.reminder",
        "user_id": str(uuid4()),
        "payload": {"plan": "pro"},
        "cron_expression": "*/5 * * * *",
        "start_at": start_at,
        "repeat_until": repeat_until,
        "idempotency_key": str(uuid4()),
    }

    response = client.post("/v1/notifications/periodic", json=payload)
    _assert_notification_response(response)


@pytest.mark.parametrize(
    "endpoint,payload",
    [
        (
            "/v1/notifications/instant",
            {
                # missing required fields
                "event_key": "invalid",
            },
        ),
        (
            "/v1/notifications/scheduled",
            {
                "event_key": "invalid",
                "user_id": str(uuid4()),
                "payload": {},
                # missing scheduled_at and idempotency_key
            },
        ),
        (
            "/v1/notifications/periodic",
            {
                "event_key": "invalid",
                "user_id": str(uuid4()),
                "payload": {},
                # missing cron/start/repeat/idempotency_key
            },
        ),
    ],
)
def test_validation_errors(client: TestClient, endpoint: str, payload: dict):
    response = client.post(endpoint, json=payload)
    assert response.status_code == 422
