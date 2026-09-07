from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from backend.core.types import ThreatHypothesis


@dataclass(frozen=True)
class AttributionEvidence:
    """
    Evidence collected from the preceding security layers.

    These fields describe observations, not ground-truth labels.
    """

    client_id: str

    anomaly_score: Optional[float] = None
    anomaly_z_score: Optional[float] = None
    peer_similarity: Optional[float] = None

    influence_score: Optional[float] = None
    validation_delta: Optional[float] = None
    harmful_influence: Optional[bool] = None

    counterfactual_accuracy_delta: Optional[float] = None
    counterfactual_loss_delta: Optional[float] = None
    harmful_counterfactual: Optional[bool] = None

    integrity_valid: Optional[bool] = None
    artifact_hash_verified: Optional[bool] = None

    historical_risk: Optional[float] = None


@dataclass(frozen=True)
class AttributionResult:
    """
    Threat attribution produced from observed security evidence.

    A threat hypothesis is an evidence-based explanation, not a
    definitive maliciousness verdict.
    """

    client_id: str

    hypothesis: ThreatHypothesis

    confidence: float

    evidence_score: float

    supporting_evidence: tuple[str, ...]

    explanation: str


def clamp_score(value: float) -> float:
    """Clamp a score to the inclusive range [0, 100]."""
    return max(0.0, min(100.0, float(value)))


def normalize_confidence(value: float) -> float:
    """Return confidence as a value between 0.0 and 1.0."""
    return max(0.0, min(1.0, float(value)))
