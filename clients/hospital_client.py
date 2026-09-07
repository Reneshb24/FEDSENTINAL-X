"""
Federated hospital client for FedSentinel.

A HospitalClient represents one participating node in the federated
learning system.

The client is responsible for:

    1. Holding its local dataset partition.
    2. Receiving the current global model.
    3. Performing local training.
    4. Producing a ModelUpdate artifact.

Security analysis is intentionally performed server-side.

The client does not decide whether its own update is trusted,
suspicious, or malicious.
"""

from __future__ import annotations

import uuid

from torch import nn
from torch.utils.data import DataLoader, Dataset

from backend.models.model_utils import StateDict
from backend.models.update import ModelUpdate, create_model_update
from clients.client_config import ClientConfig
from clients.local_trainer import LocalTrainer


class HospitalClient:
    """
    Represents one federated hospital/client.

    Examples:

        H1
        H2
        ...
        H20
    """

    def __init__(
        self,
        config: ClientConfig,
        dataset: Dataset,
        model: nn.Module,
    ) -> None:

        if dataset is None:
            raise ValueError(
                "dataset must not be None."
            )

        if len(dataset) == 0:
            raise ValueError(
                "dataset must not be empty."
            )

        self.config = config
        self.dataset = dataset
        self.model = model

        self.trainer = LocalTrainer(
            model=self.model,
            client_id=self.config.client_id,
            learning_rate=self.config.learning_rate,
            local_epochs=self.config.local_epochs,
            device=self.config.device,
        )

    @property
    def client_id(self) -> str:
        """
        Return the unique hospital/client identifier.
        """

        return self.config.client_id

    @property
    def num_samples(self) -> int:
        """
        Return the number of local training samples.
        """

        return len(self.dataset)

    def create_dataloader(
        self,
        shuffle: bool = True,
    ) -> DataLoader:
        """
        Create a DataLoader for this hospital's local dataset.
        """

        return DataLoader(
            self.dataset,
            batch_size=self.config.batch_size,
            shuffle=shuffle,
            num_workers=0,
            pin_memory=False,
        )

    def train(
        self,
        global_state: StateDict,
        round_id: str,
        update_id: str | None = None,
    ) -> ModelUpdate:
        """
        Train locally from the supplied global model and produce
        a federated ModelUpdate.

        Args:
            global_state:
                Current global model state.

            round_id:
                Federated learning round identifier.

            update_id:
                Optional externally supplied update identifier.

                If omitted, this method generates a UUID.

        Returns:
            ModelUpdate containing the client's model delta.
        """

        if not round_id.strip():
            raise ValueError(
                "round_id must not be empty."
            )

        if update_id is None:
            update_id = (
                f"{round_id}-{self.client_id}-"
                f"{uuid.uuid4().hex[:12]}"
            )

        if not update_id.strip():
            raise ValueError(
                "update_id must not be empty."
            )

        dataloader = self.create_dataloader(
            shuffle=True
        )

        training_result = self.trainer.train(
            global_state_dict=global_state,
            dataloader=dataloader,
        )

        update = create_model_update(
            update_id=update_id,
            client_id=self.client_id,
            round_id=round_id,
            delta=training_result.model_delta,
            num_examples=training_result.num_examples,
        )

        return update