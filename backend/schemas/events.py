"""
Pydantic schemas for FedSentinel realtime security events.

Events are emitted by backend services and consumed by the WebSocket
layer and frontend security console.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.core.types import EventType, ThreatLevel


class EventBase(BaseModel):
    """Common fields shared by all realtime events."""

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=1, max_length=64)
    event_type: EventType

    timestamp: datetime

    round_id: str | None = Field(
        default=None,
        max_length=64,
    )

    client_id: str | None = Field(
        default=None,
        max_length=64,
    )

    update_id: str | None = Field(
        default=None,
        max_length=64,
    )


class SecurityEvent(EventBase):
    """
    Realtime security event emitted by the detection pipeline.

    Payload contains event-specific information while the core event
    metadata remains strongly typed.
    """

    threat_level: ThreatLevel = ThreatLevel.INFO

    message: str = Field(
        default="",
        max_length=2000,
    )

    payload: dict[str, Any] = Field(
        default_factory=dict,
    )


class EventBatch(BaseModel):
    """Batch of events returned or replayed by the backend."""

    model_config = ConfigDict(extra="forbid")

    events: list[SecurityEvent]
    total: int = Field(ge=0)