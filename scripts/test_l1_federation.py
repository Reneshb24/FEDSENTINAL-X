"""
Integration test for FedSentinel Layer 1 fingerprinting.

This script:
1. Loads the MNIST training dataset.
2. Creates a 20-client federated-learning simulation.
3. Trains each hospital client for one local epoch.
4. Generates a 128-dimensional fingerprint for every update.
5. Verifies that all clients produced valid, unique fingerprints.
"""

from backend.layers.layer1_fingerprint import FingerprintGenerator
from backend.models.cnn import FedSentinelCNN
from backend.simulation.federation import FederationEngine
from data.dataset import load_mnist_train


def main() -> None:
    print("=" * 60)
    print("FedSentinel - Layer 1 Federation Test")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Load dataset
    # ---------------------------------------------------------
    print("\n[1/4] Loading MNIST dataset...")

    dataset = load_mnist_train()

    print(f"Training samples: {len(dataset)}")

    # ---------------------------------------------------------
    # 2. Create federation
    # ---------------------------------------------------------
    print("\n[2/4] Creating 20-client federation...")

    engine = FederationEngine(
        dataset=dataset,
        model_factory=FedSentinelCNN,
        num_clients=20,
        seed=42,
        concentration=0.5,
        local_epochs=1,
        batch_size=32,
        learning_rate=0.001,
        device="cpu",
    )

    print("Federation created.")

    # ---------------------------------------------------------
    # 3. Run federated round
    # ---------------------------------------------------------
    print("\n[3/4] Running federated training round...")
    print("This may take some time on CPU.\n")

    round_result = engine.run_round(
        "l1-round-001"
    )

    print(
        f"Clients participating: "
        f"{round_result.num_clients}"
    )

    print(
        f"Updates generated: "
        f"{len(round_result.updates)}"
    )

    # ---------------------------------------------------------
    # 4. Generate fingerprints
    # ---------------------------------------------------------
    print("\n[4/4] Generating L1 fingerprints...\n")

    generator = FingerprintGenerator()

    fingerprints = []

    for update in round_result.updates:

        fingerprint = generator.generate(
            update
        )

        fingerprints.append(
            fingerprint
        )

        print(
            f"{update.client_id:>4} | "
            f"dimension={fingerprint.dimension:>3} | "
            f"norm={fingerprint.l2_norm:.4f} | "
            f"mean={fingerprint.mean:.6f} | "
            f"std={fingerprint.standard_deviation:.6f} | "
            f"hash={fingerprint.vector_hash[:12]}..."
        )

    # ---------------------------------------------------------
    # Verification
    # ---------------------------------------------------------

    print("\n" + "-" * 60)
    print("L1 VERIFICATION")
    print("-" * 60)

    dimensions = {
        fingerprint.dimension
        for fingerprint in fingerprints
    }

    unique_hashes = {
        fingerprint.vector_hash
        for fingerprint in fingerprints
    }

    print(
        f"Total fingerprints: "
        f"{len(fingerprints)}"
    )

    print(
        f"Fingerprint dimensions: "
        f"{sorted(dimensions)}"
    )

    print(
        f"Unique fingerprint hashes: "
        f"{len(unique_hashes)}"
    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert round_result.num_clients == 20, (
        "Expected 20 participating clients."
    )

    assert len(round_result.updates) == 20, (
        "Expected 20 model updates."
    )

    assert len(fingerprints) == 20, (
        "Expected 20 fingerprints."
    )

    assert dimensions == {128}, (
        "Every fingerprint must have dimension 128."
    )

    assert len(unique_hashes) == 20, (
        "Each real client update should have "
        "a unique fingerprint hash."
    )

    assert all(
        fingerprint.vector.numel() == 128
        for fingerprint in fingerprints
    ), (
        "Every fingerprint vector must contain "
        "exactly 128 values."
    )

    print("\n" + "=" * 60)
    print("20-CLIENT L1 FINGERPRINT TEST OK")
    print("=" * 60)


if __name__ == "__main__":
    main()