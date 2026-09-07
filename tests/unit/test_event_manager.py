from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from backend.core.types import EventType
from backend.services.event_manager import (
    EventManager,
)


def test_emit_event() -> None:
    manager = EventManager()

    event = manager.emit(
        event_id="evt-001",
        event_type=EventType.ROUND_STARTED,
        round_id="round-001",
        message="Security round started.",
    )

    assert event.event_id == "evt-001"
    assert event.event_type == EventType.ROUND_STARTED
    assert event.round_id == "round-001"
    assert event.message == "Security round started."
    assert event.timestamp.tzinfo is not None


def test_duplicate_event_rejected() -> None:
    manager = EventManager()

    manager.emit(
        event_id="evt-001",
        event_type=EventType.ROUND_STARTED,
        message="Round started.",
    )

    with pytest.raises(ValueError):
        manager.emit(
            event_id="evt-001",
            event_type=EventType.ROUND_STARTED,
            message="Duplicate event.",
        )


def test_empty_event_id_rejected() -> None:
    manager = EventManager()

    with pytest.raises(ValueError):
        manager.emit(
            event_id="",
            event_type=EventType.ROUND_STARTED,
            message="Round started.",
        )


def test_empty_message_rejected() -> None:
    manager = EventManager()

    with pytest.raises(ValueError):
        manager.emit(
            event_id="evt-001",
            event_type=EventType.ROUND_STARTED,
            message="   ",
        )


def test_get_event() -> None:
    manager = EventManager()

    manager.emit(
        event_id="evt-001",
        event_type=EventType.ROUND_STARTED,
        message="Round started.",
    )

    event = manager.get_event("evt-001")

    assert event.event_id == "evt-001"


def test_missing_event_rejected() -> None:
    manager = EventManager()

    with pytest.raises(KeyError):
        manager.get_event("does-not-exist")


def test_events_for_round() -> None:
    manager = EventManager()

    manager.emit(
        event_id="evt-001",
        event_type=EventType.ROUND_STARTED,
        round_id="round-001",
        message="Round started.",
    )

    manager.emit(
        event_id="evt-002",
        event_type=EventType.CLIENT_UPDATE_RECEIVED,
        round_id="round-001",
        client_id="H1",
        message="Update received.",
    )

    manager.emit(
        event_id="evt-003",
        event_type=EventType.ROUND_STARTED,
        round_id="round-002",
        message="Round started.",
    )

    events = manager.events_for_round("round-001")

    assert len(events) == 2
    assert events[0].event_id == "evt-001"
    assert events[1].event_id == "evt-002"


def test_events_for_client() -> None:
    manager = EventManager()

    manager.emit(
        event_id="evt-001",
        event_type=EventType.CLIENT_UPDATE_RECEIVED,
        round_id="round-001",
        client_id="H11",
        message="Update received.",
    )

    manager.emit(
        event_id="evt-002",
        event_type=EventType.ANOMALY_DETECTED,
        round_id="round-001",
        client_id="H11",
        message="Anomaly detected.",
    )

    manager.emit(
        event_id="evt-003",
        event_type=EventType.CLIENT_UPDATE_RECEIVED,
        round_id="round-001",
        client_id="H1",
        message="Update received.",
    )

    events = manager.events_for_client("H11")

    assert len(events) == 2
    assert all(
        event.client_id == "H11"
        for event in events
    )


def test_events_by_type() -> None:
    manager = EventManager()

    manager.emit(
        event_id="evt-001",
        event_type=EventType.ANOMALY_DETECTED,
        client_id="H11",
        message="Anomaly detected.",
    )

    manager.emit(
        event_id="evt-002",
        event_type=EventType.TRUST_UPDATED,
        client_id="H11",
        message="Trust updated.",
    )

    manager.emit(
        event_id="evt-003",
        event_type=EventType.ANOMALY_DETECTED,
        client_id="H12",
        message="Anomaly detected.",
    )

    events = manager.events_by_type(
        EventType.ANOMALY_DETECTED
    )

    assert len(events) == 2


def test_query_combined_filters() -> None:
    manager = EventManager()

    manager.emit(
        event_id="evt-001",
        event_type=EventType.ANOMALY_DETECTED,
        round_id="round-001",
        client_id="H11",
        message="Anomaly detected.",
    )

    manager.emit(
        event_id="evt-002",
        event_type=EventType.TRUST_UPDATED,
        round_id="round-001",
        client_id="H11",
        message="Trust updated.",
    )

    manager.emit(
        event_id="evt-003",
        event_type=EventType.ANOMALY_DETECTED,
        round_id="round-002",
        client_id="H11",
        message="Anomaly detected.",
    )

    events = manager.query(
        round_id="round-001",
        client_id="H11",
        event_type=EventType.ANOMALY_DETECTED,
    )

    assert len(events) == 1
    assert events[0].event_id == "evt-001"


