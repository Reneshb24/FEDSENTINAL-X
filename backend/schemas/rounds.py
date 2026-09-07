"""
Pydantic schemas for federated learning rounds.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.core.types import RoundStatus


class RoundMetrics(BaseModel):
    """Training and security metrics produced during a round."""

    model_config = ConfigDict(extra="forbid")

    participating_clients: int = Field(default=0, ge=0)
    received_updates: int = Field(default=0, ge=0)
    accepted_updates: int = Field(default=0, ge=0)
    quarantined_updates: int = Field(default=0, ge=0)

    average_training_loss: float | None = None
    global_validation_accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    average_risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )


class RoundBase(BaseModel):
    """Common fields for a federated round."""

    model_config = ConfigDict(extra="forbid")

    round_id: str = Field(min_length=1, max_length=64)

    status: RoundStatus = RoundStatus.CREATED

    target_clients: int = Field(default=20, ge=1)


class RoundCreate(RoundBase):
    """Schema used to create a new federated round."""

    pass


class RoundResponse(RoundBase):
    """Complete round representation returned by the backend."""

    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    metrics: RoundMetrics = Field(
        default_factory=RoundMetrics,
    )

    global_model_hash: str | None = None


class RoundListResponse(BaseModel):
    """Collection of federated rounds."""

    model_config = ConfigDict(extra="forbid")

    rounds: list[RoundResponse]
    total: int = Field(ge=0)