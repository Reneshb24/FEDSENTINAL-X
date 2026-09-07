from __future__ import annotations

import torch

from backend.layers.layer4_counterfactual.counterfactual import (
    CounterfactualAnalyzer,
)
from backend.layers.layer4_counterfactual.evaluator import (
    evaluate_model,
)
from backend.layers.layer3_influence.subset_sampler import (
    create_validation_loader,
)
from backend.models.cnn import FedSentinelCNN
from backend.models.update import create_model_update
from backend.simulation.federation import FederationEngine
from data.dataset import load_mnist_test, load_mnist_train


def model_factory() -> FedSentinelCNN:
    return FedSentinelCNN()


def main() -> None:
    print("=" * 88)
    print("FedSentinel - Layer 4 Adversarial Validation")
    print("=" * 88)

    # ---------------------------------------------------------
    # 1. Load datasets
    # ---------------------------------------------------------
    print()
    print("[1/6] Loading datasets...")

    train_dataset = load_mnist_train()
    test_dataset = load_mnist_test()

    print(f"Training samples: {len(train_dataset)}")
    print(f"Test samples: {len(test_dataset)}")

    # ---------------------------------------------------------
    # 2. Validation subset
    # ---------------------------------------------------------
    print()
    print("[2/6] Creating validation subset...")

    validation_loader = create_validation_loader(
        test_dataset,
        sample_size=1000,
        batch_size=64,
        seed=42,
    )

    # ---------------------------------------------------------
    # 3. Federation
    # ---------------------------------------------------------
    print()
    print("[3/6] Creating federation...")

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
        round_id="l4-attack-round-001"
    )

    updates = federation_result.updates

    print(f"Legitimate updates: {len(updates)}")

    # ---------------------------------------------------------
    # 4. Synthetic attack
    # ---------------------------------------------------------
    print()
    print("[4/6] Injecting synthetic model poisoning...")

    # Dynamically select a target. The identity is not used by
    # the L4 analyzer as an attack label.
    target_index = len(updates) // 2
    target_update = updates[target_index]
    attack_client_id = target_update.client_id

    print(f"Test attack target: {attack_client_id}")
    print("L4 receives no attack label.")

    poisoned_delta = {}

    for name, tensor in target_update.delta.items():
        if torch.is_floating_point(tensor):
            poisoned_delta[name] = (
                tensor.detach().cpu().clone() * 25.0
            )
        else:
            poisoned_delta[name] = (
                tensor.detach().cpu().clone()
            )

    poisoned_update = create_model_update(
        update_id=f"{target_update.update_id}-poisoned",
        client_id=target_update.client_id,
        round_id=target_update.round_id,
        delta=poisoned_delta,
        num_examples=target_update.num_examples,
    )

    poisoned_updates = list(updates)
    poisoned_updates[target_index] = poisoned_update

    # ---------------------------------------------------------
    # 5. L4 analysis
    # ---------------------------------------------------------
    print()
    print("[5/6] Running L4 counterfactual analysis...")

    analyzer = CounterfactualAnalyzer(
        model_factory=model_factory,
        validation_loader=validation_loader,
        device="cpu",
    )

    results = analyzer.analyze(
        global_state=federation_result.global_state,
        updates=poisoned_updates,
    )

    # ---------------------------------------------------------
    # 6. Results
    # ---------------------------------------------------------
    print()
    print("[6/6] Results:")
    print("-" * 110)

    for client_id, result in results.items():
        marker = ""

        if client_id == attack_client_id:
            marker = "  <-- TEST ATTACK"

        print(
            f"{client_id:>3} | "
            f"with={result.with_client.accuracy:.4f} | "
            f"without={result.without_client.accuracy:.4f} | "
            f"acc_delta={result.accuracy_delta:+.4f} | "
            f"loss_delta={result.loss_delta:+.4f} | "
            f"harmful={str(result.harmful_counterfactual):<5}"
            f"{marker}"
        )

    print("-" * 110)

    attack_result = results[attack_client_id]

    legitimate_results = [
        result
        for client_id, result in results.items()
        if client_id != attack_client_id
    ]

    legitimate_accuracy_deltas = [
        result.accuracy_delta
        for result in legitimate_results
    ]

    print()
    print("Attack counterfactual:")
    print(f"  Client: {attack_client_id}")
    print(
        f"  Accuracy with: "
        f"{attack_result.with_client.accuracy:.4f}"
    )
    print(
        f"  Accuracy without: "
        f"{attack_result.without_client.accuracy:.4f}"
    )
    print(
        f"  Accuracy delta: "
        f"{attack_result.accuracy_delta:+.4f}"
    )
    print(
        f"  Loss delta: "
        f"{attack_result.loss_delta:+.4f}"
    )
    print(
        f"  Harmful counterfactual: "
        f"{attack_result.harmful_counterfactual}"
    )

    print()
    print("Legitimate counterfactual accuracy range:")
    print(
        f"  Minimum: "
        f"{min(legitimate_accuracy_deltas):+.4f}"
    )
    print(
        f"  Maximum: "
        f"{max(legitimate_accuracy_deltas):+.4f}"
    )
    print(
        f"  Attack:  "
        f"{attack_result.accuracy_delta:+.4f}"
    )

    assert len(updates) == 20
    assert len(results) == 20
    assert attack_result.harmful_counterfactual

    print()
    print("L4 ADVERSARIAL VALIDATION PASSED")
    print("=" * 88)


if __name__ == "__main__":
    main()
