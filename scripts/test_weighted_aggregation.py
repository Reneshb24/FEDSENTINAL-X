"""
FedSentinel weighted aggregation test.
"""

import torch

from backend.aggregation import weighted_average
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
    print("FedSentinel — Weighted Aggregation Test")
    print("=" * 70)

    updates = [
        make_update("H1", 1.0),
        make_update("H2", 2.0),
        make_update("H3", 10.0),
    ]

    weights = {
        "H1": 1.0,
        "H2": 2.0,
        "H3": 0.0,
    }

    print("\nClient weights:")

    for client_id, weight in weights.items():
        print(
            f"  {client_id}: {weight}"
        )

    aggregated = weighted_average(
        updates,
        weights,
    )

    value = aggregated[
        "layer.weight"
    ]

    print("\nAggregated delta:")
    print(
        f"  {value.tolist()}"
    )

    # H3 has zero weight.
    #
    # (1×1 + 2×2 + 10×0) / (1+2+0)
    # = 5/3

    expected = 5.0 / 3.0

    assert torch.allclose(
        value,
        torch.tensor(
            [expected, expected],
            dtype=torch.float32,
        ),
        atol=1e-6,
    )

    print(
        f"\nExpected: {expected:.6f}"
    )

    print(
        f"Actual:   {value[0].item():.6f}"
    )

    print(
        "\nWEIGHTED AGGREGATION TEST PASSED"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()