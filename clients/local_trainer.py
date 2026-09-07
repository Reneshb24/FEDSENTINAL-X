"""
Local federated training engine for FedSentinel.

This module is responsible only for local model training.

Security analysis is intentionally performed outside this module by
FedSentinel's server-side security pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
from torch.utils.data import DataLoader

from backend.models.model_utils import (
    StateDict,
    clone_state_dict,
    compute_model_delta,
    load_state_dict,
)


@dataclass(frozen=True)
class TrainingResult:
    """
    Result produced by one client's local training session.
    """

    client_id: str

    trained_state_dict: StateDict

    model_delta: StateDict

    num_examples: int

    epochs_completed: int

    average_loss: float


class LocalTrainer:
    """
    Performs local federated training for a single client.

    Responsibilities:

        1. Load the current global model state.
        2. Train on the client's local dataset.
        3. Produce the trained model state.
        4. Calculate the model delta.

    Security decisions are NOT performed here.

    The server-side FedSentinel security pipeline independently
    analyzes the resulting model update.
    """

    def __init__(
        self,
        model: nn.Module,
        client_id: str,
        learning_rate: float = 0.001,
        local_epochs: int = 1,
        device: str = "cpu",
    ) -> None:

        if not client_id.strip():
            raise ValueError(
                "client_id must not be empty."
            )

        if learning_rate <= 0:
            raise ValueError(
                "learning_rate must be positive."
            )

        if local_epochs < 1:
            raise ValueError(
                "local_epochs must be at least 1."
            )

        self.client_id = client_id

        self.learning_rate = learning_rate

        self.local_epochs = local_epochs

        self.device = torch.device(device)

        self.model = model.to(self.device)

    def train(
        self,
        global_state_dict: StateDict,
        dataloader: DataLoader,
    ) -> TrainingResult:
        """
        Perform local training starting from the supplied global model.

        Args:
            global_state_dict:
                Current global model parameters.

            dataloader:
                Client's local training DataLoader.

        Returns:
            TrainingResult containing:

                - trained model state
                - model delta
                - sample count
                - epochs completed
                - average training loss
        """

        if len(dataloader.dataset) == 0:
            raise ValueError(
                "Dataloader dataset must not be empty."
            )

        # ---------------------------------------------------------
        # 1. Clone the global state.
        # ---------------------------------------------------------
        #
        # This ensures that the caller's global model state is not
        # modified accidentally during local training.
        #
        initial_state = clone_state_dict(
            global_state_dict
        )

        # ---------------------------------------------------------
        # 2. Load the global model into the local model.
        # ---------------------------------------------------------

        load_state_dict(
            self.model,
            initial_state,
            strict=True,
        )

        self.model.train()

        # ---------------------------------------------------------
        # 3. Create optimizer and loss function.
        # ---------------------------------------------------------

        optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.learning_rate,
        )

        criterion = nn.CrossEntropyLoss()

        total_loss = 0.0

        total_batches = 0

        # ---------------------------------------------------------
        # 4. Local training.
        # ---------------------------------------------------------

        for _ in range(self.local_epochs):

            for images, labels in dataloader:

                images = images.to(
                    self.device
                )

                labels = labels.to(
                    self.device
                )

                optimizer.zero_grad()

                outputs = self.model(
                    images
                )

                loss = criterion(
                    outputs,
                    labels,
                )

                loss.backward()

                optimizer.step()

                total_loss += float(
                    loss.detach()
                    .cpu()
                    .item()
                )

                total_batches += 1

        if total_batches == 0:
            raise RuntimeError(
                "Local training produced zero batches."
            )

        # ---------------------------------------------------------
        # 5. Capture the trained model.
        # ---------------------------------------------------------

        trained_state = clone_state_dict(
            self.model.state_dict()
        )

        # ---------------------------------------------------------
        # 6. Calculate the federated model update.
        # ---------------------------------------------------------
        #
        # delta = local_model - global_model
        #
        delta = compute_model_delta(
            global_state=initial_state,
            local_state=trained_state,
        )

        # ---------------------------------------------------------
        # 7. Return training result.
        # ---------------------------------------------------------

        return TrainingResult(
            client_id=self.client_id,

            trained_state_dict=trained_state,

            model_delta=delta,

            num_examples=len(
                dataloader.dataset
            ),

            epochs_completed=self.local_epochs,

            average_loss=(
                total_loss / total_batches
            ),
        )