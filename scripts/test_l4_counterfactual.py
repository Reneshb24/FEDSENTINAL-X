from __future__ import annotations

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from backend.layers.layer4_counterfactual.counterfactual import (
    CounterfactualAnalyzer,
)
from backend.models.update import create_model_update


class TinyModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear = nn.Linear(2, 2, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear(x)


def model_factory() -> nn.Module:
    return TinyModel()


def main() -> None:
    print("=" * 80)
    print("FedSentinel - Layer 4 Controlled Counterfactual Test")
    print("=" * 80)

    validation_x = torch.tensor(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0],
            [0.0, 1.0],
        ]
    )

    validation_y = torch.tensor(
        [0, 1, 0, 1]
    )

    validation_dataset = TensorDataset(
        validation_x,
        validation_y,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=4,
        shuffle=False,
    )

    global_state = {
        "linear.weight": torch.tensor(
            [
                [2.0, 0.0],
                [0.0, 2.0],
            ]
        )
    }

    benign_delta = torch.zeros(
        2,
        2,
    )

    harmful_delta = torch.tensor(
        [
            [-5.0, 0.0],
            [0.0, -5.0],
        ]
    )

    updates = [
        create_model_update(
            update_id="controlled-h1-update",
            client_id="H1",
            round_id="controlled-round",
            delta={
                "linear.weight": benign_delta,
            },
            num_examples=100,
        ),
        create_model_update(
            update_id="controlled-h2-update",
            client_id="H2",
            round_id="controlled-round",
            delta={
                "linear.weight": harmful_delta,
            },
            num_examples=100,
        ),
    ]

    analyzer = CounterfactualAnalyzer(
        model_factory=model_factory,
        validation_loader=validation_loader,
        device="cpu",
    )

    results = analyzer.analyze(
        global_state=global_state,
        updates=updates,
    )

    print()
    print("-" * 80)

    for client_id, result in results.items():
        print(
            f"{client_id} | "
            f"with={result.with_client.accuracy:.4f} | "
            f"without={result.without_client.accuracy:.4f} | "
            f"accuracy_delta={result.accuracy_delta:+.4f} | "
            f"loss_delta={result.loss_delta:+.4f} | "
            f"harmful={result.harmful_counterfactual}"
        )
        print(f"     {result.reason}")

    print("-" * 80)

    attack_result = results["H2"]

    print()
    print("Expected behavior:")
    print(
        f"  H2 accuracy improves when removed: "
        f"{attack_result.improvement_without_client}"
    )
    print(
        f"  H2 harmful counterfactual: "
        f"{attack_result.harmful_counterfactual}"
    )

    assert attack_result.improvement_without_client
    assert attack_result.harmful_counterfactual

    print()
    print("L4 CONTROLLED VALIDATION PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()
