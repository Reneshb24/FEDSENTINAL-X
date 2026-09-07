"""
FedSentinel robust aggregation test.

Verifies that coordinate-wise trimmed mean suppresses an extreme
model-update value.
"""

import torch

from backend.aggregation import trimmed_mean
from backend.models.update import create_model_update


def make_update(
    client_id: str,
    value: float,
):
    return create_model_update(
        update_id=f"round-001-{client_id}",
        client_id=client_id,
        round_id="round-001",
        delta={
            "layer.weight": torch.tensor(
                [value, value],
                dtype=torch.float32,
            )
        },
        num_examples=100,
    )


def main() -> None:

    print("=" * 70)
    print("FedSentinel — Robust Aggregation Test")
    print("=" * 70)

    updates = [
        make_update("H1", 1.0),
        make_update("H2", 1.1),
        make_update("H3", 0.9),
        make_update("H4", 1.2),
        make_update("H5", 0.8),
        make_update("H6", 1.0),
        make_update("H7", 1.1),
        make_update("H8", 0.9),
        make_update("H9", 1.0),
        make_update("H10", 100.0),
    ]

    print("\nClient update values:")

    for update in updates:

        print(
            f"  {update.client_id}: "
            f"{update.delta['layer.weight'][0].item():.2f}"
        )

    # ---------------------------------------------------------
    # Trim 10% from each side.
    #
    # 10 clients
    # → remove 1 lowest
    # → remove 1 highest
    #
    # In this test the highest value (100.0) is removed.
    # ---------------------------------------------------------

    aggregated = trimmed_mean(
        updates,
        trim_fraction=0.1,
    )

    value = aggregated[
        "layer.weight"
    ]

    print("\nRobust aggregate:")
    print(
        f"  {value.tolist()}"
    )

    # Sorted values:
    #
    # 0.8
    # 0.9
    # 0.9
    # 1.0
    # 1.0
    # 1.0
    # 1.1
    # 1.1
    # 1.2
    # 100.0
    #
    # After trimming:
    #
    # 0.9
    # 0.9
    # 1.0
    # 1.0
    # 1.0
    # 1.1
    # 1.1
    # 1.2
    #
    # Average = 1.025

    expected = 1.025

    print(
        f"\nExpected: "
        f"{expected:.6f}"
    )

    print(
        f"Actual:   "
        f"{value[0].item():.6f}"
    )

    assert torch.allclose(
        value,
        torch.tensor(
            [expected, expected],
            dtype=torch.float32,
        ),
        atol=1e-6,
    )

    print(
        "\nROBUST AGGREGATION TEST PASSED"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()