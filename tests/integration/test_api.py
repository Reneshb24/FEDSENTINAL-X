"""
Integration tests for the FedSentinel FastAPI application.

These tests verify the HTTP API contract without modifying the
underlying security pipeline.
"""

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies import get_orchestrator
from backend.main import app
from backend.services.round_orchestrator import RoundOrchestrator


@pytest.fixture
def client():
    """
    Create an isolated FastAPI test client.

    Each test receives a fresh in-memory orchestrator so that rounds,
    incidents, and events cannot leak between tests.
    """

    orchestrator = RoundOrchestrator()

    app.dependency_overrides[get_orchestrator] = (
        lambda: orchestrator
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ------------------------------------------------------------------
# System
# ------------------------------------------------------------------


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "FedSentinel"
    assert data["version"] == "0.1.0"
    assert data["status"] == "running"
    assert data["docs"] == "/docs"


def test_health_endpoint(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "FedSentinel"


# ------------------------------------------------------------------
# Rounds
# ------------------------------------------------------------------


def test_list_rounds_initially_empty(client):
    response = client.get("/api/v1/rounds")

    assert response.status_code == 200

    data = response.json()

    assert data["rounds"] == []
    assert data["total"] == 0


def test_create_round(client):
    response = client.post(
        "/api/v1/rounds",
        params={
            "round_id": "ROUND-001",
            "target_clients": 20,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["round_id"] == "ROUND-001"
    assert data["target_clients"] == 20
    assert data["status"] == "CREATED"
    assert data["metrics"]["participating_clients"] == 20
    assert data["metrics"]["received_updates"] == 0
    assert data["metrics"]["accepted_updates"] == 0
    assert data["metrics"]["quarantined_updates"] == 0


def test_get_round(client):
    create_response = client.post(
        "/api/v1/rounds",
        params={
            "round_id": "ROUND-GET",
            "target_clients": 20,
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/v1/rounds/ROUND-GET"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["round_id"] == "ROUND-GET"
    assert data["target_clients"] == 20
    assert data["status"] == "CREATED"


def test_get_unknown_round_returns_404(client):
    response = client.get(
        "/api/v1/rounds/DOES-NOT-EXIST"
    )

    assert response.status_code == 404


def test_duplicate_round_returns_conflict(client):
    first = client.post(
        "/api/v1/rounds",
        params={
            "round_id": "ROUND-DUPLICATE",
            "target_clients": 20,
        },
    )

    assert first.status_code == 201

    second = client.post(
        "/api/v1/rounds",
        params={
            "round_id": "ROUND-DUPLICATE",
            "target_clients": 20,
        },
    )

    assert second.status_code == 409


def test_created_round_emits_started_event(client):
    response = client.post(
        "/api/v1/rounds",
        params={
            "round_id": "ROUND-EVENT",
            "target_clients": 20,
        },
    )

    assert response.status_code == 201

    events_response = client.get(
        "/api/v1/rounds/ROUND-EVENT/events"
    )

    assert events_response.status_code == 200

    data = events_response.json()

    assert data["total"] == 1

    event = data["events"][0]

    assert event["event_id"] == "ROUND-EVENT-round-created"
    assert event["event_type"] == "ROUND_STARTED"
    assert event["round_id"] == "ROUND-EVENT"
    assert event["payload"]["target_clients"] == 20
    assert event["payload"]["status"] == "CREATED"


def test_round_list_contains_created_round(client):
    client.post(
        "/api/v1/rounds",
        params={
            "round_id": "ROUND-A",
            "target_clients": 10,
        },
    )

    client.post(
        "/api/v1/rounds",
        params={
            "round_id": "ROUND-B",
            "target_clients": 15,
        },
    )

    response = client.get("/api/v1/rounds")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    round_ids = {
        item["round_id"]
        for item in data["rounds"]
    }

    assert round_ids == {
        "ROUND-A",
        "ROUND-B",
    }


# ------------------------------------------------------------------
# Events
# ------------------------------------------------------------------


def test_events_endpoint(client):
    client.post(
        "/api/v1/rounds",
        params={
            "round_id": "ROUND-EVENTS",
            "target_clients": 20,
        },
    )

    response = client.get("/api/v1/events")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["events"]) == 1
    assert data["events"][0]["event_type"] == "ROUND_STARTED"


def test_events_filter_by_round(client):
    client.post(
        "/api/v1/rounds",
        params={
            "round_id": "ROUND-ONE",
            "target_clients": 20,
        },
    )

    client.post(
        "/api/v1/rounds",
        params={
            "round_id": "ROUND-TWO",
            "target_clients": 20,
        },
    )

    response = client.get(
        "/api/v1/events",
        params={
            "round_id": "ROUND-ONE",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["events"][0]["round_id"] == "ROUND-ONE"


def test_unknown_round_events_returns_404(client):
    response = client.get(
        "/api/v1/rounds/UNKNOWN/events"
    )

    assert response.status_code == 404


# ------------------------------------------------------------------
# Incidents
# ------------------------------------------------------------------


def test_incident_list_initially_empty(client):
    response = client.get("/api/v1/incidents")

    assert response.status_code == 200

    data = response.json()

    assert data["incidents"] == []
    assert data["total"] == 0


def test_unknown_incident_returns_404(client):
    response = client.get(
        "/api/v1/incidents/INC-DOES-NOT-EXIST"
    )

    assert response.status_code == 404


# ------------------------------------------------------------------
# OpenAPI
# ------------------------------------------------------------------


def test_openapi_available(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert data["info"]["title"] == "FedSentinel"
    assert data["info"]["version"] == "0.1.0"

    paths = data["paths"]

    assert "/api/v1/health" in paths
    assert "/api/v1/rounds" in paths
    assert "/api/v1/events" in paths
    assert "/api/v1/incidents" in paths