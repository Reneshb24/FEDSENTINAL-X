"""
FedSentinel Federated Averaging.

FedAvg aggregates only the updates supplied to it.

Security responsibility:
    The caller must perform validation and quarantine before calling
    this module. This module never decides whether an update is safe.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Iterable

import torch

from backend.models.model_utils import StateDict
from backend.models.update import ModelUpdate


def fedavg(
    updates: Iterable[ModelUpdate],
) -> StateDict:
    """
    Aggregate model updates using example-weighted FedAvg.

    Each client's contribution is weighted according to its number
    of local training examples.

    Args:
        updates:
            Updates already approved for aggregation.

    Returns:
        Aggregated model delta.

    Raises:
        ValueError:
            If no updates are supplied or the update structures differ.
    """

    update_list = list(updates)

    if not update_list:
        raise ValueError(
            "At least one update is required for aggregation."
        )

    total_examples = sum(
        update.num_examples
        for update in update_list
    )

    if total_examples <= 0:
        raise ValueError(
            "Total number of examples must be greater than zero."
        )

    reference_keys = update_list[0].delta.keys()

    for update in update_list:

        if update.delta.keys() != reference_keys:
            raise ValueError(
                "All updates must contain identical parameter keys."
            )

    aggregated: StateDict = OrderedDict()

    for parameter_name in reference_keys:

        reference_tensor = update_list[0].delta[
            parameter_name
        ]

        if not torch.is_floating_point(
            reference_tensor
        ):
            aggregated[parameter_name] = (
                reference_tensor.detach()
                .cpu()
                .clone()
            )
            continue

        result = torch.zeros_like(
            reference_tensor.detach()
            .cpu()
            .float()
        )

        for update in update_list:

            tensor = update.delta[
                parameter_name
            ]

            if tensor.shape != reference_tensor.shape:
                raise ValueError(
                    f"Shape mismatch for parameter "
                    f"'{parameter_name}'."
                )

            weight = (
                update.num_examples
                / total_examples
            )

            result += (
                tensor.detach()
                .cpu()
                .float()
                * weight
            )

        aggregated[parameter_name] = result

    return aggregated