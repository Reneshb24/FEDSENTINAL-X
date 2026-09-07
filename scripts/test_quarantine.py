"""
FedSentinel quarantine integration test.

Verifies that an L2 outlier is removed from the aggregation set
while legitimate updates remain eligible.
"""

from backend.aggregation.quarantine import (
    QuarantineManager,
)
from backend.models.update import create_model_update
import torch


def create_test_update(
    client_id: str,
):
    """Create a small synthetic model update."""

    delta = {
        "layer.weight": torch.tensor(
            [0.1, 0.2, 0.3],
            dtype=torch.float32,
        ),
    }

    return create_model_update(
        update_id=f"round-001-{client_id}",
        client_id=client_id,
        round_id="round-001",
        delta=delta,
        num_examples=100,
    )


def main() -> None:

    print("=" * 70)
    print("FedSentinel — Quarantine Test")
    print("=" * 70)

    updates = [
        create_test_update("H1"),
        create_test_update("H2"),
        create_test_update("H3"),
        create_test_update("H4"),
        create_test_update("H5"),
    ]

    # Simulate evidence produced by L2.
    outlier_client_ids = {
        "H3",
    }

    manager = QuarantineManager(
        quarantine_outliers=True,
    )

    result = manager.apply(
        updates,
        outlier_client_ids=outlier_client_ids,
    )

    print("\nQuarantine results:")

    for decision in result.decisions:

        print(
            f"{decision.client_id}: "
            f"quarantined={decision.quarantined} | "
            f"action={decision.action.value} | "
            f"{decision.reason}"
        )

    print("\nSummary:")
    print(
        f"  Total updates: "
        f"{len(updates)}"
    )

    print(
        f"  Accepted: "
        f"{result.accepted_count}"
    )

    print(
        f"  Quarantined: "
        f"{result.quarantined_count}"
    )

    print(
        f"  Accepted clients: "
        f"{[u.client_id for u in result.accepted_updates]}"
    )

    print(
        f"  Quarantined clients: "
        f"{[u.client_id for u in result.quarantined_updates]}"
    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert result.accepted_count == 4

    assert result.quarantined_count == 1

    assert (
        result.quarantined_updates[0].client_id
        == "H3"
    )

    assert all(
        update.client_id != "H3"
        for update in result.accepted_updates
    )

    assert (
        result.quarantined_updates[0].client_id
        == "H3"
    )

    print(
        "\nQUARANTINE TEST PASSED"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()