from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RoundConfigurationCreate(BaseModel):
    """
    Configuration used to reproduce or execute a federated-learning round.

    SIMULATION:
        Uses the existing server-side federation simulator.

    HOSPITAL:
        Opens a real collection window where registered hospitals
        train locally and submit their model updates.
    """

    execution_mode: Literal["SIMULATION", "HOSPITAL"] = "SIMULATION"

    num_clients: int = Field(
        default=20,
        ge=2,
        le=100,
    )

    seed: int = Field(
        default=42,
        ge=0,
    )

    concentration: float = Field(
        default=0.5,
        gt=0,
    )

    local_epochs: int = Field(
        default=1,
        ge=1,
        le=20,
    )

    batch_size: int = Field(
        default=32,
        ge=1,
        le=1024,
    )

    learning_rate: float = Field(
        default=0.001,
        gt=0,
    )

    validation_sample_size: int = Field(
        default=1000,
        ge=100,
    )

    validation_batch_size: int = Field(
        default=64,
        ge=1,
        le=1024,
    )

    device: str = Field(
        default="cpu",
        min_length=2,
        max_length=20,
    )

    inject_attack: bool = True

    attack_scale: float = Field(
        default=25.0,
        ge=0,
    )


class RoundConfigurationResponse(RoundConfigurationCreate):
    pass