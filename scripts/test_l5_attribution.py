from __future__ import annotations

from backend.core.types import ThreatHypothesis
from backend.layers.layer5_attribution.attributor import AttributionEngine
from backend.layers.layer5_attribution.evidence import AttributionEvidence


def main() -> None:
    print("=" * 88)
    print("FedSentinel - Layer 5 Controlled Attribution Test")
    print("=" * 88)

    engine = AttributionEngine()

    # ---------------------------------------------------------
    # Normal client
    # ---------------------------------------------------------
    normal_evidence = AttributionEvidence(
        client_id="H1",
        anomaly_score=35.0,
        anomaly_z_score=0.8,
        peer_similarity=0.35,
        influence_score=1.2,
        validation_delta=0.012,
        harmful_influence=False,
        counterfactual_accuracy_delta=-0.002,
        counterfactual_loss_delta=0.4,
        harmful_counterfactual=False,
        integrity_valid=True,
        artifact_hash_verified=True,
        historical_risk=5.0,
    )

    # ---------------------------------------------------------
    # Suspicious client
    #
    # IMPORTANT:
    # No attack/malicious label is supplied to L5.
    # These are observations from previous layers.
    # ---------------------------------------------------------
    suspicious_evidence = AttributionEvidence(
        client_id="H2",
        anomaly_score=96.0,
        anomaly_z_score=24.0,
        peer_similarity=0.38,
        influence_score=-21.90,
        validation_delta=-0.219,
        harmful_influence=True,
        counterfactual_accuracy_delta=0.213,
        counterfactual_loss_delta=-5.7632,
        harmful_counterfactual=True,
        integrity_valid=True,
        artifact_hash_verified=True,
        historical_risk=0.0,
    )

    normal_result = engine.attribute(
        normal_evidence
    )

    suspicious_result = engine.attribute(
        suspicious_evidence
    )

    print()
    print("-" * 88)

    print("H1")
    print(f"  Attribution score: {normal_result.evidence_score:.2f}")
    print(f"  Hypothesis: {normal_result.hypothesis.value}")
    print(f"  Confidence: {normal_result.confidence:.3f}")
    print(
        f"  Supporting evidence: "
        f"{normal_result.supporting_evidence}"
    )
    print(f"  Explanation: {normal_result.explanation}")

    print()
    print("H2")
    print(f"  Attribution score: {suspicious_result.evidence_score:.2f}")
    print(f"  Hypothesis: {suspicious_result.hypothesis.value}")
    print(f"  Confidence: {suspicious_result.confidence:.3f}")
    print(
        f"  Supporting evidence: "
        f"{suspicious_result.supporting_evidence}"
    )
    print(f"  Explanation: {suspicious_result.explanation}")

    print("-" * 88)

    assert suspicious_result.hypothesis == (
        ThreatHypothesis.MODEL_POISONING
    )

    assert suspicious_result.evidence_score > (
        normal_result.evidence_score
    )

    assert suspicious_result.confidence > (
        normal_result.confidence
    )

    assert len(
        suspicious_result.supporting_evidence
    ) >= 3

    print()
    print("L5 CONTROLLED VALIDATION PASSED")
    print("=" * 88)


if __name__ == "__main__":
    main()
