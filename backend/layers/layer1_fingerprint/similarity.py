"""
Similarity calculations between update fingerprints.
"""

from __future__ import annotations

from collections.abc import Sequence

import torch
from torch import Tensor

from backend.models.model_utils import vector_cosine_similarity


def cosine_similarity(
    first: Tensor,
    second: Tensor,
) -> float:
    """Return cosine similarity in the range [-1, 1]."""

    return vector_cosine_similarity(first, second)


def mean_peer_similarity(
    fingerprint: Tensor,
    peer_fingerprints: Sequence[Tensor],
) -> float:
    """
    Calculate the mean cosine similarity between an update and its peers.

    The update itself should not be included in `peer_fingerprints`.
    """

    if not peer_fingerprints:
        return 0.0

    similarities = [
        cosine_similarity(fingerprint, peer)
        for peer in peer_fingerprints
    ]

    return float(
        torch.tensor(similarities, dtype=torch.float32)
        .mean()
        .item()
    )


def distance_from_baseline(
    fingerprint: Tensor,
    baseline: Tensor,
) -> float:
    """
    Calculate Euclidean distance from a reference fingerprint.
    """

    if fingerprint.numel() != baseline.numel():
        raise ValueError(
            "Fingerprint and baseline must have the same dimension."
        )

    if fingerprint.numel() == 0:
        return 0.0

    difference = (
        fingerprint.detach().cpu().float()
        - baseline.detach().cpu().float()
    )

    return float(
        torch.linalg.vector_norm(difference).item()
    )