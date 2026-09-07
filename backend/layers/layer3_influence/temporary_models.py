"""
Temporary model utilities for FedSentinel Layer 3.

These models are evaluation copies only. The federation's actual
global model is never mutated during influence experiments.
"""

from __future__ import annotations

from torch import nn

from backend.models.model_utils import (
    StateDict,
    load_state_dict,
)


def create_evaluation_model(
    model_factory,
    state_dict: StateDict,
) -> nn.Module:
    """
    Create an isolated model from a supplied state dictionary.
    """

    model = model_factory()

    load_state_dict(
        model,
        state_dict,
        strict=True,
    )

    return model


def clone_model_state(
    model: nn.Module,
) -> StateDict:
    """
    Return a detached CPU copy of a model state.
    """

    from backend.models.model_utils import (
        clone_state_dict,
    )

    return clone_state_dict(
        model.state_dict()
    )