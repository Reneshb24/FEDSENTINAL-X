from __future__ import annotations

from collections import OrderedDict

import torch

from backend.layers.layer1_fingerprint import FingerprintGenerator
from backend.layers.layer2_anomaly import Layer2Detector
from backend.layers.layer3_influence import InfluenceAnalyzer
from backend.layers.layer4_counterfactual import CounterfactualAnalyzer
from backend.layers.layer5_attribution import (
    AttributionEngine,
    AttributionEvidence,
)
from backend.models.cnn import FedSentinelCNN
from backend.models.update import create_model_update
from backend.simulation.federation import FederationEngine
from data.dataset import load_mnist_test, load_mnist_train


def model_factory() -> FedSentinelCNN:
    return FedSentinelCNN()


def poison_update(
    update,
    scale: float = 25.0,
):
    """Create the same synthetic model-poisoning update used by L3/L4 tests."""

    poisoned_delta = OrderedDict()

    for name, tensor in update.delta.items():

        if torch.is_floating_point(tensor):

            poisoned_delta[name] = (
                tensor.detach()
                .cpu()
                .clone()
                * scale
            )

        else:

            poisoned_delta[name] = (
                tensor.detach()
                .cpu()
                .clone()
            )

    return create_model_update(
        update_id=f"{update.update_id}-poisoned",
        client_id=update.client_id,
        round_id=update.round_id,
        delta=poisoned_delta,
        num_examples=update.num_examples,
    )


