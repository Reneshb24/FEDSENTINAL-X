"""
FedSentinel federation execution service.

This service bridges the federated-learning simulation with the
RoundOrchestrator.

Responsibilities:
    - load the MNIST datasets
    - create the shared model factory
    - generate the federated client updates
    - optionally inject the synthetic demo attack
    - create the deterministic validation loader
    - invoke the existing RoundOrchestrator

Security detection remains completely outside this service.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.layers.layer3_influence.subset_sampler import (
    create_validation_loader,
)
from backend.models.cnn import FedSentinelCNN
from backend.models.model_utils import StateDict
from backend.services.round_orchestrator import RoundOrchestrator
from backend.simulation.attacks import inject_middle_client_poison
from backend.simulation.federation import FederationEngine
from data.dataset import load_mnist_test, load_mnist_train


@dataclass(frozen=True)
class FederationExecutionResult:
    """
    Result of one simulated federation execution.

    Attack metadata is retained here for the demo environment only.
    It is never passed to the security pipeline as ground truth.
    """

    round_id: str
    updates_generated: int
    attack_injected: bool
    attack_client_id: str | None
    global_state: StateDict


class FederationService:
    """
    Execute a complete simulated federated-learning round.

    This class owns simulation concerns only.

    It does not:
        - calculate anomaly scores
        - assign trust
        - quarantine clients
        - create security verdicts
    """

    def __init__(
        self,
        *,
        orchestrator: RoundOrchestrator,
        num_clients: int = 20,
        seed: int = 42,
        concentration: float = 0.5,
        local_epochs: int = 1,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        validation_sample_size: int = 1000,
        validation_batch_size: int = 64,
        device: str = "cpu",
    ) -> None:

        if orchestrator is None:
            raise ValueError(
                "orchestrator must not be None."
            )

        if num_clients < 2:
            raise ValueError(
                "num_clients must be at least 2."
            )

        self.orchestrator = orchestrator
        self.num_clients = num_clients
        self.seed = seed
        self.concentration = concentration
        self.local_epochs = local_epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.validation_sample_size = validation_sample_size
        self.validation_batch_size = validation_batch_size
        self.device = device

    @staticmethod
    def model_factory() -> FedSentinelCNN:
        """Create the shared FedSentinel CNN architecture."""
        return FedSentinelCNN()

    def execute(
        self,
        *,
        round_id: str,
        inject_attack: bool = True,
        attack_scale: float = 25.0,
    ) -> FederationExecutionResult:
        """
        Generate federation updates and execute the security pipeline.

        The attack, when enabled, is injected before security analysis.
        The security pipeline receives only the resulting ModelUpdates.
        """

        if not round_id.strip():
            raise ValueError(
                "round_id must not be empty."
            )

        # -----------------------------------------------------
        # Load datasets
        # -----------------------------------------------------

        train_dataset = load_mnist_train()
        test_dataset = load_mnist_test()

        # -----------------------------------------------------
        # Create federation
        # -----------------------------------------------------

        federation = FederationEngine(
            dataset=train_dataset,
            model_factory=self.model_factory,
            num_clients=self.num_clients,
            seed=self.seed,
            concentration=self.concentration,
            local_epochs=self.local_epochs,
            batch_size=self.batch_size,
            learning_rate=self.learning_rate,
            device=self.device,
        )

        federation_result = federation.run_round(
            round_id=round_id
        )

        updates = list(
            federation_result.updates
        )

        attack_client_id: str | None = None

        # -----------------------------------------------------
        # Optional synthetic demo attack
        # -----------------------------------------------------

        if inject_attack:
            updates, attack_client_id = (
                inject_middle_client_poison(
                    updates,
                    scale=attack_scale,
                )
            )

        # -----------------------------------------------------
        # Validation set
        # -----------------------------------------------------

        validation_loader = create_validation_loader(
            dataset=test_dataset,
            sample_size=self.validation_sample_size,
            batch_size=self.validation_batch_size,
            seed=self.seed,
        )

        # -----------------------------------------------------
        # Security orchestration
        # -----------------------------------------------------

        self.orchestrator.execute_round(
            round_id=round_id,
            updates=updates,
            global_state=federation_result.global_state,
            model_factory=self.model_factory,
            validation_loader=validation_loader,
            device=self.device,
        )

        managed_round = self.orchestrator.get_round(
            round_id
        )

        if managed_round.result is None:
            raise RuntimeError(
                f"Security orchestration completed without a result "
                f"for round {round_id}."
            )

        secured_global_state = managed_round.result.global_state

        if secured_global_state is None:
            raise RuntimeError(
                f"Security orchestration completed without a secured global state "
                f"for round {round_id}."
            )

        return FederationExecutionResult(
            round_id=round_id,
            updates_generated=len(updates),
            attack_injected=inject_attack,
            attack_client_id=attack_client_id,
            global_state=secured_global_state,
        )
