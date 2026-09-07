"""
FedSentinel Layer 1 fingerprint generation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import hashlib

import torch

from backend.models.update import ModelUpdate

from .projection import (
    DEFAULT_FINGERPRINT_DIM,
    DEFAULT_PROJECTION_SEED,
    project_vector,
)
from .similarity import (
    distance_from_baseline,
    mean_peer_similarity,
)
from .statistics import compute_update_statistics


@dataclass(frozen=True)
class FingerprintResult:
    """Complete Layer 1 fingerprint result."""

    vector: torch.Tensor
    dimension: int
    vector_hash: str

    l2_norm: float
    mean: float
    standard_deviation: float

    peer_similarity: float
    distance_from_baseline: float

    generated_at: datetime


def _hash_vector(vector: torch.Tensor) -> str:
    """
    Generate a deterministic SHA-256 hash for a fingerprint vector.
    """

    vector = (
        vector.detach()
        .cpu()
        .float()
        .contiguous()
    )

    return hashlib.sha256(
        vector.numpy().tobytes()
    ).hexdigest()


class FingerprintGenerator:
    """
    Generate privacy-safe fingerprints for model updates.
    """

    def __init__(
        self,
        fingerprint_dim: int = DEFAULT_FINGERPRINT_DIM,
        projection_seed: int = DEFAULT_PROJECTION_SEED,
    ) -> None:

        if fingerprint_dim <= 0:
            raise ValueError(
                "fingerprint_dim must be greater than zero."
            )

        self.fingerprint_dim = fingerprint_dim
        self.projection_seed = projection_seed

    def generate(
        self,
        update: ModelUpdate,
        *,
        peer_fingerprints: list[torch.Tensor] | None = None,
        baseline: torch.Tensor | None = None,
    ) -> FingerprintResult:

        vector = update.vector

        projected = project_vector(
            vector,
            output_dim=self.fingerprint_dim,
            seed=self.projection_seed,
        )

        statistics = compute_update_statistics(
            update.delta
        )

        peers = peer_fingerprints or []

        peer_similarity = mean_peer_similarity(
            projected,
            peers,
        )

        if baseline is None:
            baseline_distance = 0.0
        else:
            baseline_distance = distance_from_baseline(
                projected,
                baseline,
            )

        return FingerprintResult(
            vector=projected,
            dimension=int(projected.numel()),
            vector_hash=_hash_vector(projected),
            l2_norm=float(statistics["l2_norm"]),
            mean=float(statistics["mean"]),
            standard_deviation=float(
                statistics["standard_deviation"]
            ),
            peer_similarity=peer_similarity,
            distance_from_baseline=baseline_distance,
            generated_at=datetime.now(timezone.utc),
        )