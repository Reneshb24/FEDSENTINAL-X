from __future__ import annotations

from dataclasses import dataclass

from backend.core.types import (
    Action,
    ThreatHypothesis,
    TrustStatus,
)


@dataclass(frozen=True)
class TrustEvidence:
    """
    Evidence supplied to the Trust Engine.

    The Trust Engine consumes evidence from security layers.
    It does not inspect raw model updates directly.
    """

    client_id: str

    # L2
    anomaly_score: float = 0.0
    anomaly_z_score: float = 0.0
    is_anomaly_outlier: bool = False
    peer_similarity: float = 0.0

    # L3
    influence_score: float = 0.0
    harmful_influence: bool = False
    validation_delta: float = 0.0

    # L4
    counterfactual_accuracy_delta: float = 0.0
    counterfactual_loss_delta: float = 0.0
    harmful_counterfactual: bool = False

    # L5
    attribution_score: float = 0.0
    hypothesis: ThreatHypothesis = (
        ThreatHypothesis.NONE
    )
    attribution_confidence: float = 0.0

    # Integrity / provenance
    integrity_valid: bool = True
    artifact_hash_verified: bool = True

    # Historical behavior
    historical_risk: float = 0.0


@dataclass(frozen=True)
class TrustDecision:
    """
    Operational trust decision for one client.

    This is still a risk-based security decision, not proof
    that the client is malicious.
    """

    client_id: str

    risk_score: float
    confidence: float

    status: TrustStatus
    action: Action

    hypothesis: ThreatHypothesis

    reason: str

    supporting_evidence: tuple[str, ...]


def clamp_score(value: float) -> float:
    """Clamp a risk score to [0, 100]."""

    return max(
        0.0,
        min(100.0, float(value)),
    )


def clamp_confidence(value: float) -> float:
    """Clamp confidence to [0, 1]."""

    return max(
        0.0,
        min(1.0, float(value)),
    )
