"""
Peer similarity analysis for FedSentinel Layer 2.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor


@dataclass(frozen=True)
class PeerSimilarityResult:
    """Similarity statistics for one client against its peers."""

    mean_similarity: float
    minimum_similarity: float
    maximum_similarity: float
    peer_count: int


def _cosine_similarity(
    first: Tensor,
    second: Tensor,
) -> float:
    """Calculate cosine similarity between two vectors."""

    first = (
        first.detach()
        .cpu()
        .float()
        .reshape(-1)
    )

    second = (
        second.detach()
        .cpu()
        .float()
        .reshape(-1)
    )

    if first.numel() != second.numel():
        raise ValueError(
            "Vectors must have the same dimension."
        )

    if first.numel() == 0:
        return 0.0

    first_norm = torch.linalg.vector_norm(first)
    second_norm = torch.linalg.vector_norm(second)

    if (
        first_norm.item() == 0.0
        or second_norm.item() == 0.0
    ):
        return 0.0

    similarity = torch.dot(
        first,
        second,
    ) / (
        first_norm * second_norm
    )

    return float(
        torch.clamp(
            similarity,
            min=-1.0,
            max=1.0,
        ).item()
    )


def calculate_peer_similarity(
    fingerprint: Tensor,
    peers: list[Tensor],
) -> PeerSimilarityResult:
    """
    Compare one fingerprint against a collection of peer fingerprints.
    """

    if fingerprint.numel() == 0:
        raise ValueError(
            "Fingerprint cannot be empty."
        )

    if not peers:
        return PeerSimilarityResult(
            mean_similarity=0.0,
            minimum_similarity=0.0,
            maximum_similarity=0.0,
            peer_count=0,
        )

    similarities = [
        _cosine_similarity(
            fingerprint,
            peer,
        )
        for peer in peers
    ]

    values = torch.tensor(
        similarities,
        dtype=torch.float32,
    )

    return PeerSimilarityResult(
        mean_similarity=float(
            values.mean().item()
        ),
        minimum_similarity=float(
            values.min().item()
        ),
        maximum_similarity=float(
            values.max().item()
        ),
        peer_count=len(peers),
    )


def calculate_round_peer_similarity(
    fingerprints: dict[str, Tensor],
) -> dict[str, PeerSimilarityResult]:
    """
    Calculate peer similarity for every client in a round.

    The client being evaluated is excluded from its own peer set.
    """

    if not fingerprints:
        raise ValueError(
            "At least one fingerprint is required."
        )

    results: dict[str, PeerSimilarityResult] = {}

    for client_id, fingerprint in fingerprints.items():

        peers = [
            peer
            for peer_id, peer in fingerprints.items()
            if peer_id != client_id
        ]

        results[client_id] = calculate_peer_similarity(
            fingerprint,
            peers,
        )

    return results