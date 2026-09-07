"""
FedSentinel Layer 3 influence analysis.

L3 measures how much an individual client update changes validation
performance relative to an aggregate that excludes that client.

This is evidence, not a maliciousness verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import torch
from torch import nn
from torch.utils.data import DataLoader

from backend.aggregation import fedavg
from backend.models.model_utils import (
    apply_model_delta,
    clone_state_dict,
)
from backend.models.update import ModelUpdate


@dataclass(frozen=True)
class InfluenceResult:
    """
    Influence evidence for one client.
    """

    client_id: str

    influence_score: float

    validation_delta: float

    validation_with_client: float

    validation_without_client: float

    sample_size: int

    harmful_influence: bool

    reason: str


def evaluate_model(
    model: nn.Module,
    data_loader: DataLoader,
    device: str = "cpu",
) -> tuple[float, float, int]:
    """
    Evaluate classification accuracy and loss.

    Returns:
        accuracy, average_loss, sample_count
    """

    model = model.to(device)

    model.eval()

    criterion = nn.CrossEntropyLoss(
        reduction="sum"
    )

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():

        for inputs, targets in data_loader:

            inputs = inputs.to(device)
            targets = targets.to(device)

            outputs = model(inputs)

            loss = criterion(
                outputs,
                targets,
            )

            total_loss += float(
                loss.item()
            )

            predictions = outputs.argmax(
                dim=1
            )

            correct += int(
                (predictions == targets)
                .sum()
                .item()
            )

            total += int(
                targets.numel()
            )

    if total == 0:
        raise ValueError(
            "Validation loader contains no samples."
        )

    accuracy = correct / total

    average_loss = total_loss / total

    return (
        float(accuracy),
        float(average_loss),
        total,
    )


class InfluenceAnalyzer:
    """
    Measure individual update influence using leave-one-out evaluation.
    """

    def __init__(
        self,
        model_factory,
        validation_loader: DataLoader,
        device: str = "cpu",
    ) -> None:

        if model_factory is None:
            raise ValueError(
                "model_factory must not be None."
            )

        self.model_factory = model_factory

        self.validation_loader = (
            validation_loader
        )

        self.device = device

    def _evaluate_state(
        self,
        state_dict,
    ) -> tuple[float, float, int]:

        model = self.model_factory()

        model.load_state_dict(
            state_dict,
            strict=True,
        )

        return evaluate_model(
            model=model,
            data_loader=self.validation_loader,
            device=self.device,
        )

    def analyze(
        self,
        global_state,
        updates: Sequence[ModelUpdate],
    ) -> list[InfluenceResult]:
        """
        Calculate leave-one-out influence for every client.

        The comparison is:

            validation(with client)
            -
            validation(without client)

        A negative value means that including the client reduced
        validation accuracy.
        """

        update_list = list(updates)

        if len(update_list) < 2:
            raise ValueError(
                "At least two updates are required."
            )

        # -----------------------------------------------------
        # Aggregate all accepted updates.
        # -----------------------------------------------------

        full_delta = fedavg(
            update_list
        )

        full_state = apply_model_delta(
            global_state,
            full_delta,
        )

        (
            full_accuracy,
            _,
            sample_size,
        ) = self._evaluate_state(
            full_state
        )

        results: list[InfluenceResult] = []

        # -----------------------------------------------------
        # Leave-one-out evaluation.
        # -----------------------------------------------------

        for target in update_list:

            remaining = [
                update
                for update in update_list
                if update.update_id
                != target.update_id
            ]

            without_delta = fedavg(
                remaining
            )

            without_state = apply_model_delta(
                global_state,
                without_delta,
            )

            (
                without_accuracy,
                _,
                _,
            ) = self._evaluate_state(
                without_state
            )

            validation_delta = (
                full_accuracy
                - without_accuracy
            )

            # Convert accuracy delta to a human-friendly
            # percentage-point score.
            influence_score = (
                validation_delta
                * 100.0
            )

            harmful = (
                validation_delta < 0.0
            )

            if harmful:

                reason = (
                    "Including this client reduced "
                    "validation accuracy relative to "
                    "the leave-one-out aggregate."
                )

            elif validation_delta > 0.0:

                reason = (
                    "Including this client improved "
                    "validation accuracy relative to "
                    "the leave-one-out aggregate."
                )

            else:

                reason = (
                    "Including this client produced no "
                    "measurable validation-accuracy change."
                )

            results.append(
                InfluenceResult(
                    client_id=target.client_id,
                    influence_score=float(
                        influence_score
                    ),
                    validation_delta=float(
                        validation_delta
                    ),
                    validation_with_client=float(
                        full_accuracy
                    ),
                    validation_without_client=float(
                        without_accuracy
                    ),
                    sample_size=sample_size,
                    harmful_influence=harmful,
                    reason=reason,
                )
            )

        return results