"""
Adaptive anomaly scoring for FedSentinel Layer 2.

Uses robust z-scores based on Median Absolute Deviation (MAD).
"""

from __future__ import annotations

import torch
from torch import Tensor


# Prevent division by zero when MAD is extremely small.
MAD_SCALE = 1.4826

# Small numerical stability constant.
EPSILON = 1e-8


def robust_z_score(
    vector: Tensor,
    median: Tensor,
    mad: Tensor,
) -> float:
    """
    Calculate a robust z-score for a fingerprint.

    The score represents how far the fingerprint is from the
    robust median baseline after accounting for the MAD.

    A larger absolute value indicates greater deviation.
    """

    vector = (
        vector.detach()
        .cpu()
        .float()
        .reshape(-1)
    )

    median = (
        median.detach()
        .cpu()
        .float()
        .reshape(-1)
    )

    mad = (
        mad.detach()
        .cpu()
        .float()
        .reshape(-1)
    )

    if vector.numel() != median.numel():
        raise ValueError(
            "Vector and median must have the same dimension."
        )

    if vector.numel() != mad.numel():
        raise ValueError(
            "Vector and MAD must have the same dimension."
        )

    if vector.numel() == 0:
        return 0.0

    scaled_mad = (
        MAD_SCALE * mad
    ).clamp_min(EPSILON)

    standardized = (
        torch.abs(vector - median)
        / scaled_mad
    )

    # Use the median robust deviation as the aggregate score.
    score = torch.median(
        standardized
    )

    return float(score.item())


def anomaly_score_from_z(
    z_score: float,
) -> float:
    """
    Convert a robust z-score into a 0-100 anomaly score.

    The mapping is intentionally smooth rather than using a hard
    malicious/not-malicious threshold.
    """

    if z_score < 0:
        z_score = abs(z_score)

    # Smoothly approaches 100 as z increases.
    score = 100.0 * (
        1.0 - 1.0 / (1.0 + z_score)
    )

    return max(
        0.0,
        min(100.0, score),
    )


def is_outlier(
    z_score: float,
    threshold: float = 3.0,
) -> bool:
    """
    Determine whether a robust z-score exceeds the configured
    anomaly threshold.
    """

    if threshold <= 0:
        raise ValueError(
            "threshold must be greater than zero."
        )

    return abs(z_score) >= threshold