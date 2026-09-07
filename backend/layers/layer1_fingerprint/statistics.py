"""
Statistical features extracted from model updates.

These features summarize an update without exposing the complete raw
parameter vector to downstream detection logic.
"""

from __future__ import annotations

from typing import Mapping

import torch
from torch import Tensor

from backend.models.model_utils import state_dict_to_vector


def compute_update_statistics(
    state_dict: Mapping[str, Tensor],
) -> dict[str, float | int]:
    """
    Compute deterministic statistical features for a model update.

    Returns:
        Dictionary containing:
        - parameter_count
        - l2_norm
        - mean
        - standard_deviation
        - minimum
        - maximum
        - absolute_mean
        - zero_fraction
    """

    vector = state_dict_to_vector(state_dict)

    if vector.numel() == 0:
        return {
            "parameter_count": 0,
            "l2_norm": 0.0,
            "mean": 0.0,
            "standard_deviation": 0.0,
            "minimum": 0.0,
            "maximum": 0.0,
            "absolute_mean": 0.0,
            "zero_fraction": 1.0,
        }

    vector = vector.float()

    parameter_count = int(vector.numel())

    l2_norm = float(
        torch.linalg.vector_norm(vector).item()
    )

    mean = float(vector.mean().item())

    # std(unbiased=False) avoids NaN for a one-element vector.
    standard_deviation = float(
        vector.std(unbiased=False).item()
    )

    minimum = float(vector.min().item())
    maximum = float(vector.max().item())

    absolute_mean = float(
        vector.abs().mean().item()
    )

    zero_fraction = float(
        (vector == 0).float().mean().item()
    )

    return {
        "parameter_count": parameter_count,
        "l2_norm": l2_norm,
        "mean": mean,
        "standard_deviation": standard_deviation,
        "minimum": minimum,
        "maximum": maximum,
        "absolute_mean": absolute_mean,
        "zero_fraction": zero_fraction,
    }