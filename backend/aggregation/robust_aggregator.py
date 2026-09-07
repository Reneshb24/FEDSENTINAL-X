"""
FedSentinel robust aggregation.

Implements coordinate-wise trimmed-mean aggregation.

The aggregator operates only on updates that have already passed
the security pipeline's quarantine boundary.
"""

from __future__ import annotations

from collections import OrderedDict

import torch

from backend.models.model_utils import StateDict
from backend.models.update import ModelUpdate


def trimmed_mean(
    updates: list[ModelUpdate],
    trim_fraction: float = 0.1,
) -> StateDict:
    """
    Perform coordinate-wise trimmed-mean aggregation.

    For every model parameter:

        1. Collect the value from every accepted client.
        2. Sort values independently for each coordinate.
        3. Remove the configured fraction from both extremes.
        4. Average the remaining values.

    Args:
        updates:
            Updates already approved for aggregation.

        trim_fraction:
            Fraction removed from each side.

            Example:
                10 clients, 0.1
                -> remove 1 lowest and 1 highest value.

    Returns:
        Robustly aggregated model delta.
    """

    update_list = list(updates)

    if not update_list:
        raise ValueError(
            "At least one update is required."
        )

    if not 0.0 <= trim_fraction < 0.5:
        raise ValueError(
            "trim_fraction must be in [0, 0.5)."
        )

    reference_keys = update_list[0].delta.keys()

    for update in update_list:

        if update.delta.keys() != reference_keys:
            raise ValueError(
                "All updates must contain identical parameter keys."
            )

    client_count = len(update_list)

    trim_count = int(
        client_count * trim_fraction
    )

    remaining_count = (
        client_count
        - 2 * trim_count
    )

    if remaining_count <= 0:
        raise ValueError(
            "trim_fraction removes all available updates."
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

        tensors = []

        for update in update_list:

            tensor = (
                update.delta[
                    parameter_name
                ]
                .detach()
                .cpu()
                .float()
            )

            if tensor.shape != reference_tensor.shape:
                raise ValueError(
                    f"Shape mismatch for parameter "
                    f"'{parameter_name}'."
                )

            tensors.append(tensor)

        stacked = torch.stack(
            tensors,
            dim=0,
        )

        sorted_values, _ = torch.sort(
            stacked,
            dim=0,
        )

        if trim_count > 0:

            retained = sorted_values[
                trim_count:
                client_count - trim_count
            ]

        else:

            retained = sorted_values

        aggregated[parameter_name] = (
            retained.mean(dim=0)
        )

    return aggregated