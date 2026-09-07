"""
FedSentinel weighted model-update aggregation.

This module provides the generic weighted aggregation primitive used
by FedAvg and later trust-aware aggregation.

Security decisions are deliberately outside this module.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Mapping

import torch

from backend.models.model_utils import StateDict
from backend.models.update import ModelUpdate


def weighted_average(
    updates: list[ModelUpdate],
    weights: Mapping[str, float],
) -> StateDict:
    """
    Aggregate model updates using explicit client weights.

    Args:
        updates:
            Updates already approved for aggregation.

        weights:
            Mapping from client ID to non-negative aggregation weight.

    Returns:
        Weighted average model delta.
    """

    if not updates:
        raise ValueError(
            "At least one update is required."
        )

    if not weights:
        raise ValueError(
            "At least one aggregation weight is required."
        )

    reference_keys = updates[0].delta.keys()

    effective_weights: dict[str, float] = {}

    for update in updates:

        if update.client_id not in weights:
            raise ValueError(
                f"Missing aggregation weight for "
                f"client '{update.client_id}'."
            )

        weight = float(
            weights[update.client_id]
        )

        if weight < 0:
            raise ValueError(
                "Aggregation weights must be non-negative."
            )

        effective_weights[
            update.client_id
        ] = weight

        if update.delta.keys() != reference_keys:
            raise ValueError(
                "All updates must contain identical parameter keys."
            )

    total_weight = sum(
        effective_weights.values()
    )

    if total_weight <= 0:
        raise ValueError(
            "Total aggregation weight must be greater than zero."
        )

    aggregated: StateDict = OrderedDict()

    for parameter_name in reference_keys:

        reference_tensor = updates[0].delta[
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

        for update in updates:

            tensor = update.delta[
                parameter_name
            ]

            if tensor.shape != reference_tensor.shape:
                raise ValueError(
                    f"Shape mismatch for parameter "
                    f"'{parameter_name}'."
                )

            client_weight = (
                effective_weights[
                    update.client_id
                ]
                / total_weight
            )

            result += (
                tensor.detach()
                .cpu()
                .float()
                * client_weight
            )

        aggregated[parameter_name] = result

    return aggregated