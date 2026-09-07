"""
Deterministic dimensionality reduction for model updates.

Random projection is used to create a compact representation while
preserving useful geometric relationships between updates.
"""

from __future__ import annotations

import torch
from torch import Tensor


# Layer 1 configuration.
DEFAULT_FINGERPRINT_DIM = 128
DEFAULT_PROJECTION_SEED = 42


def project_vector(
    vector: Tensor,
    output_dim: int = DEFAULT_FINGERPRINT_DIM,
    seed: int = DEFAULT_PROJECTION_SEED,
) -> Tensor:
    """
    Project a high-dimensional vector into a fixed lower-dimensional space.

    The projection matrix is generated deterministically from `seed`.
    """

    if output_dim <= 0:
        raise ValueError(
            "output_dim must be greater than zero."
        )

    vector = (
        vector.detach()
        .cpu()
        .float()
        .reshape(-1)
    )

    if vector.numel() == 0:
        return torch.zeros(
            output_dim,
            dtype=torch.float32,
        )

    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)

    projection = torch.randn(
        output_dim,
        vector.numel(),
        generator=generator,
        dtype=torch.float32,
    )

    projection /= vector.numel() ** 0.5

    return projection @ vector