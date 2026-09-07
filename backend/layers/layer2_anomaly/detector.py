"""
FedSentinel Layer 2 robust anomaly detector.

L2 combines robust statistical deviation and peer disagreement.
It produces anomaly evidence, not a final malicious verdict.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor

from .adaptive_threshold import (
    anomaly_score_from_z,
    is_outlier,
    robust_z_score,
)
from .baseline import (
    RobustBaseline,
    build_robust_baseline,
)
from .peer_similarity import (
    PeerSimilarityResult,
    calculate_round_peer_similarity,
)


@dataclass(frozen=True)
class Layer2Detection:
    """Layer 2 result for one client update."""

    client_id: str

    anomaly_score: float
    z_score: float

    is_outlier: bool

    peer_similarity: float
    peer_count: int

    minimum_peer_similarity: float
    maximum_peer_similarity: float

    baseline_distance: float

    reason: str


@dataclass(frozen=True)
class Layer2RoundResult:
    """Layer 2 results for an entire federation round."""

    baseline: RobustBaseline
    detections: dict[str, Layer2Detection]


def _euclidean_distance(
    vector: Tensor,
    baseline: Tensor,
) -> float:
    """Calculate Euclidean distance from the baseline."""

    vector = (
        vector.detach()
        .cpu()
        .float()
        .reshape(-1)
    )

    baseline = (
        baseline.detach()
        .cpu()
        .float()
        .reshape(-1)
    )

    if vector.numel() != baseline.numel():
        raise ValueError(
            "Vector and baseline must have the same dimension."
        )

    if vector.numel() == 0:
        return 0.0

    return float(
        torch.linalg.vector_norm(
            vector - baseline
        ).item()
    )


def _build_reason(
    *,
    anomaly_score: float,
    z_score: float,
    peer_similarity: float,
    is_outlier_result: bool,
) -> str:
    """Create an evidence-oriented explanation."""

    if not is_outlier_result:
        if peer_similarity < 0.0:
            return (
                "Update is not a statistical outlier, "
                "but shows below-average agreement with peers."
            )

        return (
            "Update remains within the robust round baseline."
        )

    if peer_similarity < 0.0:
        return (
            "Update is a robust statistical outlier and "
            "shows disagreement with federation peers."
        )

    if peer_similarity < 0.5:
        return (
            "Update is a robust statistical outlier with "
            "weak peer agreement."
        )

    return (
        "Update is a robust statistical outlier relative "
        "to the current federation baseline."
    )


class Layer2Detector:
    """
    Detect anomalous model updates using the complete federation
    participant set.

    This detector intentionally does not classify clients as
    malicious. It produces anomaly evidence for later layers.
    """

    def __init__(
        self,
        z_threshold: float = 3.0,
    ) -> None:

        if z_threshold <= 0:
            raise ValueError(
                "z_threshold must be greater than zero."
            )

        self.z_threshold = z_threshold

    def detect_round(
        self,
        fingerprints: dict[str, Tensor],
    ) -> Layer2RoundResult:
        """
        Analyze all fingerprints participating in a round.

        Args:
            fingerprints:
                Mapping from client ID to 128-dimensional
                L1 fingerprint.
        """

        if not fingerprints:
            raise ValueError(
                "At least one fingerprint is required."
            )

        vectors = list(
            fingerprints.values()
        )

        baseline = build_robust_baseline(
            vectors
        )

        peer_results = calculate_round_peer_similarity(
            fingerprints
        )

        detections: dict[str, Layer2Detection] = {}

        for client_id, fingerprint in fingerprints.items():

            z_score = robust_z_score(
                fingerprint,
                baseline.median,
                baseline.mad,
            )

            anomaly_score = anomaly_score_from_z(
                z_score
            )

            outlier = is_outlier(
                z_score,
                threshold=self.z_threshold,
            )

            peer: PeerSimilarityResult = (
                peer_results[client_id]
            )

            baseline_distance = _euclidean_distance(
                fingerprint,
                baseline.median,
            )

            reason = _build_reason(
                anomaly_score=anomaly_score,
                z_score=z_score,
                peer_similarity=peer.mean_similarity,
                is_outlier_result=outlier,
            )

            detections[client_id] = Layer2Detection(
                client_id=client_id,
                anomaly_score=anomaly_score,
                z_score=z_score,
                is_outlier=outlier,
                peer_similarity=peer.mean_similarity,
                peer_count=peer.peer_count,
                minimum_peer_similarity=(
                    peer.minimum_similarity
                ),
                maximum_peer_similarity=(
                    peer.maximum_similarity
                ),
                baseline_distance=baseline_distance,
                reason=reason,
            )

        return Layer2RoundResult(
            baseline=baseline,
            detections=detections,
        )