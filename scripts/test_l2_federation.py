"""
FedSentinel Layer 2 integration test.

Runs the real 20-client MNIST federation, generates L1 fingerprints,
then analyzes those fingerprints with the L2 robust anomaly detector.

No attack is used in this test.

Purpose:
    Validate L2 behavior on legitimate non-IID federated clients.
"""

from backend.models.cnn import FedSentinelCNN
from backend.layers.layer1_fingerprint import FingerprintGenerator
from backend.layers.layer2_anomaly import Layer2Detector
from backend.simulation.federation import FederationEngine
from data.dataset import load_mnist_train


def model_factory():
    """Create a fresh FedSentinel CNN."""
    return FedSentinelCNN()


def main() -> None:
    print("=" * 70)
    print("FedSentinel — Layer 2 Real Federation Test")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Load MNIST
    # ---------------------------------------------------------

    print("\n[1/4] Loading MNIST dataset...")

    dataset = load_mnist_train()

    print(
        f"Training samples: {len(dataset)}"
    )

    # ---------------------------------------------------------
    # 2. Create federation
    # ---------------------------------------------------------

    print("\n[2/4] Creating 20-client federation...")

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

    print(
        f"Partitions created: "
        f"{len(federation.partitions)}"
    )

    # ---------------------------------------------------------
    # 3. Generate federated updates
    # ---------------------------------------------------------

    print("\n[3/4] Training clients...")

    federation_result = federation.run_round(
        round_id="l2-baseline-round-001"
    )

    updates = federation_result.updates

    print(
        f"Updates generated: "
        f"{len(updates)}"
    )

    print(
        f"Round ID: "
        f"{federation_result.round_id}"
    )

    # ---------------------------------------------------------
    # 4. Generate L1 fingerprints
    # ---------------------------------------------------------

    print("\n[4/4] Generating L1 fingerprints...")

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

    print("-" * 80)

    outliers = []

    for client_id, detection in result.detections.items():

        if detection.is_outlier:
            outliers.append(client_id)

        print(
            f"{client_id:>4} | "
            f"z={detection.z_score:>8.3f} | "
            f"anomaly={detection.anomaly_score:>6.2f} | "
            f"peer={detection.peer_similarity:>7.3f} | "
            f"outlier={str(detection.is_outlier):<5} | "
            f"baseline_dist={detection.baseline_distance:>8.3f}"
        )

    print("-" * 80)

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print(
        f"\nTotal clients: "
        f"{len(result.detections)}"
    )

    print(
        f"Detected outliers: "
        f"{len(outliers)}"
    )

    print(
        f"Outlier clients: "
        f"{outliers if outliers else 'None'}"
    )

    # ---------------------------------------------------------
    # Baseline information
    # ---------------------------------------------------------

    print("\nRobust baseline:")

    print(
        f"  Dimensions: "
        f"{result.baseline.median.numel()}"
    )

    print(
        f"  Samples: "
        f"{result.baseline.sample_count}"
    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert federation.num_clients == 20

    assert len(federation.partitions) == 20

    assert len(updates) == 20

    assert len(fingerprints) == 20

    assert len(result.detections) == 20

    print(
        "\n20-CLIENT L2 FEDERATION TEST COMPLETED"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()