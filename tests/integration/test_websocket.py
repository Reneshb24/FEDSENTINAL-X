"""
Integration tests for the FedSentinel WebSocket event stream.
"""

import threading
import time

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies import get_orchestrator
from backend.core.types import EventType
from backend.main import app
from backend.services.round_orchestrator import RoundOrchestrator


@pytest.fixture
def orchestrator():
    """
    Create the exact orchestrator used by FastAPI dependency injection.
    """

    instance = RoundOrchestrator()

    app.dependency_overrides[get_orchestrator] = (
        lambda: instance
    )

    yield instance

    app.dependency_overrides.clear()


@pytest.fixture
def client(orchestrator):
    """
    Create a FastAPI test client using the same orchestrator.
    """

    with TestClient(app) as test_client:
        yield test_client


# ------------------------------------------------------------------
# Global stream
# ------------------------------------------------------------------


def test_websocket_replays_existing_events(client):
    """
    Existing events should be immediately replayed after connection.
    """

    response = client.post(
        "/api/v1/rounds",
        params={
            "round_id": "WS-ROUND-001",
            "target_clients": 20,
        },
    )

    assert response.status_code == 201

    with client.websocket_connect("/ws/events") as websocket:
        event = websocket.receive_json()

    assert event["event_id"] == "WS-ROUND-001-round-created"
    assert event["event_type"] == "ROUND_STARTED"
    assert event["round_id"] == "WS-ROUND-001"


def test_websocket_event_payload_is_preserved(client):
    """
    WebSocket events should preserve the original event payload.
    """

    client.post(
        "/api/v1/rounds",
        params={
            "round_id": "WS-PAYLOAD",
            "target_clients": 12,
        },
    )

    with client.websocket_connect("/ws/events") as websocket:
        event = websocket.receive_json()

    assert event["payload"]["target_clients"] == 12
    assert event["payload"]["status"] == "CREATED"


# ------------------------------------------------------------------
# Round-specific stream
# ------------------------------------------------------------------


def test_round_websocket_filters_events(client):
    """
    A round-specific WebSocket must only expose events belonging
    to that round.
    """

    client.post(
        "/api/v1/rounds",
        params={
            "round_id": "WS-ROUND-A",
            "target_clients": 10,
        },
    )

    client.post(
        "/api/v1/rounds",
        params={
            "round_id": "WS-ROUND-B",
            "target_clients": 20,
        },
    )

    with client.websocket_connect(
        "/ws/events/WS-ROUND-A"
    ) as websocket:
        event = websocket.receive_json()

    assert event["round_id"] == "WS-ROUND-A"
    assert event["event_type"] == "ROUND_STARTED"


# ------------------------------------------------------------------
# Realtime event delivery
# ------------------------------------------------------------------


def test_websocket_receives_new_event(client, orchestrator):
    """
    Events created after WebSocket connection should eventually
    be delivered to the connected client.
    """

    with client.websocket_connect("/ws/events") as websocket:

        def emit_event():
            time.sleep(0.3)

            orchestrator.event_manager.emit(
                event_id="WS-LIVE-EVENT",
                event_type=EventType.TRUST_UPDATED,
                message="Live trust event.",
                round_id="WS-LIVE-ROUND",
                client_id="H11",
                data={
                    "risk_score": 82.0,
                    "confidence": 0.91,
                    "status": "QUARANTINED",
                    "action": "QUARANTINE",
                },
            )

        thread = threading.Thread(
            target=emit_event,
            daemon=True,
        )

        thread.start()

        event = websocket.receive_json()

        thread.join(timeout=2)

    assert event["event_id"] == "WS-LIVE-EVENT"
    assert event["event_type"] == "TRUST_UPDATED"
    assert event["round_id"] == "WS-LIVE-ROUND"
    assert event["client_id"] == "H11"

    assert event["payload"]["risk_score"] == 82.0
    assert event["payload"]["status"] == "QUARANTINED"


# ------------------------------------------------------------------
# Multiple events
# ------------------------------------------------------------------


def test_websocket_replays_multiple_events(client, orchestrator):
    """
    Multiple stored events should be replayed in chronological
    order.
    """

    client.post(
        "/api/v1/rounds",
        params={
            "round_id": "WS-MULTIPLE",
            "target_clients": 20,
        },
    )

    orchestrator.event_manager.emit(
        event_id="WS-MULTIPLE-EVENT-2",
        event_type=EventType.INTEGRITY_CHECKED,
        message="Integrity check completed.",
        round_id="WS-MULTIPLE",
        client_id="H1",
        data={
            "passed": True,
            "forensic_eligible": True,
        },
    )

    with client.websocket_connect("/ws/events") as websocket:

        first = websocket.receive_json()
        second = websocket.receive_json()

    assert first["event_id"] == "WS-MULTIPLE-round-created"
    assert second["event_id"] == "WS-MULTIPLE-EVENT-2"


# ------------------------------------------------------------------
# Clean disconnect
# ------------------------------------------------------------------


def test_websocket_can_disconnect_cleanly(client):
    """
    Closing a WebSocket connection should not raise an application
    error.
    """

    with client.websocket_connect("/ws/events") as websocket:
        websocket.close()

