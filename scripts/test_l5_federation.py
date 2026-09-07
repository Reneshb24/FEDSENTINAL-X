from __future__ import annotations

from backend.layers.layer1_fingerprint import FingerprintGenerator
from backend.layers.layer2_anomaly import Layer2Detector
from backend.layers.layer3_influence import InfluenceAnalyzer
from backend.layers.layer4_counterfactual import CounterfactualAnalyzer
from backend.layers.layer5_attribution import (
    AttributionEngine,
    AttributionEvidence,
)
from backend.models.cnn import FedSentinelCNN
from backend.simulation.federation import FederationEngine
from data.dataset import load_mnist_test, load_mnist_train


def main() -> None:
    print("=" * 88)
    print("FedSentinel - Layer 5 Real Federation Integration Test")
    print("=" * 88)

    # ---------------------------------------------------------
    # 1. DATASET
    # ---------------------------------------------------------
    print()
    print("[1] Loading datasets...")

    train_dataset = load_mnist_train()
    test_dataset = load_mnist_test()

    print(f"    Train samples: {len(train_dataset)}")
    print(f"    Test samples : {len(test_dataset)}")

    # ---------------------------------------------------------
    # 2. FEDERATION
    # ---------------------------------------------------------
    print()
    print("[2] Creating federation...")

    federation = FederationEngine(
        dataset=train_dataset,
        model_factory=FedSentinelCNN,
        num_clients=20,
        seed=42,
        concentration=0.5,
        local_epochs=1,
        batch_size=32,
        learning_rate=0.001,
        device="cpu",
    )

    print(f"    Clients: {federation.num_clients}")

    # ---------------------------------------------------------
    # 3. FEDERATION ROUND
    # ---------------------------------------------------------
    print()
    print("[3] Running federation round...")

    round_result = federation.run_round(
        round_id="L5-REAL-001"
    )

    updates = round_result.updates

    print(f"    Updates generated: {len(updates)}")

    assert len(updates) == 20

    # ---------------------------------------------------------
    # 4. L1 FINGERPRINTS
    # ---------------------------------------------------------
    print()
    print("[4] Generating L1 fingerprints...")

    fingerprint_generator = FingerprintGenerator()

    fingerprints = {}

    for update in updates:

        result = fingerprint_generator.generate(
            update
        )

        fingerprints[update.client_id] = result.vector

    print(
        f"    Fingerprints generated: "
        f"{len(fingerprints)}"
    )

    assert len(fingerprints) == 20

    # ---------------------------------------------------------
    # 5. L2 ANOMALY DETECTION
    # ---------------------------------------------------------
    print()
    print("[5] Running L2 anomaly detection...")

    l2 = Layer2Detector()

    l2_result = l2.detect_round(
        fingerprints
    )

    print(
        f"    L2 detections: "
        f"{len(l2_result.detections)}"
    )

    assert len(l2_result.detections) == 20

    # ---------------------------------------------------------
    # 6. VALIDATION SUBSET
    # ---------------------------------------------------------
    print()
    print("[6] Preparing validation subset...")

    from backend.layers.layer3_influence.subset_sampler import (
        create_validation_loader,
        create_validation_subset,
    )

    validation_subset = create_validation_subset(
        test_dataset,
        sample_size=1000,
        seed=42,
    )

    validation_loader = create_validation_loader(
        validation_subset,
        batch_size=64,
    )

    print(
        f"    Validation samples: "
        f"{len(validation_subset)}"
    )

    # ---------------------------------------------------------
    # 7. L3 INFLUENCE
    # ---------------------------------------------------------
    print()
    print("[7] Running L3 influence analysis...")

    l3 = InfluenceAnalyzer(
        model_factory=FedSentinelCNN,
        validation_loader=validation_loader,
        device="cpu",
    )

    l3_results = l3.analyze(
        global_state=round_result.global_state,
        updates=updates,
    )

    l3_by_client = {
        result.client_id: result
        for result in l3_results
    }

    print(
        f"    L3 results: "
        f"{len(l3_by_client)}"
    )

    assert len(l3_by_client) == 20

    # ---------------------------------------------------------
    # 8. L4 COUNTERFACTUAL
    # ---------------------------------------------------------
    print()
    print("[8] Running L4 counterfactual analysis...")

    l4 = CounterfactualAnalyzer(
        model_factory=FedSentinelCNN,
        validation_loader=validation_loader,
        device="cpu",
    )

    l4_results = l4.analyze(
        global_state=round_result.global_state,
        updates=updates,
    )

    print(
        f"    L4 results: "
        f"{len(l4_results)}"
    )

    assert len(l4_results) == 20

    # ---------------------------------------------------------
    # 9. L5 ATTRIBUTION
    # ---------------------------------------------------------
    print()
    print("[9] Correlating L2 + L3 + L4 through L5...")

    l5 = AttributionEngine()

    attribution_results = {}

    for client_id in fingerprints:

        l2_detection = (
            l2_result.detections[client_id]
        )

        l3_result = (
            l3_by_client[client_id]
        )

        l4_result = (
            l4_results[client_id]
        )

        # IMPORTANT:
        # No malicious/attack label is provided here.
        #
        # L5 receives only observations produced by
        # previous security layers.
        evidence = AttributionEvidence(
            client_id=client_id,

            # L2
            anomaly_score=(
                l2_detection.anomaly_score
            ),
            anomaly_z_score=(
                l2_detection.z_score
            ),
            peer_similarity=(
                l2_detection.peer_similarity
            ),

            # L3
            influence_score=(
                l3_result.influence_score
            ),
            validation_delta=(
                l3_result.validation_delta
            ),
            harmful_influence=(
                l3_result.harmful_influence
            ),

            # L4
            counterfactual_accuracy_delta=(
                l4_result.accuracy_delta
            ),
            counterfactual_loss_delta=(
                l4_result.loss_delta
            ),
            harmful_counterfactual=(
                l4_result.harmful_counterfactual
            ),

            # Integrity
            integrity_valid=True,
            artifact_hash_verified=True,

            # No persistent history yet.
            historical_risk=0.0,
        )

        attribution_results[client_id] = (
            l5.attribute(evidence)
        )

    # ---------------------------------------------------------
    # 10. RESULTS
    # ---------------------------------------------------------
    print()
    print("-" * 88)

    print(
        f"{'CLIENT':<10}"
        f"{'SCORE':>10}"
        f"{'HYPOTHESIS':<24}"
        f"{'CONF':>10}"
    )

    print("-" * 88)

    ranked = sorted(
        attribution_results.values(),
        key=lambda result: result.evidence_score,
        reverse=True,
    )

    for result in ranked:

        print(
            f"{result.client_id:<10}"
            f"{result.evidence_score:>10.2f}"
            f"{result.hypothesis.value:<24}"
            f"{result.confidence:>10.3f}"
        )

    print("-" * 88)

    print()
    print("L5 REAL FEDERATION INTEGRATION COMPLETED")
    print()
    print(
        "L5 received no attack or maliciousness label."
    )
    print(
        "L5 correlated only L2, L3, and L4 evidence."
    )
    print("=" * 88)


if __name__ == "__main__":
    main()
