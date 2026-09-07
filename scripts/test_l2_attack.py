"""
FedSentinel Layer 2 adversarial validation.

This test:
    1. Runs a legitimate 20-client federation.
    2. Selects one real model update.
    3. Injects a strong synthetic model-update perturbation.
    4. Generates L1 fingerprints.
    5. Runs L2 anomaly detection.
    6. Verifies that the injected update becomes an outlier.

Important:
    The detector is NOT told which client is malicious.
    The selected client is only used to construct the test attack.
"""

from collections import OrderedDict

import torch

from backend.models.cnn import FedSentinelCNN
from backend.layers.layer1_fingerprint import FingerprintGenerator
from backend.layers.layer2_anomaly import Layer2Detector
from backend.simulation.federation import FederationEngine
from data.dataset import load_mnist_train


def model_factory():
    """Create a fresh FedSentinel CNN."""
    return FedSentinelCNN()


def inject_update_perturbation(
    update,
    scale: float = 25.0,
):
    """
    Create a poisoned copy of a model update.

    The original update is not modified.

    The perturbation is deliberately strong so that this test validates
    the anomaly pipeline itself before we move to subtle backdoor attacks.
    """

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

    return update.__class__(
        update_id=f"{update.update_id}-poisoned",
        client_id=update.client_id,
        round_id=update.round_id,
        delta=poisoned_delta,
        num_examples=update.num_examples,
        created_at=update.created_at,
    )


def main() -> None:

    print("=" * 70)
    print("FedSentinel — Layer 2 Adversarial Validation")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Load dataset
    # ---------------------------------------------------------

    print("\n[1/5] Loading MNIST dataset...")

    dataset = load_mnist_train()

    print(
        f"Training samples: {len(dataset)}"
    )

    # ---------------------------------------------------------
    # 2. Create federation
    # ---------------------------------------------------------

    print("\n[2/5] Creating federation...")

    federation = FederationEngine(
        dataset=dataset,
        model_factory=model_factory,
        num_clients=20,
        seed=42,
        concentration=0.5,
        local_epochs=1,
        batch_size=32,
        learning_rate=0.001,
        device="cpu",
    )

    print(
        f"Clients configured: "
        f"{federation.num_clients}"
    )

    # ---------------------------------------------------------
    # 3. Run legitimate round
    # ---------------------------------------------------------

    print("\n[3/5] Training legitimate clients...")

    federation_result = federation.run_round(
        round_id="l2-attack-round-001"
    )

    updates = list(
        federation_result.updates
    )

    print(
        f"Legitimate updates: "
        f"{len(updates)}"
    )

    # ---------------------------------------------------------
    # 4. Inject one poisoned update
    # ---------------------------------------------------------

    print("\n[4/5] Injecting synthetic poisoned update...")

    # Select a test target without using a hardcoded client ID.
    target_index = len(updates) // 2

    original_update = updates[target_index]

    poisoned_update = inject_update_perturbation(
        original_update,
        scale=25.0,
    )

    updates[target_index] = poisoned_update

    attack_client = poisoned_update.client_id

    print(
        f"Test attack injected into: "
        f"{attack_client}"
    )

    print(
        "Detector receives no attack label."
    )

    # ---------------------------------------------------------
    # 5. Generate L1 fingerprints
    # ---------------------------------------------------------

    print("\n[5/5] Generating fingerprints...")

    generator = FingerprintGenerator()

    fingerprints = {}

    for update in updates:

        fingerprint = generator.generate(
            update
        )

        fingerprints[
            update.client_id
        ] = fingerprint.vector

    print(
        f"Fingerprints generated: "
        f"{len(fingerprints)}"
    )

    # ---------------------------------------------------------
    # Run L2
    # ---------------------------------------------------------

    print("\nRunning Layer 2 anomaly detection...\n")

    detector = Layer2Detector(
        z_threshold=3.0,
    )

    result = detector.detect_round(
        fingerprints
    )

    # ---------------------------------------------------------
    # Display results
    # ---------------------------------------------------------

    print("-" * 90)

    outliers = []

    for client_id, detection in result.detections.items():

        if detection.is_outlier:
            outliers.append(client_id)

        marker = (
            " <-- TEST ATTACK"
            if client_id == attack_client
            else ""
        )

        print(
            f"{client_id:>4} | "
            f"z={detection.z_score:>10.3f} | "
            f"anomaly={detection.anomaly_score:>7.2f} | "
            f"peer={detection.peer_similarity:>7.3f} | "
            f"outlier={str(detection.is_outlier):<5} | "
            f"distance={detection.baseline_distance:>10.3f}"
            f"{marker}"
        )

    print("-" * 90)

    # ---------------------------------------------------------
    # Attack result
    # ---------------------------------------------------------

    attack_detection = result.detections[
        attack_client
    ]

    print("\nAttack analysis:")
    print(
        f"  Test target: "
        f"{attack_client}"
    )
    print(
        f"  Z-score: "
        f"{attack_detection.z_score:.3f}"
    )
    print(
        f"  Anomaly score: "
        f"{attack_detection.anomaly_score:.2f}"
    )
    print(
        f"  Peer similarity: "
        f"{attack_detection.peer_similarity:.3f}"
    )
    print(
        f"  Outlier: "
        f"{attack_detection.is_outlier}"
    )
    print(
        f"  Reason: "
        f"{attack_detection.reason}"
    )

    print("\nDetection summary:")
    print(
        f"  Total clients: "
        f"{len(result.detections)}"
    )
    print(
        f"  Outliers: "
        f"{len(outliers)}"
    )
    print(
        f"  Outlier clients: "
        f"{outliers if outliers else 'None'}"
    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert len(updates) == 20
    assert len(fingerprints) == 20
    assert len(result.detections) == 20

    assert attack_client in result.detections

    assert attack_detection.is_outlier, (
        "L2 failed to detect the injected model-update anomaly."
    )

    print(
        "\nL2 ADVERSARIAL VALIDATION PASSED"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()