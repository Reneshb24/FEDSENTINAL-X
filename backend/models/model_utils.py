"""
Utilities for manipulating federated model parameters.

These functions operate on model state dictionaries without serializing
arbitrary Python objects. This is important because model-update artifacts
are security-sensitive inputs to FedSentinel.
"""

from collections import OrderedDict
from typing import Mapping

import torch
from torch import Tensor, nn


StateDict = OrderedDict[str, Tensor]


def clone_state_dict(
    state_dict: Mapping[str, Tensor],
) -> StateDict:
    """
    Create an independent CPU copy of a model state dictionary.

    Args:
        state_dict:
            Model state dictionary to clone.

    Returns:
        Independent CPU copy of the state dictionary.

    The returned tensors do not share storage with the original tensors.
    """

    return OrderedDict(
        (
            name,
            tensor.detach().cpu().clone(),
        )
        for name, tensor in state_dict.items()
    )


def model_to_state_dict(
    model: nn.Module,
) -> StateDict:
    """
    Create an independent CPU copy of a model's state dictionary.
    """

    return clone_state_dict(
        model.state_dict()
    )


def load_state_dict(
    model: nn.Module,
    state_dict: Mapping[str, Tensor],
    *,
    strict: bool = True,
) -> nn.Module:
    """
    Load a state dictionary into a model.

    Strict loading is enabled by default so missing or unexpected
    parameters cannot be silently ignored.
    """

    model.load_state_dict(
        state_dict,
        strict=strict,
    )

    return model


def state_dict_to_vector(
    state_dict: Mapping[str, Tensor],
) -> Tensor:
    """
    Flatten all floating-point parameters into one CPU vector.

    This vector representation is useful for:

        - update comparison
        - distance calculations
        - anomaly detection
        - fingerprint generation
        - influence analysis
        - similarity calculations
    """

    vectors: list[Tensor] = []

    for tensor in state_dict.values():
        if torch.is_floating_point(tensor):
            vectors.append(
                tensor.detach()
                .cpu()
                .float()
                .reshape(-1)
            )

    if not vectors:
        return torch.empty(
            0,
            dtype=torch.float32,
        )

    return torch.cat(vectors)


def model_to_vector(
    model: nn.Module,
) -> Tensor:
    """
    Convert a model's floating-point parameters into one vector.
    """

    return state_dict_to_vector(
        model.state_dict()
    )


def compute_model_delta(
    global_state: Mapping[str, Tensor],
    local_state: Mapping[str, Tensor],
) -> StateDict:
    """
    Compute the local model update relative to the global model.

    Formula:

        delta = local_state - global_state

    Floating-point tensors are subtracted.

    Non-floating tensors, such as BatchNorm counters, are copied from
    the local state because subtraction is not meaningful for them.
    """

    if global_state.keys() != local_state.keys():
        raise ValueError(
            "Global and local model states must contain identical keys."
        )

    delta: StateDict = OrderedDict()

    for name in global_state:
        global_tensor = global_state[name]
        local_tensor = local_state[name]

        if global_tensor.shape != local_tensor.shape:
            raise ValueError(
                f"Shape mismatch for parameter '{name}': "
                f"{global_tensor.shape} != {local_tensor.shape}"
            )

        if torch.is_floating_point(global_tensor):
            delta[name] = (
                local_tensor.detach().cpu()
                - global_tensor.detach().cpu()
            )
        else:
            # Non-floating tensors such as BatchNorm counters are copied
            # because subtraction is not meaningful for them.
            delta[name] = (
                local_tensor.detach()
                .cpu()
                .clone()
            )

    return delta


def apply_model_delta(
    global_state: Mapping[str, Tensor],
    delta: Mapping[str, Tensor],
) -> StateDict:
    """
    Apply a model delta to a global model state.

    Formula:

        new_state = global_state + delta

    Floating-point tensors are added.

    Non-floating tensors are copied from the delta.
    """

    if global_state.keys() != delta.keys():
        raise ValueError(
            "Global state and delta must contain identical keys."
        )

    updated: StateDict = OrderedDict()

    for name in global_state:
        global_tensor = global_state[name]
        delta_tensor = delta[name]

        if global_tensor.shape != delta_tensor.shape:
            raise ValueError(
                f"Shape mismatch for parameter '{name}': "
                f"{global_tensor.shape} != {delta_tensor.shape}"
            )

        if torch.is_floating_point(global_tensor):
            updated[name] = (
                global_tensor.detach().cpu()
                + delta_tensor.detach().cpu()
            )
        else:
            updated[name] = (
                delta_tensor.detach()
                .cpu()
                .clone()
            )

    return updated


def vector_l2_norm(
    vector: Tensor,
) -> float:
    """
    Return the L2 norm of a parameter/update vector.

    Returns 0.0 for an empty vector.
    """

    if vector.numel() == 0:
        return 0.0

    vector = (
        vector.detach()
        .cpu()
        .float()
    )

    return float(
        torch.linalg.vector_norm(vector).item()
    )


def vector_cosine_similarity(
    first: Tensor,
    second: Tensor,
) -> float:
    """
    Calculate cosine similarity between two vectors.

    Returns 0.0 when either vector has zero magnitude.

    The result is clamped to [-1.0, 1.0] to prevent floating-point
    precision errors from producing values slightly outside the
    mathematically valid range.
    """

    if first.numel() != second.numel():
        raise ValueError(
            "Vectors must have the same number of elements."
        )

    if first.numel() == 0:
        return 0.0

    first = (
        first.detach()
        .cpu()
        .float()
    )

    second = (
        second.detach()
        .cpu()
        .float()
    )

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

    similarity = torch.clamp(
        similarity,
        min=-1.0,
        max=1.0,
    )

    return float(
        similarity.item()
    )