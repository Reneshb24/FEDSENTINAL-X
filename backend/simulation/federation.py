"""
Federated learning simulation engine for FedSentinel.

This module orchestrates a complete federated learning round.

Responsibilities:

    1. Load/create the federated clients.
    2. Maintain the global model.
    3. Execute local training.
    4. Collect ModelUpdate artifacts.

This module does NOT perform security detection.

FedSentinel's security layers independently inspect the submitted
updates after they are produced.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from torch import nn

from backend.models.model_utils import StateDict, clone_state_dict
from backend.models.update import ModelUpdate
from clients.client_config import ClientConfig
from clients.hospital_client import HospitalClient
from data.dataset import create_client_subset
from data.non_iid_splitter import (
    ClientPartition,
    create_non_iid_partitions,
)


@dataclass(frozen=True)
class FederationRoundResult:
    """
    Result of one complete federated training round.
    """

    round_id: str

    global_state: StateDict

    updates: List[ModelUpdate]

    client_partitions: Dict[str, ClientPartition]

    @property
    def num_clients(self) -> int:
        """Number of clients participating in the round."""

        return len(self.updates)

    @property
    def total_examples(self) -> int:
        """Total number of training examples used by clients."""

        return sum(
            update.num_examples
            for update in self.updates
        )


class FederationEngine:
    """
    Orchestrates federated training across multiple hospital clients.

    The engine deliberately has no knowledge of:

        - malicious clients
        - attack labels
        - anomaly scores
        - trust scores
        - quarantine decisions

    Those belong to FedSentinel's security pipeline.
    """

    def __init__(
        self,
        dataset,
        model_factory,
        num_clients: int = 20,
        seed: int = 42,
        concentration: float = 0.5,
        local_epochs: int = 1,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        device: str = "cpu",
    ) -> None:

        if dataset is None:
            raise ValueError(
                "dataset must not be None."
            )

        if len(dataset) == 0:
            raise ValueError(
                "dataset must not be empty."
            )

        if model_factory is None:
            raise ValueError(
                "model_factory must not be None."
            )

        if num_clients < 2:
            raise ValueError(
                "num_clients must be at least 2."
            )

        self.dataset = dataset

        self.model_factory = model_factory

        self.num_clients = num_clients

        self.seed = seed

        self.concentration = concentration

        self.local_epochs = local_epochs

        self.batch_size = batch_size

        self.learning_rate = learning_rate

        self.device = device

        self.global_model = model_factory()

        self.global_state = clone_state_dict(
            self.global_model.state_dict()
        )

        self.partitions = create_non_iid_partitions(
            dataset=self.dataset,
            num_clients=self.num_clients,
            seed=self.seed,
            concentration=self.concentration,
        )

    def create_clients(self) -> Dict[str, HospitalClient]:
        """
        Create one HospitalClient for every federation partition.
        """

        clients: Dict[str, HospitalClient] = {}

        for client_id, partition in self.partitions.items():

            subset = create_client_subset(
                self.dataset,
                partition.indices,
            )

            config = ClientConfig(
                client_id=client_id,
                local_epochs=self.local_epochs,
                batch_size=self.batch_size,
                learning_rate=self.learning_rate,
                device=self.device,
            )

            model = self.model_factory()

            clients[client_id] = HospitalClient(
                config=config,
                dataset=subset,
                model=model,
            )

        return clients

    def run_round(
        self,
        round_id: str,
    ) -> FederationRoundResult:
        """
        Execute one complete federated training round.

        Every client starts from the same global model state.

        Returns:
            FederationRoundResult containing the global state and
            all client ModelUpdates.
        """

        if not round_id.strip():
            raise ValueError(
                "round_id must not be empty."
            )

        clients = self.create_clients()

        updates: List[ModelUpdate] = []

        round_global_state = clone_state_dict(
            self.global_state
        )

        for client_id, client in clients.items():

            update_id = (
                f"{round_id}-{client_id}"
            )

            update = client.train(
                global_state=round_global_state,
                round_id=round_id,
                update_id=update_id,
            )

            updates.append(update)

        return FederationRoundResult(
            round_id=round_id,
            global_state=round_global_state,
            updates=updates,
            client_partitions=self.partitions,
        )