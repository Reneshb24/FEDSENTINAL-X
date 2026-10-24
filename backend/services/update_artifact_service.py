"""
FedSentinel model-update artifact storage.

Stores hospital-submitted federated learning updates as SafeTensors.

Storage:

    data/model_updates/
        <round_id>/
            <hospital_id>/
                <update_id>.safetensors

Security principles:

    - No pickle-based serialization.
    - No raw hospital dataset is stored here.
    - No security verdict is stored in the artifact.
    - No trust score is stored in the artifact.
    - Artifact integrity is verified using SHA-256.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

import torch
from safetensors.torch import load_file, save_file
from torch import Tensor

from backend.models.model_utils import StateDict, clone_state_dict


class UpdateArtifactService:
    """
    Persist and retrieve federated model-update deltas.

    Each artifact contains only:

        parameter_name -> tensor_delta

    The database stores metadata such as:

        update_id
        round_id
        hospital_id
        artifact_hash
        artifact_type
        artifact_size

    Security analysis remains outside this service.
    """

    DEFAULT_STORAGE_ROOT = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "model_updates"
    )

    ARTIFACT_TYPE = "SAFETENSORS"
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
    # PATH VALIDATION
    # =========================================================

    @staticmethod
    def _safe_component(
        value: str,
        field_name: str,
    ) -> str:
        """
        Validate a filesystem path component.

        Prevents path traversal and unsupported characters.
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

    # =========================================================
    # ARTIFACT PATH
    # =========================================================

    def artifact_path(
        self,
        *,
        round_id: str,
        hospital_id: str,
        update_id: str,
    ) -> Path:
        """
        Build deterministic update-artifact path.

        Example:

            data/model_updates/
                round-4/
                    hospital-21/
                        update-123.safetensors
        """

        safe_round_id = self._safe_component(
            round_id,
            "round_id",
        )

        safe_hospital_id = self._safe_component(
            hospital_id,
            "hospital_id",
        )

        safe_update_id = self._safe_component(
            update_id,
            "update_id",
        )

        return (
            self.storage_root
            / safe_round_id
            / safe_hospital_id
            / f"{safe_update_id}{self.ARTIFACT_EXTENSION}"
        )

    # =========================================================
    # VALIDATION
    # =========================================================

    @staticmethod
    def _validate_state_dict(
        state_dict: Mapping[str, Tensor],
    ) -> None:
        """
        Validate a model-update state dictionary.
        """

        if not state_dict:
            raise ValueError(
                "Update state dictionary must not be empty."
            )

        for name, tensor in state_dict.items():

            if not isinstance(name, str):
                raise TypeError(
                    "Update parameter names must be strings."
                )

            if not name.strip():
                raise ValueError(
                    "Update parameter names must not be empty."
                )

            if not isinstance(tensor, Tensor):
                raise TypeError(
                    f"Update entry '{name}' must be a torch.Tensor."
                )

            if tensor.layout != torch.strided:
                raise ValueError(
                    f"Update entry '{name}' must use strided storage."
                )

            if tensor.is_sparse:
                raise ValueError(
                    f"Update entry '{name}' cannot be sparse."
                )

            if tensor.numel() == 0:
                raise ValueError(
                    f"Update entry '{name}' cannot be empty."
                )

            if not torch.is_floating_point(tensor):
                raise ValueError(
                    f"Update entry '{name}' must contain floating-point values."
                )

            if not torch.all(
                torch.isfinite(tensor)
            ):
                raise ValueError(
                    f"Update entry '{name}' contains non-finite values."
                )

    # =========================================================
    # HASH
    # =========================================================

    @staticmethod
    def _sha256(
        path: Path,
    ) -> str:
        """
        Calculate SHA-256 of the physical artifact.
        """

        digest = hashlib.sha256()

        with path.open("rb") as file:

            while True:

                chunk = file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                digest.update(chunk)

        return digest.hexdigest()

    # =========================================================
    # SAVE
    # =========================================================

    def save(
        self,
        *,
        round_id: str,
        hospital_id: str,
        update_id: str,
        delta: Mapping[str, Tensor],
    ) -> tuple[Path, str, int]:
        """
        Save a hospital model delta as SafeTensors.

        Returns:

            artifact_path
            sha256
            artifact_size
        """

        self._validate_state_dict(
            delta
        )

        normalized_delta = clone_state_dict(
            delta
        )

        path = self.artifact_path(
            round_id=round_id,
            hospital_id=hospital_id,
            update_id=update_id,
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
                normalized_delta,
                str(temporary_path),
            )

            temporary_path.replace(
                path
            )

        finally:

            if temporary_path.exists():
                temporary_path.unlink()

        artifact_hash = self._sha256(
            path
        )

        artifact_size = path.stat().st_size

        return (
            path,
            artifact_hash,
            artifact_size,
        )

    # =========================================================
    # LOAD
    # =========================================================

    def load(
        self,
        *,
        round_id: str,
        hospital_id: str,
        update_id: str,
    ) -> StateDict:
        """
        Load a model-update delta from SafeTensors.

        No arbitrary Python deserialization is performed.
        """

        path = self.artifact_path(
            round_id=round_id,
            hospital_id=hospital_id,
            update_id=update_id,
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Update artifact does not exist: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Update artifact path is not a file: {path}"
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
    # VERIFY
    # =========================================================

    def verify(
        self,
        *,
        round_id: str,
        hospital_id: str,
        update_id: str,
        expected_hash: str,
    ) -> bool:
        """
        Verify physical artifact integrity.
        """

        if not expected_hash:
            raise ValueError(
                "expected_hash cannot be empty."
            )

        path = self.artifact_path(
            round_id=round_id,
            hospital_id=hospital_id,
            update_id=update_id,
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Update artifact does not exist: {path}"
            )

        actual_hash = self._sha256(
            path
        )

        return actual_hash == expected_hash

    # =========================================================
    # VERIFIED LOAD
    # =========================================================

    def load_verified(
        self,
        *,
        round_id: str,
        hospital_id: str,
        update_id: str,
        expected_hash: str,
    ) -> StateDict:
        """
        Load an update only after verifying its physical hash.
        """

        if not expected_hash:
            raise ValueError(
                "expected_hash cannot be empty."
            )

        path = self.artifact_path(
            round_id=round_id,
            hospital_id=hospital_id,
            update_id=update_id,
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Update artifact does not exist: {path}"
            )

        actual_hash = self._sha256(
            path
        )

        if actual_hash != expected_hash:
            raise ValueError(
                "Model update artifact integrity verification failed. "
                f"Expected hash '{expected_hash}', "
                f"but calculated '{actual_hash}'."
            )

        return self.load(
            round_id=round_id,
            hospital_id=hospital_id,
            update_id=update_id,
        )
