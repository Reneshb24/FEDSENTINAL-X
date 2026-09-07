"""
FedSentinel Layer 3 controlled influence test.

This test verifies that leave-one-out influence analysis works
on real neural-network model updates.

The test uses a small validation subset to keep execution fast.
"""

import torch

from backend.layers.layer3_influence import (
    InfluenceAnalyzer,
    create_validation_loader,
)
from backend.models.cnn import FedSentinelCNN
from backend.models.model_utils import clone_state_dict
from backend.models.update import create_model_update
from data.dataset import load_mnist_test


def model_factory():
    """Create a fresh FedSentinel CNN."""
    return FedSentinelCNN()


def make_update(
    client_id: str,
    value: float,
):
    """
    Create a synthetic model update.

    The same scalar perturbation is applied to every floating-point
    parameter so that the test remains deterministic.
    """

    model = model_factory()

    delta = {}

    for name, tensor in model.state_dict().items():

        if torch.is_floating_point(tensor):

            delta[name] = torch.full_like(
                tensor,
                value,
            )

        else:

            delta[name] = tensor.detach().cpu().clone()

    return create_model_update(
        update_id=f"l3-test-{client_id}",
        client_id=client_id,
        round_id="l3-test-round",
        delta=delta,
        num_examples=100,
    )


def main() -> None:

    print("=" * 70)
    print("FedSentinel — Layer 3 Controlled Influence Test")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Load validation data
    # ---------------------------------------------------------

    print("\n[1/4] Loading MNIST test dataset...")

    dataset = load_mnist_test()

    print(
        f"Test samples available: "
        f"{len(dataset)}"
    )

    validation_loader = create_validation_loader(
        dataset=dataset,
        sample_size=100,
        batch_size=32,
        seed=42,
    )

    print(
        "Validation subset: 100 samples"
    )

    # ---------------------------------------------------------
    # 2. Create baseline model
    # ---------------------------------------------------------

    print("\n[2/4] Creating baseline model...")

    model = model_factory()

    global_state = clone_state_dict(
        model.state_dict()
    )

    print(
        f"Parameters: "
        f"{sum(p.numel() for p in model.parameters())}"
    )

    # ---------------------------------------------------------
    # 3. Create controlled updates
    # ---------------------------------------------------------

    print("\n[3/4] Creating controlled updates...")

    updates = [
        make_update("H1", 0.00001),
        make_update("H2", 0.00001),
        make_update("H3", 0.00001),
    ]

    print(
        f"Updates created: "
        f"{len(updates)}"
    )

    # ---------------------------------------------------------
    # 4. Run influence analysis
    # ---------------------------------------------------------

    print("\n[4/4] Running L3 influence analysis...")

    analyzer = InfluenceAnalyzer(
        model_factory=model_factory,
        validation_loader=validation_loader,
        device="cpu",
    )

    results = analyzer.analyze(
        global_state=global_state,
        updates=updates,
    )

    # ---------------------------------------------------------
    # Display results
    # ---------------------------------------------------------

    print("\nInfluence results:")
    print("-" * 90)

    for result in results:

        print(
            f"{result.client_id:>4} | "
            f"with={result.validation_with_client:.4f} | "
            f"without={result.validation_without_client:.4f} | "
            f"delta={result.validation_delta:+.4f} | "
            f"score={result.influence_score:+.2f} | "
            f"harmful={result.harmful_influence}"
        )

    print("-" * 90)

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert len(results) == 3

    for result in results:

        assert result.client_id in {
            "H1",
            "H2",
            "H3",
        }

        assert result.sample_size == 100

    print(
        "\nL3 CONTROLLED INFLUENCE TEST PASSED"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()