def test_events_are_chronological() -> None:
    manager = EventManager()

    now = datetime.now(timezone.utc)

    manager.emit(
        event_id="evt-002",
        event_type=EventType.TRUST_UPDATED,
        message="Later event.",
        timestamp=now + timedelta(seconds=2),
    )

    manager.emit(
        event_id="evt-001",
        event_type=EventType.ROUND_STARTED,
        message="Earlier event.",
        timestamp=now,
    )

    events = manager.list_events()

    assert events[0].event_id == "evt-001"
    assert events[1].event_id == "evt-002"


def test_latest_event() -> None:
    manager = EventManager()

    assert manager.latest_event() is None

    manager.emit(
        event_id="evt-001",
        event_type=EventType.ROUND_STARTED,
        message="Round started.",
    )

    manager.emit(
        event_id="evt-002",
        event_type=EventType.GLOBAL_MODEL_SECURED,
        message="Global model secured.",
    )

    latest = manager.latest_event()

    assert latest is not None
    assert latest.event_id == "evt-002"


def test_count() -> None:
    manager = EventManager()

    assert manager.count() == 0

    manager.emit(
        event_id="evt-001",
        event_type=EventType.ROUND_STARTED,
        message="Round started.",
    )

    manager.emit(
        event_id="evt-002",
        event_type=EventType.ROUND_STARTED,
        message="Another round started.",
    )

    assert manager.count() == 2


def test_event_data_is_stored() -> None:
    manager = EventManager()

    event = manager.emit(
        event_id="evt-001",
        event_type=EventType.ANOMALY_DETECTED,
        client_id="H11",
        message="Anomaly detected.",
        data={
            "anomaly_score": 96.54,
            "z_score": 27.89,
        },
    )

    assert event.data["anomaly_score"] == 96.54
    assert event.data["z_score"] == 27.89


def test_clear() -> None:
    manager = EventManager()

    manager.emit(
        event_id="evt-001",
        event_type=EventType.ROUND_STARTED,
        message="Round started.",
    )

    assert manager.count() == 1

    manager.clear()

    assert manager.count() == 0
    assert manager.latest_event() is None
# ------------------------------------------------------------------
# Realtime subscribers
# ------------------------------------------------------------------


def test_subscriber_receives_emitted_event():
    """
    A registered subscriber receives every newly emitted event.
    """

    manager = EventManager()

    received = []

    def subscriber(event):
        received.append(event)

    manager.subscribe(subscriber)

    event = manager.emit(
        event_id="SUB-001",
        event_type=EventType.TRUST_UPDATED,
        message="Trust updated.",
        round_id="ROUND-001",
        client_id="H11",
        data={
            "risk_score": 80.0,
        },
    )

    assert len(received) == 1
    assert received[0] == event


def test_duplicate_subscriber_is_registered_once():
    """
    Registering the same subscriber twice must not duplicate
    notifications.
    """

    manager = EventManager()

    received = []

    def subscriber(event):
        received.append(event)

    manager.subscribe(subscriber)
    manager.subscribe(subscriber)

    manager.emit(
        event_id="SUB-002",
        event_type=EventType.TRUST_UPDATED,
        message="Trust updated.",
    )

    assert manager.subscriber_count() == 1
    assert len(received) == 1


def test_unsubscribe_stops_notifications():
    """
    An unsubscribed consumer must stop receiving new events.
    """

    manager = EventManager()

    received = []

    def subscriber(event):
        received.append(event)

    manager.subscribe(subscriber)
    manager.unsubscribe(subscriber)

    manager.emit(
        event_id="SUB-003",
        event_type=EventType.TRUST_UPDATED,
        message="Trust updated.",
    )

    assert manager.subscriber_count() == 0
    assert received == []


def test_subscriber_failure_does_not_break_event_creation():
    """
    A failing subscriber must not prevent the event from being stored.
    """

    manager = EventManager()

    def broken_subscriber(event):
        raise RuntimeError("subscriber failure")

    manager.subscribe(broken_subscriber)

    event = manager.emit(
        event_id="SUB-004",
        event_type=EventType.TRUST_UPDATED,
        message="Trust updated.",
    )

    assert event.event_id == "SUB-004"
    assert manager.count() == 1


def test_clear_removes_subscribers():
    """
    clear() removes both stored events and realtime subscribers.
    """

    manager = EventManager()

    def subscriber(event):
        pass

    manager.subscribe(subscriber)

    manager.emit(
        event_id="SUB-005",
        event_type=EventType.TRUST_UPDATED,
        message="Trust updated.",
    )

    manager.clear()

    assert manager.count() == 0
    assert manager.subscriber_count() == 0