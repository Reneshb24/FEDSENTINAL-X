"""
FedSentinel FedAvg test.

Verifies:
    1. Example-weighted averaging works.
    2. Quarantined updates can be excluded before aggregation.
"""

import torch

from backend.aggregation import fedavg
from backend.aggregation.quarantine import QuarantineManager
from backend.models.update import create_model_update


def make_update(
    client_id: str,
    value: float,
    num_examples: int,
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
        num_examples=num_examples,
    )


def main() -> None:

    print("=" * 70)
    print("FedSentinel — FedAvg Test")
    print("=" * 70)

    # ---------------------------------------------------------
    # Create updates
    # ---------------------------------------------------------

    updates = [
        make_update(
            "H1",
            value=1.0,
            num_examples=100,
        ),
        make_update(
            "H2",
            value=2.0,
            num_examples=200,
        ),
        make_update(
            "H3",
            value=100.0,
            num_examples=100,
        ),
    ]

    # ---------------------------------------------------------
    # Quarantine H3
    # ---------------------------------------------------------

    quarantine = QuarantineManager()

    quarantine_result = quarantine.apply(
        updates,
        outlier_client_ids={"H3"},
    )

    print("\nQuarantine:")
    print(
        f"  Accepted: "
        f"{[u.client_id for u in quarantine_result.accepted_updates]}"
    )
    print(
        f"  Quarantined: "
        f"{[u.client_id for u in quarantine_result.quarantined_updates]}"
    )

    # ---------------------------------------------------------
    # Aggregate only accepted updates
    # ---------------------------------------------------------

    aggregated = fedavg(
        quarantine_result.accepted_updates
    )

    value = aggregated[
        "layer.weight"
    ]

    print("\nAggregated delta:")
    print(
        f"  {value.tolist()}"
    )

    # ---------------------------------------------------------
    # Expected result
    #
    # H1 = 1.0 × 100
    # H2 = 2.0 × 200
    #
    # weighted average:
    #
    # (1×100 + 2×200) / 300
    # = 500 / 300
    # = 1.666666...
    # ---------------------------------------------------------

    expected = 5.0 / 3.0

    assert torch.allclose(
        value,
        torch.tensor(
            [expected, expected],
            dtype=torch.float32,
        ),
        atol=1e-6,
    )

    # ---------------------------------------------------------
    # Verify quarantined update had zero influence
    # ---------------------------------------------------------

    assert (
        quarantine_result.quarantined_count
        == 1
    )

    assert (
        quarantine_result.accepted_count
        == 2
    )

    print(
        "\nExpected weighted value:"
        f" {expected:.6f}"
    )

    print(
        "Actual weighted value:"
        f" {value[0].item():.6f}"
    )

    print(
        "\nFEDAVG TEST PASSED"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()