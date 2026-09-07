"""
Pydantic schemas for federated model updates.

An update represents a contribution from one federated client during one
federated learning round. Security evidence is accumulated as the update
moves through the FedSentinel pipeline.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.core.types import Action, ThreatHypothesis


class UpdateIntegrity(BaseModel):
    """Integrity information associated with a model update."""

    model_config = ConfigDict(extra="forbid")

    artifact_hash: str = Field(min_length=1, max_length=128)
    hash_algorithm: str = Field(default="sha256", min_length=1, max_length=32)

    verified: bool = False
    verification_timestamp: datetime | None = None


class UpdateProvenance(BaseModel):
    """Origin and lifecycle information for an update."""

    model_config = ConfigDict(extra="forbid")

    client_id: str = Field(min_length=1, max_length=64)
    round_id: str = Field(min_length=1, max_length=64)

    created_at: datetime
    received_at: datetime | None = None

    artifact_format: str = Field(
        default=".npz",
        min_length=1,
        max_length=32,
    )

    source: str = Field(
        default="federated_client",
        min_length=1,
        max_length=64,
    )


class UpdateFingerprint(BaseModel):
    """Privacy-safe representation of an update."""

    model_config = ConfigDict(extra="forbid")

    dimension: int = Field(ge=1)
    vector_hash: str = Field(min_length=1, max_length=128)

    l2_norm: float = Field(ge=0.0)
    mean: float
    standard_deviation: float = Field(ge=0.0)

    generated_at: datetime


class UpdateEvidence(BaseModel):
    """
    Security evidence accumulated during update analysis.

    This object deliberately stores evidence separately from the final
    security decision.
    """

    model_config = ConfigDict(extra="forbid")

    layer0_passed: bool | None = None
    layer1_fingerprint: UpdateFingerprint | None = None

    layer2_anomaly_score: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    layer2_is_outlier: bool | None = None

    layer3_influence_score: float | None = Field(
        default=None,
        ge=-100.0,
        le=100.0,
    )

    layer4_stability_score: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    layer5_attribution_score: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    evidence_items: list[str] = Field(default_factory=list)


class UpdateDecision(BaseModel):
    """
    Security interpretation of the collected evidence.

    Risk and confidence are intentionally separate values.
    """

    model_config = ConfigDict(extra="forbid")

    risk_score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=1.0)

    threat_hypothesis: ThreatHypothesis = ThreatHypothesis.NONE

    recommended_action: Action = Action.ALLOW

    reason: str = Field(default="", max_length=2000)


class UpdateBase(BaseModel):
    """Common update identity and metadata."""

    model_config = ConfigDict(extra="forbid")

    update_id: str = Field(min_length=1, max_length=64)
    client_id: str = Field(min_length=1, max_length=64)
    round_id: str = Field(min_length=1, max_length=64)

    num_examples: int = Field(ge=1)

    submitted_at: datetime


class UpdateCreate(UpdateBase):
    """Schema received when a client submits a model update."""

    integrity: UpdateIntegrity
    provenance: UpdateProvenance


class UpdateResponse(UpdateBase):
    """Complete update representation returned by the backend."""

    integrity: UpdateIntegrity
    provenance: UpdateProvenance

    fingerprint: UpdateFingerprint | None = None
    evidence: UpdateEvidence | None = None
    decision: UpdateDecision | None = None

    is_quarantined: bool = False
    processed_at: datetime | None = None


class UpdateListResponse(BaseModel):
    """Collection of model updates."""

    model_config = ConfigDict(extra="forbid")

    updates: list[UpdateResponse]
    total: int = Field(ge=0)