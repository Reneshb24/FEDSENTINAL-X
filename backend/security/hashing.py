"""
Cryptographic hashing utilities for FedSentinel.

Hashes provide deterministic identities for security-sensitive artifacts.

The hashing layer does NOT decide whether an update is malicious.
It only establishes integrity/provenance evidence that later security
layers can use.

Supported algorithms are intentionally restricted to well-known
cryptographic hash functions.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

import torch
from torch import Tensor


DEFAULT_HASH_ALGORITHM = "sha256"

SUPPORTED_HASH_ALGORITHMS = frozenset(
    {
        "sha256",
        "sha512",
    }
)


def _get_hash_function(
    algorithm: str,
) -> "hashlib._Hash":
    """
    Create a hashlib object for the requested algorithm.
    """

    algorithm = algorithm.lower().strip()

    if algorithm not in SUPPORTED_HASH_ALGORITHMS:
        raise ValueError(
            f"Unsupported hash algorithm: {algorithm}. "
            f"Supported algorithms: "
            f"{sorted(SUPPORTED_HASH_ALGORITHMS)}"
        )

    return hashlib.new(algorithm)


def hash_bytes(
    data: bytes,
    algorithm: str = DEFAULT_HASH_ALGORITHM,
) -> str:
    """
    Calculate the hexadecimal hash of raw bytes.
    """

    if not isinstance(data, bytes):
        raise TypeError(
            "data must be bytes."
        )

    digest = _get_hash_function(
        algorithm
    )

    digest.update(data)

    return digest.hexdigest()


def hash_file(
    path: Path,
    algorithm: str = DEFAULT_HASH_ALGORITHM,
    chunk_size: int = 1024 * 1024,
) -> str:
    """
    Calculate the cryptographic hash of a file.

    Files are processed in chunks to avoid loading large artifacts
    completely into memory.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"File does not exist: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be positive."
        )

    digest = _get_hash_function(
        algorithm
    )

    with path.open("rb") as file:
        while True:
            chunk = file.read(chunk_size)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def hash_tensor(
    tensor: Tensor,
    algorithm: str = DEFAULT_HASH_ALGORITHM,
) -> str:
    """
    Calculate a deterministic hash for a tensor.

    The hash includes:

        - tensor dtype
        - tensor shape
        - tensor raw bytes

    The tensor is moved to CPU and detached before hashing.

    This function does not serialize arbitrary Python objects.
    """

    if not isinstance(tensor, Tensor):
        raise TypeError(
            "tensor must be a torch.Tensor."
        )

    tensor = (
        tensor.detach()
        .cpu()
        .contiguous()
    )

    digest = _get_hash_function(
        algorithm
    )

    digest.update(
        str(tensor.dtype).encode("utf-8")
    )

    digest.update(
        repr(tuple(tensor.shape)).encode("utf-8")
    )

    digest.update(
        tensor.numpy().tobytes()
    )

    return digest.hexdigest()


def hash_state_dict(
    state_dict: Mapping[str, Tensor],
    algorithm: str = DEFAULT_HASH_ALGORITHM,
) -> str:
    """
    Calculate a deterministic hash for an entire model state dictionary.

    Parameter names are sorted before hashing so the resulting hash
    does not depend on dictionary insertion order.

    Each parameter contributes:

        parameter name
        parameter dtype
        parameter shape
        parameter raw bytes
    """

    if not state_dict:
        raise ValueError(
            "state_dict must not be empty."
        )

    digest = _get_hash_function(
        algorithm
    )

    for name in sorted(state_dict.keys()):

        tensor = state_dict[name]

        if not isinstance(tensor, Tensor):
            raise TypeError(
                f"State entry '{name}' is not a torch.Tensor."
            )

        tensor = (
            tensor.detach()
            .cpu()
            .contiguous()
        )

        digest.update(
            name.encode("utf-8")
        )

        digest.update(
            str(tensor.dtype).encode("utf-8")
        )

        digest.update(
            repr(tuple(tensor.shape)).encode("utf-8")
        )

        digest.update(
            tensor.numpy().tobytes()
        )

    return digest.hexdigest()


def hash_model_update(
    delta: Mapping[str, Tensor],
    algorithm: str = DEFAULT_HASH_ALGORITHM,
) -> str:
    """
    Calculate the deterministic security hash of a model update.

    A model update is treated as a state dictionary containing parameter
    deltas.

    This hash can later be used for:

        - duplicate detection
        - replay detection
        - provenance
        - evidence records
        - incident investigation
        - audit trails
    """

    return hash_state_dict(
        state_dict=delta,
        algorithm=algorithm,
    )