def main() -> None:
    print("=" * 100)
    print("FedSentinel - Layer 5 Real Adversarial Integration Test")
    print("=" * 100)

    # ---------------------------------------------------------
    # 1. DATASET
    # ---------------------------------------------------------
    print()
    print("[1/9] Loading datasets...")

    train_dataset = load_mnist_train()
    test_dataset = load_mnist_test()

    print(f"    Train samples: {len(train_dataset)}")
    print(f"    Test samples : {len(test_dataset)}")

    # ---------------------------------------------------------
    # 2. FEDERATION
    # ---------------------------------------------------------
    print()
    print("[2/9] Creating federation...")

    federation = FederationEngine(
        dataset=train_dataset,
        model_factory=model_factory,
        num_clients=20,
        seed=42,
        concentration=0.5,
        local_epochs=1,
        batch_size=32,
        learning_rate=0.001,
        device="cpu",
    )

    # ---------------------------------------------------------
    # 3. GENERATE LEGITIMATE UPDATES
    # ---------------------------------------------------------
    print()
    print("[3/9] Running federation round...")

    federation_result = federation.run_round(
        round_id="l5-attack-round-001"
    )

    updates = list(
        federation_result.updates
    )

    print(
        f"    Legitimate updates: "
        f"{len(updates)}"
    )

    assert len(updates) == 20

    # ---------------------------------------------------------
    # 4. INJECT SYNTHETIC ATTACK
    # ---------------------------------------------------------
    print()
    print("[4/9] Injecting synthetic model poisoning...")

    target_index = len(updates) // 2

    original_update = updates[target_index]

    poisoned = poison_update(
        original_update,
        scale=25.0,
    )

    updates[target_index] = poisoned

    attack_client = poisoned.client_id

    print(
        f"    Test attack target: "
        f"{attack_client}"
    )

    print(
        "    L1/L2/L3/L4/L5 receive no attack label."
    )

    # ---------------------------------------------------------
    # 5. L1
    # ---------------------------------------------------------
    print()
    print("[5/9] Generating L1 fingerprints...")

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
    # 6. L2
    # ---------------------------------------------------------
    print()
    print("[6/9] Running L2 anomaly detection...")

    l2 = Layer2Detector()

    l2_result = l2.detect_round(
        fingerprints
    )

    attack_l2 = l2_result.detections[
        attack_client
    ]

    print(
        f"    Attack client L2 score: "
        f"{attack_l2.anomaly_score:.2f}"
    )

    print(
        f"    Attack client L2 z-score: "
        f"{attack_l2.z_score:.3f}"
    )

    print(
        f"    Attack client L2 outlier: "
        f"{attack_l2.is_outlier}"
    )

    # ---------------------------------------------------------
    # 7. VALIDATION + L3 + L4
    # ---------------------------------------------------------
    print()
    print("[7/9] Running L3 and L4 analysis...")

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

    l3 = InfluenceAnalyzer(
        model_factory=model_factory,
        validation_loader=validation_loader,
        device="cpu",
    )

    l3_results = l3.analyze(
        global_state=federation_result.global_state,
        updates=updates,
    )

    l3_by_client = {
        result.client_id: result
        for result in l3_results
    }

    l4 = CounterfactualAnalyzer(
        model_factory=model_factory,
        validation_loader=validation_loader,
        device="cpu",
    )

    l4_results = l4.analyze(
        global_state=federation_result.global_state,
        updates=updates,
    )

    attack_l3 = l3_by_client[
        attack_client
    ]

    attack_l4 = l4_results[
        attack_client
    ]

    print(
        f"    Attack L3 influence: "
        f"{attack_l3.influence_score:+.2f}"
    )

    print(
        f"    Attack L3 harmful: "
        f"{attack_l3.harmful_influence}"
    )

    print(
        f"    Attack L4 accuracy delta: "
        f"{attack_l4.accuracy_delta:+.4f}"
    )

    print(
        f"    Attack L4 loss delta: "
        f"{attack_l4.loss_delta:+.4f}"
    )

    print(
        f"    Attack L4 harmful: "
        f"{attack_l4.harmful_counterfactual}"
    )

    # ---------------------------------------------------------
    # 8. L5 ATTRIBUTION
    # ---------------------------------------------------------
    print()
    print("[8/9] Correlating evidence through L5...")

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

        # -----------------------------------------------------
        # CRITICAL:
        #
        # L5 receives observations only.
        #
        # No attack label.
        # No target client.
        # No ground-truth information.
        # -----------------------------------------------------
        evidence = AttributionEvidence(
            client_id=client_id,

            anomaly_score=(
                l2_detection.anomaly_score
            ),

            anomaly_z_score=(
                l2_detection.z_score
            ),

            peer_similarity=(
                l2_detection.peer_similarity
            ),

            influence_score=(
                l3_result.influence_score
            ),

            validation_delta=(
                l3_result.validation_delta
            ),

            harmful_influence=(
                l3_result.harmful_influence
            ),

            counterfactual_accuracy_delta=(
                l4_result.accuracy_delta
            ),

            counterfactual_loss_delta=(
                l4_result.loss_delta
            ),

            harmful_counterfactual=(
                l4_result.harmful_counterfactual
            ),

            integrity_valid=True,

            artifact_hash_verified=True,

            historical_risk=0.0,
        )

        attribution_results[client_id] = (
            l5.attribute(evidence)
        )

    # ---------------------------------------------------------
    # 9. RESULTS
    # ---------------------------------------------------------
    print()
    print("-" * 100)

    print(
        f"{'CLIENT':<10}"
        f"{'SCORE':>10}"
        f"{'HYPOTHESIS':<24}"
        f"{'CONF':>10}"
        f"{'MARKER':<20}"
    )

    print("-" * 100)

    ranked = sorted(
        attribution_results.values(),
        key=lambda result: result.evidence_score,
        reverse=True,
    )

    for result in ranked:

        marker = ""

        if result.client_id == attack_client:
            marker = "<-- TEST ATTACK"

        print(
            f"{result.client_id:<10}"
            f"{result.evidence_score:>10.2f}"
            f"{result.hypothesis.value:<24}"
            f"{result.confidence:>10.3f}"
            f"{marker:<20}"
        )

    print("-" * 100)

    attack_result = attribution_results[
        attack_client
    ]

    attack_rank = next(
        index
        for index, result in enumerate(
            ranked,
            start=1,
        )
        if result.client_id == attack_client
    )

    print()
    print("ATTACK ATTRIBUTION")
    print(
        f"  Client:       {attack_client}"
    )
    print(
        f"  Rank:         {attack_rank}/20"
    )
    print(
        f"  Score:        "
        f"{attack_result.evidence_score:.2f}"
    )
    print(
        f"  Hypothesis:   "
        f"{attack_result.hypothesis.value}"
    )
    print(
        f"  Confidence:   "
        f"{attack_result.confidence:.3f}"
    )

    print()
    print("Supporting evidence:")

    for evidence_item in (
        attack_result.supporting_evidence
    ):
        print(
            f"  - {evidence_item}"
        )

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------
    assert len(attribution_results) == 20

    assert attack_l2.is_outlier

    assert attack_l3.harmful_influence

    assert attack_l4.harmful_counterfactual

    assert attack_result.evidence_score > 50.0

    print()
    print(
        "L5 ADVERSE EVIDENCE VALIDATION PASSED"
    )

    print("=" * 100)


if __name__ == "__main__":
    main()
