"""
Pydantic schemas for FedSentinel security incidents.

A detection represents evidence about an individual update.
An incident represents a security situation that may involve one or more
clients, updates, or rounds.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.core.types import Action, ThreatHypothesis, ThreatLevel


class IncidentEvidence(BaseModel):
    """Evidence associated with a security incident."""

    model_config = ConfigDict(extra="forbid")

    detection_ids: list[str] = Field(default_factory=list)
    update_ids: list[str] = Field(default_factory=list)
    client_ids: list[str] = Field(default_factory=list)
    round_ids: list[str] = Field(default_factory=list)

    evidence_items: list[str] = Field(default_factory=list)


class IncidentBase(BaseModel):
    """Common fields for a security incident."""

    model_config = ConfigDict(extra="forbid")

    incident_id: str = Field(min_length=1, max_length=64)

    title: str = Field(min_length=1, max_length=200)

    description: str = Field(
        default="",
        max_length=4000,
    )

    threat_level: ThreatLevel
    threat_hypothesis: ThreatHypothesis


class IncidentCreate(IncidentBase):
    """Schema used to create a new incident."""

    evidence: IncidentEvidence = Field(
        default_factory=IncidentEvidence,
    )


class IncidentResponse(IncidentBase):
    """Complete incident representation returned by the API."""

    created_at: datetime
    updated_at: datetime

    status: str = Field(
        default="OPEN",
        min_length=1,
        max_length=32,
    )

    recommended_action: Action = Action.REVIEW

    risk_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    evidence: IncidentEvidence = Field(
        default_factory=IncidentEvidence,
    )

    assigned_to: str | None = Field(
        default=None,
        max_length=128,
    )

    resolved_at: datetime | None = None

    resolution_notes: str | None = Field(
        default=None,
        max_length=4000,
    )


class IncidentListResponse(BaseModel):
    """Collection of security incidents."""

    model_config = ConfigDict(extra="forbid")

    incidents: list[IncidentResponse]

    total: int = Field(ge=0)