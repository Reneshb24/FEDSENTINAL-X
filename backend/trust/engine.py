from __future__ import annotations

from dataclasses import dataclass

from backend.core.types import (
    Action,
    ThreatHypothesis,
    TrustStatus,
)

from .evidence import (
    TrustDecision,
    TrustEvidence,
    clamp_confidence,
    clamp_score,
)


@dataclass(frozen=True)
class TrustWeights:
    """Weights used to combine independent security evidence."""

    anomaly: float = 0.20
    influence: float = 0.20
    counterfactual: float = 0.20
    attribution: float = 0.20
    integrity: float = 0.10
    history: float = 0.10


class TrustEngine:
    """
    Convert multi-layer security evidence into an operational
    trust decision.

    The engine does not claim to prove maliciousness. It produces
    a risk-based action using independent security evidence.
    """

    def __init__(
        self,
        weights: TrustWeights | None = None,
    ) -> None:

        self.weights = (
            weights
            if weights is not None
            else TrustWeights()
        )

        total = (
            self.weights.anomaly
            + self.weights.influence
            + self.weights.counterfactual
            + self.weights.attribution
            + self.weights.integrity
            + self.weights.history
        )

        if total <= 0:
            raise ValueError(
                "Trust weights must have a positive total."
            )

    # ---------------------------------------------------------
    # Evidence components
    # ---------------------------------------------------------

    @staticmethod
    def _anomaly_component(
        evidence: TrustEvidence,
    ) -> float:

        score = clamp_score(
            evidence.anomaly_score
        )

        if evidence.is_anomaly_outlier:
            score = max(
                score,
                80.0,
            )

        return score

    @staticmethod
    def _influence_component(
        evidence: TrustEvidence,
    ) -> float:

        if not evidence.harmful_influence:
            return 0.0

        # Negative influence is harmful evidence.
        magnitude = abs(
            evidence.influence_score
        )

        return clamp_score(
            magnitude
        )

    @staticmethod
    def _counterfactual_component(
        evidence: TrustEvidence,
    ) -> float:

        if not evidence.harmful_counterfactual:
            return 0.0

        accuracy_component = (
            max(
                0.0,
                evidence.counterfactual_accuracy_delta,
            )
            * 300.0
        )

        loss_component = (
            max(
                0.0,
                -evidence.counterfactual_loss_delta,
            )
            * 10.0
        )

        return clamp_score(
            max(
                50.0,
                accuracy_component
                + loss_component,
            )
        )

    @staticmethod
    def _attribution_component(
        evidence: TrustEvidence,
    ) -> float:

        return clamp_score(
            evidence.attribution_score
        )

    @staticmethod
    def _integrity_component(
        evidence: TrustEvidence,
    ) -> float:

        if (
            not evidence.integrity_valid
            or not evidence.artifact_hash_verified
        ):
            return 100.0

        return 0.0

    @staticmethod
    def _history_component(
        evidence: TrustEvidence,
    ) -> float:

        return clamp_score(
            evidence.historical_risk
        )

    # ---------------------------------------------------------
    # Risk calculation
    # ---------------------------------------------------------

    def calculate_risk(
        self,
        evidence: TrustEvidence,
    ) -> float:

        anomaly = self._anomaly_component(
            evidence
        )

        influence = self._influence_component(
            evidence
        )

        counterfactual = (
            self._counterfactual_component(
                evidence
            )
        )

        attribution = (
            self._attribution_component(
                evidence
            )
        )

        integrity = (
            self._integrity_component(
                evidence
            )
        )

        history = (
            self._history_component(
                evidence
            )
        )

        weights = self.weights

        weighted_score = (
            anomaly * weights.anomaly
            + influence * weights.influence
            + counterfactual * weights.counterfactual
            + attribution * weights.attribution
            + integrity * weights.integrity
            + history * weights.history
        )

        return clamp_score(
            weighted_score
        )

    # ---------------------------------------------------------
    # Confidence
    # ---------------------------------------------------------

    @staticmethod
    def calculate_confidence(
        evidence: TrustEvidence,
    ) -> float:

        strong_signals = 0

        if (
            evidence.anomaly_score >= 65.0
            or evidence.is_anomaly_outlier
        ):
            strong_signals += 1

        if evidence.harmful_influence:
            strong_signals += 1

        if evidence.harmful_counterfactual:
            strong_signals += 1

        if evidence.attribution_score >= 50.0:
            strong_signals += 1

        if (
            not evidence.integrity_valid
            or not evidence.artifact_hash_verified
        ):
            strong_signals += 1

        if evidence.historical_risk >= 60.0:
            strong_signals += 1

        confidence_by_signals = {
            0: 0.20,
            1: 0.35,
            2: 0.55,
            3: 0.75,
            4: 0.88,
            5: 0.94,
            6: 0.97,
        }

        confidence = confidence_by_signals[
            min(
                strong_signals,
                6,
            )
        ]

        # Attribution confidence provides an additional
        # independent confidence signal.
        confidence = max(
            confidence,
            evidence.attribution_confidence,
        )

        return clamp_confidence(
            confidence
        )

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    @staticmethod
    def determine_status(
        risk_score: float,
        evidence: TrustEvidence,
    ) -> TrustStatus:
        """
        Convert quantitative risk and corroborating evidence into
        an operational trust status.

        Status is intentionally not based on risk_score alone.
        Independent security signals can escalate a client even
        when their weighted numerical score is below a threshold.

        RISK != VERDICT.
        """

        # Integrity failure is an immediate containment event.
        if (
            not evidence.integrity_valid
            or not evidence.artifact_hash_verified
        ):
            return TrustStatus.QUARANTINED

        # Count independent strong security signals.
        strong_signals = sum(
            [
                evidence.anomaly_score >= 65.0
                or evidence.is_anomaly_outlier,
                evidence.harmful_influence,
                evidence.harmful_counterfactual,
                evidence.attribution_score >= 50.0,
                evidence.historical_risk >= 60.0,
            ]
        )

        # Three or more corroborating signals -> quarantine.
        if strong_signals >= 3:
            return TrustStatus.QUARANTINED

        # Two independent strong signals -> suspicious.
        if strong_signals >= 2:
            return TrustStatus.SUSPICIOUS

        # One strong signal -> review.
        if strong_signals >= 1:
            return TrustStatus.REVIEW

        # Fall back to quantitative risk when no strong signal exists.
        if risk_score >= 65.0:
            return TrustStatus.QUARANTINED

        if risk_score >= 45.0:
            return TrustStatus.SUSPICIOUS

        if risk_score >= 25.0:
            return TrustStatus.REVIEW

        return TrustStatus.TRUSTED

    # ---------------------------------------------------------
    # Action
    # ---------------------------------------------------------

    @staticmethod
    def determine_action(
        status: TrustStatus,
        evidence: TrustEvidence,
    ) -> Action:

        if status == TrustStatus.QUARANTINED:
            return Action.QUARANTINE

        if status == TrustStatus.SUSPICIOUS:
            return Action.REVIEW

        if status == TrustStatus.REVIEW:
            return Action.MONITOR

        # Trusted clients are allowed unless there is
        # a direct integrity failure.
        if (
            not evidence.integrity_valid
            or not evidence.artifact_hash_verified
        ):
            return Action.BLOCK

        return Action.ALLOW

    # ---------------------------------------------------------
    # Explanation
    # ---------------------------------------------------------

    @staticmethod
    def _build_supporting_evidence(
        evidence: TrustEvidence,
    ) -> tuple[str, ...]:

        items: list[str] = []

        if (
            evidence.anomaly_score >= 65.0
            or evidence.is_anomaly_outlier
        ):
            items.append(
                f"L2 anomaly evidence {evidence.anomaly_score:.2f}"
            )

        if evidence.harmful_influence:
            items.append(
                f"L3 harmful influence "
                f"{evidence.influence_score:+.2f}"
            )

        if evidence.harmful_counterfactual:
            items.append(
                "L4 removal improves validation behavior"
            )

        if evidence.attribution_score >= 25.0:
            items.append(
                f"L5 attribution "
                f"{evidence.attribution_score:.2f}"
            )

        if (
            not evidence.integrity_valid
            or not evidence.artifact_hash_verified
        ):
            items.append(
                "Artifact integrity verification failed"
            )

        if evidence.historical_risk >= 25.0:
            items.append(
                f"Historical risk "
                f"{evidence.historical_risk:.2f}"
            )

        if not items:
            items.append(
                "No strong security evidence detected."
            )

        return tuple(items)

    # ---------------------------------------------------------
    # Public decision API
    # ---------------------------------------------------------

    def evaluate(
        self,
        evidence: TrustEvidence,
    ) -> TrustDecision:

        risk_score = self.calculate_risk(
            evidence
        )

        confidence = self.calculate_confidence(
            evidence
        )

        status = self.determine_status(
            risk_score,
            evidence,
        )

        action = self.determine_action(
            status,
            evidence,
        )

        supporting_evidence = (
            self._build_supporting_evidence(
                evidence
            )
        )

        reason = (
            f"Client {evidence.client_id} has "
            f"risk score {risk_score:.2f} and "
            f"trust status {status.value}. "
            f"Recommended action: {action.value}. "
            f"This is a risk-based operational decision, "
            f"not proof of maliciousness."
        )

        return TrustDecision(
            client_id=evidence.client_id,
            risk_score=risk_score,
            confidence=confidence,
            status=status,
            action=action,
            hypothesis=evidence.hypothesis,
            reason=reason,
            supporting_evidence=supporting_evidence,
        )
