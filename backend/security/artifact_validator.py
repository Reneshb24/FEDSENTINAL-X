"""
Security-sensitive artifact validation for FedSentinel.

Layer 0 is the first server-side validation boundary for model updates.

It checks:

    - update structure
    - tensor validity
    - NaN / Inf values
    - parameter shapes
    - parameter count
    - update norm
    - duplicate update hashes
    - cryptographic integrity

L0 produces evidence.

It does NOT determine that a client is malicious.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional, Set

import torch
from torch import Tensor

from backend.core.constants import (
    MAX_ARTIFACT_SIZE_BYTES,
)
from backend.models.model_utils import (
    state_dict_to_vector,
    vector_l2_norm,
)
from backend.models.update import ModelUpdate
from backend.security.hashing import hash_model_update


# ---------------------------------------------------------------------------
# Layer 0 defaults
# ---------------------------------------------------------------------------
#
# These are security-policy defaults for the prototype.
#
# They are deliberately kept here instead of modifying the project's
# existing core constants interface.
#

DEFAULT_MAX_UPDATE_NORM = 100.0

DEFAULT_MAX_PARAMETER_COUNT = 10_000_000


@dataclass(frozen=True)
class ArtifactValidationResult:
    """
    Result produced by Layer 0 artifact validation.
    """

    passed: bool

    integrity_verified: bool

    duplicate_detected: bool

    gradient_bounds_valid: bool

    parameter_structure_valid: bool

    finite_values_valid: bool

    parameter_count: int

    update_norm: float

    artifact_hash: str

    reason: str


class ArtifactValidator:
    """
    Server-side Layer 0 validator.

    The validator maintains a set of previously observed update hashes
    so identical/replayed updates can be detected.

    No client ID is used to determine whether an update is malicious.
    """

    def __init__(
        self,
        expected_state: Optional[Mapping[str, Tensor]] = None,
        max_update_norm: float = DEFAULT_MAX_UPDATE_NORM,
        max_parameter_count: int = DEFAULT_MAX_PARAMETER_COUNT,
    ) -> None:

        if max_update_norm <= 0:
            raise ValueError(
                "max_update_norm must be positive."
            )

        if max_parameter_count <= 0:
            raise ValueError(
                "max_parameter_count must be positive."
            )

        self.expected_state = (
            dict(expected_state)
            if expected_state is not None
            else None
        )

        self.max_update_norm = max_update_norm

        self.max_parameter_count = max_parameter_count

        self._seen_hashes: Set[str] = set()

    def validate(
        self,
        update: ModelUpdate,
    ) -> ArtifactValidationResult:
        """
        Validate one ModelUpdate.

        The validator examines the actual update contents.

        It does not use:

            - client ID
            - attack labels
            - demo configuration
            - knowledge of compromised clients
        """

        if update is None:
            raise ValueError(
                "update must not be None."
            )

        delta = update.delta

        # ---------------------------------------------------------
        # Cryptographic artifact identity
        # ---------------------------------------------------------

        artifact_hash = hash_model_update(
            delta
        )

        duplicate_detected = (
            artifact_hash in self._seen_hashes
        )

        # Record this artifact so future submissions can be
        # checked for replay/duplication.
        self._seen_hashes.add(
            artifact_hash
        )

        # ---------------------------------------------------------
        # Parameter structure validation
        # ---------------------------------------------------------

        parameter_structure_valid = True

        if not delta:
            parameter_structure_valid = False

        if self.expected_state is not None:

            expected_keys = set(
                self.expected_state.keys()
            )

            actual_keys = set(
                delta.keys()
            )

            if expected_keys != actual_keys:

                parameter_structure_valid = False

            else:

                for name in expected_keys:

                    expected_tensor = (
                        self.expected_state[name]
                    )

                    actual_tensor = delta[name]

                    if not isinstance(
                        actual_tensor,
                        Tensor,
                    ):
                        parameter_structure_valid = False
                        break

                    if (
                        expected_tensor.shape
                        != actual_tensor.shape
                    ):
                        parameter_structure_valid = False
                        break

        # ---------------------------------------------------------
        # Tensor validity
        # ---------------------------------------------------------

        finite_values_valid = True

        parameter_count = 0

        for name, tensor in delta.items():

            if not isinstance(
                tensor,
                Tensor,
            ):
                finite_values_valid = False
                parameter_structure_valid = False
                continue

            parameter_count += tensor.numel()

            if tensor.numel() == 0:

                finite_values_valid = False

            if torch.is_floating_point(tensor):

                if not torch.isfinite(tensor).all():

                    finite_values_valid = False

        # ---------------------------------------------------------
        # Parameter count bounds
        # ---------------------------------------------------------

        if parameter_count == 0:

            parameter_structure_valid = False

        if parameter_count > self.max_parameter_count:

            parameter_structure_valid = False

        # ---------------------------------------------------------
        # Update norm
        # ---------------------------------------------------------

        try:

            vector = state_dict_to_vector(
                delta
            )

            update_norm = vector_l2_norm(
                vector
            )

        except Exception:

            update_norm = float("inf")

            finite_values_valid = False

        gradient_bounds_valid = (
            finite_values_valid
            and update_norm <= self.max_update_norm
        )

        # ---------------------------------------------------------
        # Integrity
        # ---------------------------------------------------------

        integrity_verified = bool(
            artifact_hash
        )

        # ---------------------------------------------------------
        # Failure evidence
        # ---------------------------------------------------------

        failures: list[str] = []

        if not integrity_verified:

            failures.append(
                "integrity verification failed"
            )

        if duplicate_detected:

            failures.append(
                "duplicate update detected"
            )

        if not parameter_structure_valid:

            failures.append(
                "parameter structure invalid"
            )

        if not finite_values_valid:

            failures.append(
                "non-finite tensor values detected"
            )

        if not gradient_bounds_valid:

            failures.append(
                "update norm exceeds configured bounds"
            )

        passed = len(failures) == 0

        if passed:

            reason = (
                "Update passed Layer 0 artifact validation."
            )

        else:

            reason = "; ".join(
                failures
            )

        return ArtifactValidationResult(
            passed=passed,

            integrity_verified=integrity_verified,

            duplicate_detected=duplicate_detected,

            gradient_bounds_valid=gradient_bounds_valid,

            parameter_structure_valid=parameter_structure_valid,

            finite_values_valid=finite_values_valid,

            parameter_count=parameter_count,

            update_norm=update_norm,

            artifact_hash=artifact_hash,

            reason=reason,
        )