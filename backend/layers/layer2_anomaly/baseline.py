"""
Robust baseline calculations for Layer 2 anomaly detection.

The baseline is calculated from the participating clients in a
federated round. Median and MAD are used because they are less
sensitive to extreme outliers than mean and standard deviation.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor


@dataclass(frozen=True)
class RobustBaseline:
    """Robust statistical baseline for a federation round."""

    median: Tensor
    mad: Tensor
    sample_count: int


def compute_median(
    vectors: list[Tensor],
) -> Tensor:
    """Compute the element-wise median of fingerprint vectors."""

    if not vectors:
        raise ValueError(
            "At least one fingerprint is required."
        )

    first_dimension = vectors[0].numel()

    if first_dimension == 0:
        raise ValueError(
            "Fingerprint vectors cannot be empty."
        )

    normalized = [
        vector.detach()
        .cpu()
        .float()
        .reshape(-1)
        for vector in vectors
    ]

    if any(
        vector.numel() != first_dimension
        for vector in normalized
    ):
        raise ValueError(
            "All fingerprint vectors must have "
            "the same dimension."
        )

    stacked = torch.stack(normalized)

    return torch.median(
        stacked,
        dim=0,
    ).values


def compute_mad(
    vectors: list[Tensor],
    median: Tensor | None = None,
) -> Tensor:
    """
    Compute element-wise Median Absolute Deviation.

    MAD = median(|x - median(x)|)
    """

    if not vectors:
        raise ValueError(
            "At least one fingerprint is required."
        )

    if median is None:
        median = compute_median(vectors)

    normalized = [
        vector.detach()
        .cpu()
        .float()
        .reshape(-1)
        for vector in vectors
    ]

    stacked = torch.stack(normalized)

    deviations = torch.abs(
        stacked - median
    )

    return torch.median(
        deviations,
        dim=0,
    ).values


def build_robust_baseline(
    vectors: list[Tensor],
) -> RobustBaseline:
    """Build a robust median/MAD baseline."""

    if not vectors:
        raise ValueError(
            "Cannot build a baseline from zero fingerprints."
        )

    median = compute_median(vectors)
    mad = compute_mad(
        vectors,
        median=median,
    )

    return RobustBaseline(
        median=median,
        mad=mad,
        sample_count=len(vectors),
    )