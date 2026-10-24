from __future__ import annotations

from collections import OrderedDict

import torch

from backend.models.update import ModelUpdate, create_model_update


def poison_update(
    update: ModelUpdate,
    scale: float = 25.0,
) -> ModelUpdate:
    """
    Create a synthetic model-poisoning version of an update.

    This helper belongs to the simulation/demo layer only.

    Security components receive only the resulting ModelUpdate;
    they do not receive the attack label or target identity.
    """

    if scale <= 0:
        raise ValueError("scale must be greater than zero.")

    poisoned_delta = OrderedDict()

    for name, tensor in update.delta.items():
        if torch.is_floating_point(tensor):
            poisoned_delta[name] = (
                tensor.detach()
                .cpu()
                .clone()
                * scale
            )
        else:
            poisoned_delta[name] = (
                tensor.detach()
                .cpu()
                .clone()
            )

    return create_model_update(
        update_id=f"{update.update_id}-poisoned",
        client_id=update.client_id,
        round_id=update.round_id,
        delta=poisoned_delta,
        num_examples=update.num_examples,
    )


def inject_middle_client_poison(
    updates: list[ModelUpdate],
    scale: float = 25.0,
) -> tuple[list[ModelUpdate], str]:
    """
    Replace the deterministic middle update with a poisoned update.

    Returns:
        (modified_updates, attack_client_id)

    The returned client ID is simulation metadata and must not be
    passed into the security detection pipeline as ground truth.
    """

    if not updates:
        raise ValueError("updates must not be empty.")

    target_index = len(updates) // 2

    modified_updates = list(updates)

    target_update = modified_updates[target_index]

    poisoned = poison_update(
        target_update,
        scale=scale,
    )

    modified_updates[target_index] = poisoned

    return modified_updates, poisoned.client_id
