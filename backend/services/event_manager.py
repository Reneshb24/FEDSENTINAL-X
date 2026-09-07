"""
FedSentinel event management.

EventManager provides the operational event stream for the FedSentinel
security control plane.

Responsibilities:
    - create structured security events
    - store events in memory
    - retrieve events by round
    - retrieve events by client
    - retrieve events by event type
    - maintain chronological event ordering
    - support event-stream consumers such as WebSocket clients

Important:
    EventManager does not perform detection.
    It does not modify Trust decisions.
    It only records security operations and evidence generated elsewhere.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from backend.core.types import EventType


@dataclass(frozen=True)
class SecurityEventRecord:
    """
    Runtime representation of one security event.
    """

    event_id: str
    event_type: EventType
    timestamp: datetime

    round_id: str | None = None
    client_id: str | None = None

    message: str = ""

    data: dict[str, Any] = field(default_factory=dict)


# A subscriber receives every newly emitted event.
EventSubscriber = Callable[[SecurityEventRecord], None]


class EventManager:
    """
    Manage the FedSentinel security event stream.

    Events are kept in memory for the current prototype.

    Subscribers allow realtime consumers such as WebSocket clients
    to receive events immediately after they are emitted.

    Event storage and the event model remain unchanged.
    """

    def __init__(self) -> None:
        self._events: list[SecurityEventRecord] = []
        self._event_ids: set[str] = set()

        # Realtime event consumers.
        self._subscribers: set[EventSubscriber] = set()

    # ---------------------------------------------------------
    # Event creation
    # ---------------------------------------------------------

    def emit(
        self,
        *,
        event_id: str,
        event_type: EventType,
        message: str,
        round_id: str | None = None,
        client_id: str | None = None,
        data: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> SecurityEventRecord:
        """
        Create and store a security event.

        After the event is stored, registered subscribers are notified.
        Subscriber failures do not prevent the event itself from being
        stored or returned.
        """

        if not event_id:
            raise ValueError(
                "event_id cannot be empty."
            )

        if not message.strip():
            raise ValueError(
                "message cannot be empty."
            )

        if event_id in self._event_ids:
            raise ValueError(
                f"Event '{event_id}' already exists."
            )

        event = SecurityEventRecord(
            event_id=event_id,
            event_type=event_type,
            timestamp=(
                timestamp
                if timestamp is not None
                else datetime.now(timezone.utc)
            ),
            round_id=round_id,
            client_id=client_id,
            message=message,
            data=dict(data or {}),
        )

        # Store first. The event must always remain available for
        # historical/replay consumers.
        self._events.append(event)
        self._event_ids.add(event_id)

        # Notify realtime consumers after successful storage.
        self._notify_subscribers(event)

        return event

    # ---------------------------------------------------------
    # Subscriber management
    # ---------------------------------------------------------

    def subscribe(
        self,
        subscriber: EventSubscriber,
    ) -> None:
        """
        Register a realtime event subscriber.

        Registering the same callable multiple times has no effect.
        """

        if not callable(subscriber):
            raise TypeError(
                "subscriber must be callable."
            )

        self._subscribers.add(subscriber)

    def unsubscribe(
        self,
        subscriber: EventSubscriber,
    ) -> None:
        """
        Remove a previously registered subscriber.

        Removing a subscriber that is not registered is harmless.
        """

        self._subscribers.discard(subscriber)

    def subscriber_count(self) -> int:
        """
        Return the number of currently registered subscribers.
        """

        return len(self._subscribers)

    def _notify_subscribers(
        self,
        event: SecurityEventRecord,
    ) -> None:
        """
        Notify all currently registered subscribers.

        Subscriber exceptions are isolated so one faulty consumer
        cannot break event creation for the rest of the system.
        """

        for subscriber in tuple(self._subscribers):
            try:
                subscriber(event)
            except Exception:
                # Realtime consumers must never be able to break
                # the security event store.
                continue

    # ---------------------------------------------------------
    # Event lookup
    # ---------------------------------------------------------

    def get_event(
        self,
        event_id: str,
    ) -> SecurityEventRecord:
        """
        Return one event by ID.
        """

        for event in self._events:
            if event.event_id == event_id:
                return event

        raise KeyError(
            f"Event '{event_id}' does not exist."
        )

    def list_events(self) -> list[SecurityEventRecord]:
        """
        Return all events in chronological order.
        """

        return sorted(
            self._events,
            key=lambda event: event.timestamp,
        )

    # ---------------------------------------------------------
    # Round filtering
    # ---------------------------------------------------------

    def events_for_round(
        self,
        round_id: str,
    ) -> list[SecurityEventRecord]:
        """
        Return all events belonging to a round.
        """

        return [
            event
            for event in self.list_events()
            if event.round_id == round_id
        ]

    # ---------------------------------------------------------
    # Client filtering
    # ---------------------------------------------------------

    def events_for_client(
        self,
        client_id: str,
    ) -> list[SecurityEventRecord]:
        """
        Return all events belonging to a client.
        """

        return [
            event
            for event in self.list_events()
            if event.client_id == client_id
        ]

    # ---------------------------------------------------------
    # Event-type filtering
    # ---------------------------------------------------------

    def events_by_type(
        self,
        event_type: EventType,
    ) -> list[SecurityEventRecord]:
        """
        Return all events of a specific type.
        """

        return [
            event
            for event in self.list_events()
            if event.event_type == event_type
        ]

    # ---------------------------------------------------------
    # Combined filtering
    # ---------------------------------------------------------

    def query(
        self,
        *,
        round_id: str | None = None,
        client_id: str | None = None,
        event_type: EventType | None = None,
    ) -> list[SecurityEventRecord]:
        """
        Query events using optional round, client, and event-type filters.
        """

        events = self.list_events()

        if round_id is not None:
            events = [
                event
                for event in events
                if event.round_id == round_id
            ]

        if client_id is not None:
            events = [
                event
                for event in events
                if event.client_id == client_id
            ]

        if event_type is not None:
            events = [
                event
                for event in events
                if event.event_type == event_type
            ]

        return events

    # ---------------------------------------------------------
    # Latest event
    # ---------------------------------------------------------

    def latest_event(
        self,
    ) -> SecurityEventRecord | None:
        """
        Return the most recent event.
        """

        events = self.list_events()

        if not events:
            return None

        return events[-1]

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------

    def count(self) -> int:
        """
        Return the number of stored events.
        """

        return len(self._events)

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Clear all events and realtime subscribers.

        Useful for tests and local development.
        """

        self._events.clear()
        self._event_ids.clear()
        self._subscribers.clear()