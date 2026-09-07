"""
Pydantic schemas for FedSentinel detection results.

A detection result contains evidence collected from the multi-layer
security pipeline and the resulting security interpretation.

Important:
    Risk != Verdict.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.core.types import (
    Action,
    DetectionStatus,
    ThreatHypothesis,
    ThreatLevel,
)


class Layer0Result(BaseModel):
    """Result of first-line local update validation."""

    model_config = ConfigDict(extra="forbid")

    passed: bool
    integrity_verified: bool
    duplicate_detected: bool = False
    gradient_bounds_valid: bool = True
    label_sanity_passed: bool = True

    reason: str = Field(
        default="",
        max_length=1000,
    )


class Layer1Result(BaseModel):
    """Privacy-safe update fingerprint result."""

    model_config = ConfigDict(extra="forbid")

    fingerprint: dict[str, float | int | str]

    peer_similarity: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
    )

    distance_from_baseline: float | None = Field(
        default=None,
        ge=0.0,
    )


class Layer2Result(BaseModel):
    """Robust anomaly-detection result."""

    model_config = ConfigDict(extra="forbid")

    anomaly_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    is_outlier: bool

    z_score: float | None = None

    peer_count: int = Field(
        default=0,
        ge=0,
    )

    reason: str = Field(
        default="",
        max_length=1000,
    )


class Layer3Result(BaseModel):
    """Influence analysis result."""

    model_config = ConfigDict(extra="forbid")

    influence_score: float = Field(
        ge=-100.0,
        le=100.0,
    )

    validation_delta: float | None = None

    sample_size: int = Field(
        default=0,
        ge=0,
    )

    harmful_influence: bool = False

    reason: str = Field(
        default="",
        max_length=1000,
    )


class Layer4Result(BaseModel):
    """
    Counterfactual robustness analysis.

    L4 compares the aggregated model with a client contribution
    against the corresponding model with that client contribution
    removed.

    The result is evidence only. It does not establish maliciousness.
    """

    model_config = ConfigDict(extra="forbid")

    # ---------------------------------------------------------
    # Existing counterfactual/stability contract
    # ---------------------------------------------------------

    stability_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    trials: int = Field(
        default=0,
        ge=0,
    )

    perturbation_strength: float = Field(
        default=0.0,
        ge=0.0,
    )

    unstable: bool = False

    # ---------------------------------------------------------
    # Actual L4 validation evidence
    # ---------------------------------------------------------

    # Difference in validation accuracy after removing the client.

    # Positive:
    #     removing the client improves accuracy.
    #
    # Negative:
    #     removing the client reduces accuracy.
    accuracy_delta: float = 0.0

    # Difference in validation loss after removing the client.
    #
    # Negative:
    #     removing the client reduces loss.
    #
    # Positive:
    #     removing the client increases loss.
    loss_delta: float = 0.0

    # Whether removing the client improves validation accuracy.
    improvement_without_client: bool = False

    # Stronger evidence when removal improves both:
    #
    #     accuracy
    #     loss
    #
    # This is evidence of harmful counterfactual impact,
    # NOT a maliciousness verdict.
    harmful_counterfactual: bool = False

    reason: str = Field(
        default="",
        max_length=1000,
    )


class Layer5Result(BaseModel):
    """Attribution and historical-correlation result."""

    model_config = ConfigDict(extra="forbid")

    attribution_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    historical_risk: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
    )

    related_clients: list[str] = Field(
        default_factory=list,
    )

    related_rounds: list[str] = Field(
        default_factory=list,
    )

    repeated_pattern: bool = False

    reason: str = Field(
        default="",
        max_length=1000,
    )


class DetectionEvidence(BaseModel):
    """
    Consolidated evidence from L0 through L5.

    This object is evidence, not a verdict.
    """

    model_config = ConfigDict(extra="forbid")

    layer0: Layer0Result | None = None

    layer1: Layer1Result | None = None

    layer2: Layer2Result | None = None

    layer3: Layer3Result | None = None

    layer4: Layer4Result | None = None

    layer5: Layer5Result | None = None

    evidence_items: list[str] = Field(
        default_factory=list,
    )


class DetectionDecision(BaseModel):
    """
    Security interpretation of collected evidence.

    Risk indicates potential danger.
    Confidence indicates confidence in that interpretation.
    Threat hypothesis explains the suspected behavior.
    Action indicates the recommended operational response.
    """

    model_config = ConfigDict(extra="forbid")

    risk_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    threat_level: ThreatLevel

    threat_hypothesis: ThreatHypothesis

    status: DetectionStatus

    recommended_action: Action

    reason: str = Field(
        default="",
        max_length=2000,
    )


class DetectionResult(BaseModel):
    """Complete security detection result for one model update."""

    model_config = ConfigDict(extra="forbid")

    update_id: str = Field(
        min_length=1,
        max_length=64,
    )

    client_id: str = Field(
        min_length=1,
        max_length=64,
    )

    round_id: str = Field(
        min_length=1,
        max_length=64,
    )

    started_at: datetime

    completed_at: datetime | None = None

    evidence: DetectionEvidence

    decision: DetectionDecision

    is_quarantined: bool = False

    quarantine_reason: str | None = None


class DetectionListResponse(BaseModel):
    """Collection of detection results."""

    model_config = ConfigDict(extra="forbid")

    detections: list[DetectionResult]

    total: int = Field(
        ge=0,
    )