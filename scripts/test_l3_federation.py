"""
FedSentinel Layer 3 real federation validation.

Runs a real 20-client MNIST federation and measures the influence
of each client using leave-one-out validation.

No attack is used.

Purpose:
    Verify that L3 produces measurable influence evidence from
    legitimate federated updates.
"""

from backend.layers.layer3_influence import (
    InfluenceAnalyzer,
    create_validation_loader,
)
from backend.models.cnn import FedSentinelCNN
from backend.simulation.federation import FederationEngine
from data.dataset import load_mnist_test, load_mnist_train


def model_factory():
    return FedSentinelCNN()


def main() -> None:

    print("=" * 80)
    print("FedSentinel — Layer 3 Real Federation Validation")
    print("=" * 80)

    # ---------------------------------------------------------
    # 1. Load datasets
    # ---------------------------------------------------------

    print("\n[1/5] Loading datasets...")

    train_dataset = load_mnist_train()
    test_dataset = load_mnist_test()

    print(
        f"Training samples: {len(train_dataset)}"
    )

    print(
        f"Test samples: {len(test_dataset)}"
    )

    # ---------------------------------------------------------
    # 2. Create validation loader
    # ---------------------------------------------------------

    print("\n[2/5] Creating validation subset...")

    validation_loader = create_validation_loader(
        dataset=test_dataset,
        sample_size=1000,
        batch_size=64,
        seed=42,
    )

    print(
        "Validation samples: 1000"
    )

    # ---------------------------------------------------------
    # 3. Create federation
    # ---------------------------------------------------------

    print("\n[3/5] Creating federation...")

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

    print(
        f"Clients configured: "
        f"{federation.num_clients}"
    )

    print(
        f"Partitions created: "
        f"{len(federation.partitions)}"
    )

    # ---------------------------------------------------------
    # 4. Run federation
    # ---------------------------------------------------------

    print("\n[4/5] Training federation...")

    federation_result = federation.run_round(
        round_id="l3-federation-round-001"
    )

    updates = federation_result.updates

    print(
        f"Updates generated: "
        f"{len(updates)}"
    )

    # ---------------------------------------------------------
    # 5. Run L3
    # ---------------------------------------------------------

    print("\n[5/5] Running leave-one-out influence analysis...")

    analyzer = InfluenceAnalyzer(
        model_factory=model_factory,
        validation_loader=validation_loader,
        device="cpu",
    )

    results = analyzer.analyze(
        global_state=federation_result.global_state,
        updates=updates,
    )

    # ---------------------------------------------------------
    # Display results
    # ---------------------------------------------------------

    print("\nInfluence results:")
    print("-" * 100)

    for result in results:

        print(
            f"{result.client_id:>4} | "
            f"with={result.validation_with_client:.4f} | "
            f"without={result.validation_without_client:.4f} | "
            f"delta={result.validation_delta:+.4f} | "
            f"score={result.influence_score:+.2f} | "
            f"harmful={result.harmful_influence}"
        )

    print("-" * 100)

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    harmful = [
        result
        for result in results
        if result.harmful_influence
    ]

    positive = [
        result
        for result in results
        if result.validation_delta > 0
    ]

    neutral = [
        result
        for result in results
        if result.validation_delta == 0
    ]

    print("\nSummary:")
    print(
        f"  Clients analyzed: {len(results)}"
    )
    print(
        f"  Harmful influence: {len(harmful)}"
    )
    print(
        f"  Positive influence: {len(positive)}"
    )
    print(
        f"  Zero measured influence: {len(neutral)}"
    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert len(updates) == 20
    assert len(results) == 20

    for result in results:

        assert result.client_id
        assert result.sample_size == 1000

        assert 0.0 <= (
            result.validation_with_client
        ) <= 1.0

        assert 0.0 <= (
            result.validation_without_client
        ) <= 1.0

    print(
        "\n20-CLIENT L3 FEDERATION VALIDATION PASSED"
    )

    print("=" * 80)


if __name__ == "__main__":
    main()