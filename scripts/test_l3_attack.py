"""
FedSentinel Layer 3 adversarial validation.

Runs a real 20-client federation, injects a strong synthetic
model-poisoning update into one client, and measures the client's
leave-one-out influence.

The L3 analyzer is NOT given the identity of the attacker.
"""

from collections import OrderedDict

import torch

from backend.layers.layer3_influence import (
    InfluenceAnalyzer,
    create_validation_loader,
)
from backend.models.cnn import FedSentinelCNN
from backend.models.model_utils import clone_state_dict
from backend.models.update import create_model_update
from backend.simulation.federation import FederationEngine
from data.dataset import load_mnist_test, load_mnist_train


def model_factory():
    return FedSentinelCNN()


def poison_update(
    update,
    scale: float = 25.0,
):
    """
    Create a strongly poisoned copy of an existing update.
    """

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


def main() -> None:

    print("=" * 80)
    print("FedSentinel — Layer 3 Adversarial Validation")
    print("=" * 80)

    # ---------------------------------------------------------
    # 1. Load datasets
    # ---------------------------------------------------------

    print("\n[1/6] Loading datasets...")

    train_dataset = load_mnist_train()
    test_dataset = load_mnist_test()

    print(
        f"Training samples: {len(train_dataset)}"
    )

    print(
        f"Test samples: {len(test_dataset)}"
    )

    # ---------------------------------------------------------
    # 2. Validation subset
    # ---------------------------------------------------------

    print("\n[2/6] Creating validation subset...")

    validation_loader = create_validation_loader(
        dataset=test_dataset,
        sample_size=1000,
        batch_size=64,
        seed=42,
    )

    # ---------------------------------------------------------
    # 3. Federation
    # ---------------------------------------------------------

    print("\n[3/6] Creating federation...")

    federation = FederationEngine(
        dataset=train_dataset,
        model_factory=model_factory,
        num_clients=20,
        seed=42,
        concentration=0.5,
        local_epochs=1,
        batch_size=32,
        learning_rate=0.001,
        device="cpu",
    )

    federation_result = federation.run_round(
        round_id="l3-attack-round-001"
    )

    updates = list(
        federation_result.updates
    )

    print(
        f"Legitimate updates: {len(updates)}"
    )

    # ---------------------------------------------------------
    # 4. Inject attack
    # ---------------------------------------------------------

    print("\n[4/6] Injecting synthetic model poisoning...")

    target_index = len(updates) // 2

    original_update = updates[target_index]

    poisoned = poison_update(
        original_update,
        scale=25.0,
    )

    updates[target_index] = poisoned

    attack_client = poisoned.client_id

    print(
        f"Test attack target: {attack_client}"
    )

    print(
        "L3 receives no attack label."
    )

    # ---------------------------------------------------------
    # 5. Run L3
    # ---------------------------------------------------------

    print("\n[5/6] Running L3 influence analysis...")

    analyzer = InfluenceAnalyzer(
        model_factory=model_factory,
        validation_loader=validation_loader,
        device="cpu",
    )

    results = analyzer.analyze(
        global_state=federation_result.global_state,
        updates=updates,
    )

    # ---------------------------------------------------------
    # 6. Display
    # ---------------------------------------------------------

    print("\n[6/6] Results:")
    print("-" * 105)

    for result in results:

        marker = (
            " <-- TEST ATTACK"
            if result.client_id == attack_client
            else ""
        )

        print(
            f"{result.client_id:>4} | "
            f"with={result.validation_with_client:.4f} | "
            f"without={result.validation_without_client:.4f} | "
            f"delta={result.validation_delta:+.4f} | "
            f"score={result.influence_score:+7.2f} | "
            f"harmful={str(result.harmful_influence):<5}"
            f"{marker}"
        )

    print("-" * 105)

    attack_result = next(
        result
        for result in results
        if result.client_id == attack_client
    )

    legitimate_results = [
        result
        for result in results
        if result.client_id != attack_client
    ]

    print("\nAttack influence:")
    print(
        f"  Client: "
        f"{attack_client}"
    )

    print(
        f"  Validation delta: "
        f"{attack_result.validation_delta:+.4f}"
    )

    print(
        f"  Influence score: "
        f"{attack_result.influence_score:+.2f}"
    )

    print(
        f"  Harmful influence: "
        f"{attack_result.harmful_influence}"
    )

    print("\nLegitimate influence range:")

    scores = [
        result.influence_score
        for result in legitimate_results
    ]

    print(
        f"  Minimum: {min(scores):+.2f}"
    )

    print(
        f"  Maximum: {max(scores):+.2f}"
    )

    print(
        f"  Attack:  "
        f"{attack_result.influence_score:+.2f}"
    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert len(updates) == 20
    assert len(results) == 20

    assert attack_client in {
        result.client_id
        for result in results
    }

    assert attack_result.harmful_influence

    print(
        "\nL3 ADVERSARIAL VALIDATION PASSED"
    )

    print("=" * 80)


if __name__ == "__main__":
    main()