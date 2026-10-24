"""
FedSentinel global model artifact storage.

This service provides safe persistence and retrieval of model state
dictionaries using the safetensors format.

Responsibilities:
    - Save model state dictionaries as .safetensors artifacts.
    - Load model state dictionaries safely.
    - Verify model integrity against the existing FedSentinel hash.
    - Provide deterministic artifact locations.

This service does NOT:
    - decide whether a model is malicious
    - decide trust
    - perform aggregation
    - perform L0-L5 analysis
    - modify federation membership

Security principle:

    MODEL HASH != MODEL STORAGE

The hash establishes integrity identity.
The artifact provides the actual recoverable model state.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import torch
from torch import Tensor
from safetensors.torch import load_file, save_file

from backend.models.model_utils import StateDict, clone_state_dict
from backend.security.hashing import hash_state_dict


class ModelArtifactService:
    """
    Persist and retrieve FedSentinel global model artifacts.

    Artifacts are stored outside the database.

    Example:

        data/model_artifacts/
            <model_name>/
                round-1.safetensors
                round-2.safetensors
    """

    DEFAULT_STORAGE_ROOT = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "model_artifacts"
    )

    ARTIFACT_EXTENSION = ".safetensors"

    def __init__(
        self,
        storage_root: Path | str | None = None,
    ) -> None:

        self.storage_root = Path(
            storage_root
            if storage_root is not None
            else self.DEFAULT_STORAGE_ROOT
        )

        self.storage_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =========================================================
    # Path helpers
    # =========================================================

    @staticmethod
    def _safe_component(
        value: str,
        field_name: str,
    ) -> str:
        """
        Validate a path component.

        Only deterministic filesystem-safe characters are accepted.
        """

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        value = value.strip()

        if not value:
            raise ValueError(
                f"{field_name} cannot be empty."
            )
        value = value.replace(" ", "-")

        allowed = (
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789"
            "._-"
        )

        if any(
            character not in allowed
            for character in value
        ):
            raise ValueError(
                f"{field_name} contains unsupported characters."
            )

        return value

    def artifact_path(
        self,
        *,
        model_name: str,
        version: str,
    ) -> Path:
        """
        Return the deterministic artifact path.

        Example:

            data/model_artifacts/
                FedSentinel/
                    round-1.safetensors
        """

        safe_model_name = self._safe_component(
            model_name,
            "model_name",
        )

        safe_version = self._safe_component(
            version,
            "version",
        )

        model_directory = (
            self.storage_root
            / safe_model_name
        )

        return (
            model_directory
            / f"{safe_version}{self.ARTIFACT_EXTENSION}"
        )

    # =========================================================
    # Validation
    # =========================================================

    @staticmethod
    def _validate_state_dict(
        state_dict: Mapping[str, Tensor],
    ) -> None:
        """
        Validate that the supplied state dictionary is suitable
        for safe tensor storage.
        """

        if not state_dict:
            raise ValueError(
                "state_dict must not be empty."
            )

        for name, tensor in state_dict.items():

            if not isinstance(name, str):
                raise TypeError(
                    "State dictionary parameter names must be strings."
                )

            if not isinstance(tensor, Tensor):
                raise TypeError(
                    f"State entry '{name}' must be a torch.Tensor."
                )

            if tensor.layout != torch.strided:
                raise ValueError(
                    f"State entry '{name}' must use strided tensor storage."
                )

            if tensor.is_sparse:
                raise ValueError(
                    f"State entry '{name}' cannot be sparse."
                )

            if tensor.numel() == 0:
                raise ValueError(
                    f"State entry '{name}' cannot be empty."
                )

    # =========================================================
    # Save
    # =========================================================

    def save(
        self,
        *,
        model_name: str,
        version: str,
        state_dict: Mapping[str, Tensor],
    ) -> tuple[Path, str, int]:
        """
        Save a model state dictionary.

        Returns:

            (
                artifact_path,
                model_hash,
                artifact_size,
            )

        The hash is generated using FedSentinel's existing
        deterministic hash_state_dict() implementation.
        """

        self._validate_state_dict(
            state_dict
        )

        normalized_state = clone_state_dict(
            state_dict
        )

        model_hash = hash_state_dict(
            normalized_state
        )

        path = self.artifact_path(
            model_name=model_name,
            version=version,
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = path.with_suffix(
            ".tmp"
        )

        try:

            save_file(
                normalized_state,
                str(temporary_path),
            )

            temporary_path.replace(
                path
            )

        finally:

            if temporary_path.exists():
                temporary_path.unlink()

        artifact_size = path.stat().st_size

        return (
            path,
            model_hash,
            artifact_size,
        )

    # =========================================================
    # Load
    # =========================================================

    def load(
        self,
        *,
        model_name: str,
        version: str,
    ) -> StateDict:
        """
        Load a model state dictionary from a safetensors artifact.

        No arbitrary Python object deserialization is performed.
        """

        path = self.artifact_path(
            model_name=model_name,
            version=version,
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Model artifact does not exist: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Model artifact path is not a file: {path}"
            )

        state_dict = load_file(
            str(path),
            device="cpu",
        )

        self._validate_state_dict(
            state_dict
        )

        return clone_state_dict(
            state_dict
        )

    # =========================================================
    # Verification
    # =========================================================

    def verify(
        self,
        *,
        model_name: str,
        version: str,
        expected_hash: str,
    ) -> bool:
        """
        Verify the actual model artifact against the expected
        FedSentinel model hash.

        The artifact is loaded and its state dictionary is hashed
        using the existing hash_state_dict() implementation.
        """

        if not expected_hash:
            raise ValueError(
                "expected_hash cannot be empty."
            )

        state_dict = self.load(
            model_name=model_name,
            version=version,
        )

        actual_hash = hash_state_dict(
            state_dict
        )

        return actual_hash == expected_hash

    # =========================================================
    # Verified load
    # =========================================================

    def load_verified(
        self,
        *,
        model_name: str,
        version: str,
        expected_hash: str,
    ) -> StateDict:
        """
        Load a model only when its calculated hash matches the
        expected persisted identity.

        This is the preferred loading method for hospitals and
        federation services.
        """

        state_dict = self.load(
            model_name=model_name,
            version=version,
        )

        actual_hash = hash_state_dict(
            state_dict
        )

        if actual_hash != expected_hash:
            raise ValueError(
                "Global model artifact integrity verification failed. "
                f"Expected hash '{expected_hash}', "
                f"but calculated '{actual_hash}'."
            )

        return state_dict