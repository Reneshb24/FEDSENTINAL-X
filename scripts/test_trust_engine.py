from backend.core.types import (
    Action,
    ThreatHypothesis,
    TrustStatus,
)
from backend.trust import TrustEngine, TrustEvidence


def show_result(name: str, result) -> None:
    print()
    print(name)
    print("-" * 80)
    print(f"Client:       {result.client_id}")
    print(f"Risk score:   {result.risk_score:.2f}")
    print(f"Confidence:   {result.confidence:.3f}")
    print(f"Status:       {result.status.value}")
    print(f"Action:       {result.action.value}")
    print(f"Hypothesis:   {result.hypothesis.value}")
    print("Evidence:")

    for item in result.supporting_evidence:
        print(f"  - {item}")

    print(f"Reason:       {result.reason}")


def main() -> None:
    print("=" * 88)
    print("FedSentinel - Trust Engine Controlled Validation")
    print("=" * 88)

    engine = TrustEngine()

    # ---------------------------------------------------------
    # 1. HEALTHY CLIENT
    # ---------------------------------------------------------
    healthy = TrustEvidence(
        client_id="H1",

        anomaly_score=30.0,
        anomaly_z_score=0.7,
        is_anomaly_outlier=False,
        peer_similarity=0.35,

        influence_score=1.2,
        harmful_influence=False,
        validation_delta=0.012,

        counterfactual_accuracy_delta=-0.002,
        counterfactual_loss_delta=0.4,
        harmful_counterfactual=False,

        attribution_score=10.0,
        hypothesis=ThreatHypothesis.NONE,
        attribution_confidence=0.10,

        integrity_valid=True,
        artifact_hash_verified=True,

        historical_risk=5.0,
    )

    healthy_result = engine.evaluate(
        healthy
    )

    show_result(
        "CASE 1 - HEALTHY CLIENT",
        healthy_result,
    )

    assert healthy_result.status == (
        TrustStatus.TRUSTED
    )

    assert healthy_result.action == (
        Action.ALLOW
    )

    # ---------------------------------------------------------
    # 2. SINGLE-SIGNAL SUSPICION
    # ---------------------------------------------------------
    suspicious = TrustEvidence(
        client_id="H5",

        anomaly_score=70.0,
        anomaly_z_score=3.8,
        is_anomaly_outlier=True,
        peer_similarity=0.10,

        influence_score=1.0,
        harmful_influence=False,
        validation_delta=0.01,

        counterfactual_accuracy_delta=0.0,
        counterfactual_loss_delta=0.1,
        harmful_counterfactual=False,

        attribution_score=30.0,
        hypothesis=ThreatHypothesis.ANOMALOUS_UPDATE,
        attribution_confidence=0.45,

        integrity_valid=True,
        artifact_hash_verified=True,

        historical_risk=10.0,
    )

    suspicious_result = engine.evaluate(
        suspicious
    )

    show_result(
        "CASE 2 - SINGLE-SIGNAL SUSPICION",
        suspicious_result,
    )

    assert suspicious_result.status in {
        TrustStatus.REVIEW,
        TrustStatus.SUSPICIOUS,
    }

    # ---------------------------------------------------------
    # 3. MULTI-SIGNAL H11-STYLE ATTACK
    # ---------------------------------------------------------
    attack = TrustEvidence(
        client_id="H11",

        # L2
        anomaly_score=96.36,
        anomaly_z_score=26.452,
        is_anomaly_outlier=True,
        peer_similarity=0.0,

        # L3
        influence_score=-16.70,
        harmful_influence=True,
        validation_delta=-0.1670,

        # L4
        counterfactual_accuracy_delta=0.1670,
        counterfactual_loss_delta=-3.0167,
        harmful_counterfactual=True,

        # L5
        attribution_score=57.16,
        hypothesis=ThreatHypothesis.MODEL_POISONING,
        attribution_confidence=0.679,

        # Integrity
        integrity_valid=True,
        artifact_hash_verified=True,

        # No historical risk required.
        historical_risk=0.0,
    )

    attack_result = engine.evaluate(
        attack
    )

    show_result(
        "CASE 3 - H11 MULTI-SIGNAL ATTACK",
        attack_result,
    )

    assert attack_result.risk_score >= 45.0

    assert attack_result.status in {
        TrustStatus.SUSPICIOUS,
        TrustStatus.QUARANTINED,
    }

    assert attack_result.action in {
        Action.REVIEW,
        Action.QUARANTINE,
    }

    # ---------------------------------------------------------
    # 4. INTEGRITY FAILURE
    # ---------------------------------------------------------
    integrity_failure = TrustEvidence(
        client_id="H20",

        anomaly_score=10.0,

        integrity_valid=False,
        artifact_hash_verified=False,

        attribution_score=0.0,
        hypothesis=ThreatHypothesis.INTEGRITY_VIOLATION,

        historical_risk=0.0,
    )

    integrity_result = engine.evaluate(
        integrity_failure
    )

    show_result(
        "CASE 4 - INTEGRITY FAILURE",
        integrity_result,
    )

    assert integrity_result.status == (
        TrustStatus.QUARANTINED
    )

    assert integrity_result.action == (
        Action.QUARANTINE
    )

    print()
    print("=" * 88)
    print("TRUST ENGINE CONTROLLED VALIDATION PASSED")
    print("=" * 88)


if __name__ == "__main__":
    main()
