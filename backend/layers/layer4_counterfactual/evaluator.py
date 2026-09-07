from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
from torch.utils.data import DataLoader


@dataclass(frozen=True)
class EvaluationResult:
    """Validation metrics for a model."""

    accuracy: float
    average_loss: float
    sample_count: int


def evaluate_model(
    model: nn.Module,
    data_loader: DataLoader,
    device: str = "cpu",
) -> EvaluationResult:
    """
    Evaluate a model on a validation loader.

    Returns accuracy, average cross-entropy loss, and
    number of evaluated samples.
    """
    model = model.to(device)
    model.eval()

    criterion = nn.CrossEntropyLoss(reduction="sum")

    correct = 0
    total = 0
    total_loss = 0.0

    with torch.no_grad():
        for inputs, targets in data_loader:
            inputs = inputs.to(device)
            targets = targets.to(device)

            outputs = model(inputs)
            loss = criterion(outputs, targets)

            predictions = outputs.argmax(dim=1)

            correct += int((predictions == targets).sum().item())
            total += int(targets.size(0))
            total_loss += float(loss.item())

    if total == 0:
        raise ValueError("Validation loader contains no samples.")

    return EvaluationResult(
        accuracy=correct / total,
        average_loss=total_loss / total,
        sample_count=total,
    )
