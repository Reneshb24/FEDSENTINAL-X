from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClientConfig:
    """
    Configuration for one federated learning client.

    The configuration contains only training/runtime parameters.
    Security decisions are made by the server-side FedSentinel
    pipeline, not by this configuration.
    """

    client_id: str

    local_epochs: int = 1
    batch_size: int = 32
    learning_rate: float = 0.001

    device: str = "cpu"

    def __post_init__(self) -> None:
        if not self.client_id.strip():
            raise ValueError("client_id must not be empty.")

        if self.local_epochs < 1:
            raise ValueError(
                "local_epochs must be at least 1."
            )

        if self.batch_size < 1:
            raise ValueError(
                "batch_size must be at least 1."
            )

        if self.learning_rate <= 0:
            raise ValueError(
                "learning_rate must be positive."
            )

        if not self.device.strip():
            raise ValueError(
                "device must not be empty."
            )