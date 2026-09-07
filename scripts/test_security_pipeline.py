"""
End-to-end FedSentinel security pipeline validation.

The attack is injected only by the test harness.
The security pipeline receives no attack label.
"""

from collections import OrderedDict

from backend.layers.layer3_influence import InfluenceAnalyzer
from backend.layers.layer4_counterfactual import CounterfactualAnalyzer
from backend.models.cnn import FedSentinelCNN
from backend.models.update import create_model_update
from data.dataset import load_mnist_train
from backend.simulation.federation import FederationEngine
from backend.services.security_pipeline import SecurityPipeline


def model_factory():
    return FedSentinelCNN()


def poison_update(update, scale=25.0):
    """Synthetic model-poisoning mutation used only by this test."""

    poisoned_delta = OrderedDict()

    for name, tensor in update.delta.items():
        if tensor.is_floating_point():
            poisoned_delta[name] = tensor * scale
        else:
            poisoned_delta[name] = tensor.clone()

    return create_model_update(
        update_id=f"{update.update_id}-poisoned",
        client_id=update.client_id,
        round_id=update.round_id,
        delta=poisoned_delta,
        num_examples=update.num_examples,
    )


def main():
    print("=" * 88)
    print("FedSentinel - End-to-End Security Pipeline Validation")
    print("=" * 88)

    # ---------------------------------------------------------
    # 1. Build deterministic federation
    # ---------------------------------------------------------

    engine = FederationEngine(
        dataset=load_mnist_train(),
        model_factory=model_factory,
        num_clients=20,
        seed=42,
        concentration=0.5,
        local_epochs=1,
        batch_size=32,
        learning_rate=0.001,
        device="cpu",
    )

    print()
    print("Federation created.")
    print(f"Clients: {engine.num_clients}")
    print(f"Seed:    {engine.seed}")

    # ---------------------------------------------------------
    # 2. Generate one real federated round
    # ---------------------------------------------------------

    federation_result = engine.run_round(
        round_id="round-001"
    )

    updates = list(federation_result.updates)

    print()
    print(f"Generated updates: {len(updates)}")

    assert len(updates) == 20

    # ---------------------------------------------------------
    # 3. Inject attack dynamically.
    #
    # IMPORTANT:
    # The pipeline does not receive the target client ID.
    # ---------------------------------------------------------

    target_index = len(updates) // 2
    original_target = updates[target_index]

    updates[target_index] = poison_update(
        original_target,
        scale=25.0,
    )

    injected_client = updates[target_index].client_id

    print()
    print("Synthetic attack injected by test harness.")
    print(f"Injected client: {injected_client}")
    print(f"Attack scale:    25.0")

    # ---------------------------------------------------------
    # 4. Run FedSentinel security pipeline
    # ---------------------------------------------------------

    pipeline = SecurityPipeline()

    from torch.utils.data import DataLoader, Subset

    validation_dataset = load_mnist_train()

    validation_subset = Subset(
        validation_dataset,
        range(min(2000, len(validation_dataset))),
    )

    validation_loader = DataLoader(
        validation_subset,
        batch_size=64,
        shuffle=False,
        num_workers=0,
    )

    result = pipeline.process_round(
        round_id="round-001",
        updates=updates,
        global_state=federation_result.global_state,
        model_factory=model_factory,
        validation_loader=validation_loader,
        device="cpu",
    )

    # ---------------------------------------------------------
    # 5. Basic pipeline assertions
    # ---------------------------------------------------------

    print()
    print("Pipeline completed.")
    print(f"Total updates:       {result.total_updates}")
    print(f"Accepted updates:    {len(result.accepted_updates)}")
    print(f"Quarantined updates: {len(result.quarantined_updates)}")
    print(f"Incident required:   {result.incident_required}")

    assert result.total_updates == 20
    assert len(result.client_results) == 20

    # ---------------------------------------------------------
    # 6. Find highest-risk client WITHOUT using target ID
    # ---------------------------------------------------------

    ranked = sorted(
        result.client_results.values(),
        key=lambda item: (
            item.trust.risk_score
            if item.trust is not None
            else -1.0
        ),
        reverse=True,
    )

    print()
    print("-" * 88)
    print("TOP SECURITY RESULTS")
    print("-" * 88)

    for position, client_result in enumerate(ranked[:10], start=1):
        trust = client_result.trust

        print(
            f"{position:2}. "
            f"{client_result.client_id:<5} "
            f"risk={trust.risk_score:6.2f} "
            f"confidence={trust.confidence:.3f} "
            f"status={trust.status.value:<12} "
            f"action={trust.action.value:<12}"
        )

    # ---------------------------------------------------------
    # 7. Verify independent discovery
    # ---------------------------------------------------------

    print()
    print("-" * 88)
    print("H11 FORENSIC TRACE")
    print("-" * 88)

    h11 = result.client_results[injected_client]

    print(f"H11 quarantined: {h11.quarantined}")
    print(f"H11 evidence:    {h11.evidence_items}")
    print(f"H11 L2:          {h11.layer2}")
    print(f"H11 L3:          {h11.layer3}")
    print(f"H11 L4:          {h11.layer4}")
    print(f"H11 L5:          {h11.layer5}")
    print(f"H11 Trust:       {h11.trust}")

    top_result = ranked[0]

    print()
    print("-" * 88)
    print("INDEPENDENT DISCOVERY")
    print("-" * 88)
    print(f"Highest-risk client: {top_result.client_id}")
    print(f"Injected client:     {injected_client}")

    assert top_result.client_id == injected_client

    # ---------------------------------------------------------
    # 8. Verify quarantine
    # ---------------------------------------------------------

    assert top_result.quarantined is True
    assert top_result.trust is not None

    print()
    print("Trust decision:")
    print(f"  Risk:       {top_result.trust.risk_score:.2f}")
    print(f"  Confidence: {top_result.trust.confidence:.3f}")
    print(f"  Status:     {top_result.trust.status.value}")
    print(f"  Action:     {top_result.trust.action.value}")
    print(f"  Hypothesis: {top_result.trust.hypothesis.value}")

    # ---------------------------------------------------------
    # 9. Print evidence chain
    # ---------------------------------------------------------

    print()
    print("Evidence chain:")

    for item in top_result.evidence_items:
        print(f"  - {item}")

    if top_result.trust.supporting_evidence:
        print()
        print("Trust evidence:")

        for item in top_result.trust.supporting_evidence:
            print(f"  - {item}")

    print()
    print("=" * 88)
    print("END-TO-END SECURITY PIPELINE VALIDATION PASSED")
    print("=" * 88)


if __name__ == "__main__":
    main()
