from __future__ import annotations

from dataclasses import dataclass

from backend.core.types import ThreatHypothesis

from .evidence import (
    AttributionEvidence,
    AttributionResult,
    clamp_score,
    normalize_confidence,
)


@dataclass(frozen=True)
class AttributionWeights:
    """Relative contribution of each evidence source."""

    anomaly: float = 0.30
    influence: float = 0.25
    counterfactual: float = 0.30
    integrity: float = 0.10
    history: float = 0.05


class AttributionEngine:
    """
    Evidence-based threat attribution.

    L5 does not determine ground-truth maliciousness. It creates a
    defensible threat hypothesis from evidence produced by previous
    security layers and optional historical context.
    """

    def __init__(
        self,
        weights: AttributionWeights | None = None,
    ) -> None:
        self.weights = weights or AttributionWeights()

    def _anomaly_component(
        self,
        evidence: AttributionEvidence,
    ) -> float:
        """Convert anomaly evidence into a 0-100 contribution."""
        if evidence.anomaly_score is None:
            return 0.0

        return clamp_score(
            evidence.anomaly_score
        )

    def _influence_component(
        self,
        evidence: AttributionEvidence,
    ) -> float:
        """
        Convert harmful influence into a 0-100 contribution.

        Positive influence is not treated as suspicious.
        Negative influence is stronger evidence as magnitude grows.
        """
        if evidence.influence_score is None:
            return 0.0

        if evidence.influence_score >= 0:
            return 0.0

        return clamp_score(
            abs(evidence.influence_score)
        )

    def _counterfactual_component(
        self,
        evidence: AttributionEvidence,
    ) -> float:
        """
        Convert counterfactual evidence into a 0-100 contribution.

        Accuracy and loss improvements after removal are treated as
        independent supporting signals.
        """
        score = 0.0

        if evidence.counterfactual_accuracy_delta is not None:
            accuracy_delta = evidence.counterfactual_accuracy_delta

            if accuracy_delta > 0:
                score += min(
                    60.0,
                    accuracy_delta * 300.0,
                )

        if evidence.counterfactual_loss_delta is not None:
            loss_delta = evidence.counterfactual_loss_delta

            if loss_delta < 0:
                score += min(
                    40.0,
                    abs(loss_delta) * 10.0,
                )

        if evidence.harmful_counterfactual:
            score = max(
                score,
                50.0,
            )

        return clamp_score(score)

    def _integrity_component(
        self,
        evidence: AttributionEvidence,
    ) -> float:
        """Convert integrity evidence into a risk contribution."""
        if evidence.integrity_valid is False:
            return 100.0

        if evidence.artifact_hash_verified is False:
            return 100.0

        return 0.0

    def _history_component(
        self,
        evidence: AttributionEvidence,
    ) -> float:
        """Convert historical risk into a bounded contribution."""
        if evidence.historical_risk is None:
            return 0.0

        return clamp_score(
            evidence.historical_risk
        )

    def calculate_attribution_score(
        self,
        evidence: AttributionEvidence,
    ) -> float:
        """Calculate the combined attribution evidence score."""
        score = (
            self._anomaly_component(evidence)
            * self.weights.anomaly
        )

        score += (
            self._influence_component(evidence)
            * self.weights.influence
        )

        score += (
            self._counterfactual_component(evidence)
            * self.weights.counterfactual
        )

        score += (
            self._integrity_component(evidence)
            * self.weights.integrity
        )

        score += (
            self._history_component(evidence)
            * self.weights.history
        )

        return clamp_score(score)

    def determine_hypothesis(
        self,
        evidence: AttributionEvidence,
        attribution_score: float,
    ) -> ThreatHypothesis:
        """
        Determine the most defensible threat hypothesis.

        This is intentionally conservative. A hypothesis is not a
        verdict.
        """
        # Integrity violations have their own explicit evidence path.
        if (
            evidence.integrity_valid is False
            or evidence.artifact_hash_verified is False
        ):
            return ThreatHypothesis.INTEGRITY_VIOLATION

        # Strong multi-layer model-impact evidence.
        strong_anomaly = (
            evidence.anomaly_score is not None
            and evidence.anomaly_score >= 65.0
        )

        harmful_influence = (
            evidence.influence_score is not None
            and evidence.influence_score < 0
        )

        strong_counterfactual = (
            evidence.harmful_counterfactual is True
            or (
                evidence.counterfactual_accuracy_delta is not None
                and evidence.counterfactual_accuracy_delta >= 0.05
            )
        )

        if (
            strong_anomaly
            and harmful_influence
            and strong_counterfactual
        ):
            return ThreatHypothesis.MODEL_POISONING

        # Counterfactual + influence evidence can still indicate
        # model-level poisoning even when L2 is inconclusive.
        if (
            harmful_influence
            and strong_counterfactual
            and attribution_score >= 50.0
        ):
            return ThreatHypothesis.MODEL_POISONING

        if strong_anomaly:
            return ThreatHypothesis.ANOMALOUS_UPDATE

        if harmful_influence or strong_counterfactual:
            return ThreatHypothesis.ANOMALOUS_UPDATE

        if attribution_score >= 25.0:
            return ThreatHypothesis.UNKNOWN

        return ThreatHypothesis.NONE

    def _supporting_evidence(
        self,
        evidence: AttributionEvidence,
    ) -> tuple[str, ...]:
        """Build human-readable evidence references."""
        items: list[str] = []

        if (
            evidence.anomaly_score is not None
            and evidence.anomaly_score >= 65.0
        ):
            items.append(
                f"L2 anomaly score {evidence.anomaly_score:.2f}"
            )

        if (
            evidence.influence_score is not None
            and evidence.influence_score < 0
        ):
            items.append(
                f"L3 harmful influence {evidence.influence_score:.2f}"
            )

        if evidence.harmful_influence:
            items.append(
                "L3 reports harmful influence"
            )

        if (
            evidence.counterfactual_accuracy_delta is not None
            and evidence.counterfactual_accuracy_delta > 0
        ):
            items.append(
                "L4 removal improves validation accuracy"
            )

        if (
            evidence.counterfactual_loss_delta is not None
            and evidence.counterfactual_loss_delta < 0
        ):
            items.append(
                "L4 removal reduces validation loss"
            )

        if evidence.harmful_counterfactual:
            items.append(
                "L4 reports harmful counterfactual impact"
            )

        if evidence.integrity_valid is False:
            items.append(
                "L0 integrity validation failed"
            )

        if evidence.artifact_hash_verified is False:
            items.append(
                "Artifact hash verification failed"
            )

        if (
            evidence.historical_risk is not None
            and evidence.historical_risk > 0
        ):
            items.append(
                f"Historical risk {evidence.historical_risk:.2f}"
            )

        return tuple(items)

    def _calculate_confidence(
        self,
        evidence: AttributionEvidence,
        attribution_score: float,
        hypothesis: ThreatHypothesis,
    ) -> float:
        """Estimate confidence from independent supporting signals."""
        signals = 0

        if (
            evidence.anomaly_score is not None
            and evidence.anomaly_score >= 65.0
        ):
            signals += 1

        if (
            evidence.influence_score is not None
            and evidence.influence_score < 0
        ):
            signals += 1

        if evidence.harmful_counterfactual:
            signals += 1

        if evidence.integrity_valid is False:
            signals += 1

        if (
            evidence.historical_risk is not None
            and evidence.historical_risk >= 50.0
        ):
            signals += 1

        if hypothesis == ThreatHypothesis.NONE:
            return normalize_confidence(
                min(0.50, attribution_score / 100.0)
            )

        base_confidence = {
            1: 0.35,
            2: 0.55,
            3: 0.75,
            4: 0.90,
            5: 0.95,
        }.get(signals, 0.95)

        score_factor = attribution_score / 100.0

        return normalize_confidence(
            min(
                base_confidence,
                0.25 + (0.75 * score_factor),
            )
        )

    def attribute(
        self,
        evidence: AttributionEvidence,
    ) -> AttributionResult:
        """
        Produce an attribution result from observed evidence.
        """
        attribution_score = self.calculate_attribution_score(
            evidence
        )

        hypothesis = self.determine_hypothesis(
            evidence,
            attribution_score,
        )

        supporting_evidence = self._supporting_evidence(
            evidence
        )

        confidence = self._calculate_confidence(
            evidence,
            attribution_score,
            hypothesis,
        )

        if supporting_evidence:
            evidence_text = "; ".join(
                supporting_evidence
            )

            explanation = (
                f"Threat hypothesis: {hypothesis.value}. "
                f"Supporting evidence: {evidence_text}. "
                "This is an evidence-based hypothesis, not a "
                "ground-truth maliciousness verdict."
            )
        else:
            explanation = (
                "No strong cross-layer security evidence was observed. "
                "No maliciousness conclusion is made."
            )

        return AttributionResult(
            client_id=evidence.client_id,
            hypothesis=hypothesis,
            confidence=confidence,
            evidence_score=attribution_score,
            supporting_evidence=supporting_evidence,
            explanation=explanation,
        )
