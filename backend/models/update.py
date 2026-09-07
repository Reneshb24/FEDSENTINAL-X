"""
Internal representation of a federated model update.

This module bridges PyTorch model deltas and FedSentinel's security
pipeline. It does not perform unsafe object deserialization.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

import torch
from torch import Tensor

from backend.models.model_utils import (
    StateDict,
    state_dict_to_vector,
    vector_l2_norm,
)


@dataclass
class ModelUpdate:
    """
    A model update produced by one federated client.

    The update contains only tensor state and explicit metadata.
    """

    update_id: str
    client_id: str
    round_id: str

    delta: StateDict

    num_examples: int

    created_at: datetime

    @property
    def vector(self) -> Tensor:
        """Return the flattened update vector."""

        return state_dict_to_vector(self.delta)

    @property
    def l2_norm(self) -> float:
        """Return the L2 norm of the update."""

        return vector_l2_norm(self.vector)

    @property
    def parameter_count(self) -> int:
        """Return the number of floating-point parameters in the update."""

        return int(self.vector.numel())

    @property
    def metadata(self) -> dict[str, str | int | float]:
        """Return security-relevant metadata about the update."""

        return {
            "update_id": self.update_id,
            "client_id": self.client_id,
            "round_id": self.round_id,
            "num_examples": self.num_examples,
            "parameter_count": self.parameter_count,
            "l2_norm": self.l2_norm,
            "created_at": self.created_at.isoformat(),
        }

    def clone(self) -> "ModelUpdate":
        """Create an independent copy of the update."""

        cloned_delta: StateDict = {
            name: tensor.detach().cpu().clone()
            for name, tensor in self.delta.items()
        }

        return ModelUpdate(
            update_id=self.update_id,
            client_id=self.client_id,
            round_id=self.round_id,
            delta=cloned_delta,
            num_examples=self.num_examples,
            created_at=self.created_at,
        )


def create_model_update(
    update_id: str,
    client_id: str,
    round_id: str,
    delta: Mapping[str, Tensor],
    num_examples: int,
) -> ModelUpdate:
    """
    Construct a ModelUpdate from a model delta.

    Basic metadata validation happens here. Deeper security validation
    belongs to Layer 0.
    """

    if not update_id:
        raise ValueError("update_id cannot be empty")

    if not client_id:
        raise ValueError("client_id cannot be empty")

    if not round_id:
        raise ValueError("round_id cannot be empty")

    if num_examples <= 0:
        raise ValueError("num_examples must be greater than zero")

    if not delta:
        raise ValueError("delta cannot be empty")

    normalized_delta: StateDict = {}

    for name, tensor in delta.items():
        if not isinstance(tensor, Tensor):
            raise TypeError(
                f"Update parameter '{name}' must be a torch.Tensor."
            )

        normalized_delta[name] = (
            tensor.detach()
            .cpu()
            .clone()
        )

    return ModelUpdate(
        update_id=update_id,
        client_id=client_id,
        round_id=round_id,
        delta=normalized_delta,
        num_examples=num_examples,
        created_at=datetime.now(timezone.utc),
    )