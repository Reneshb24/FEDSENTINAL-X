from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.schemas.round_configuration import (
    RoundConfigurationResponse,
)


class FederationRoundCreate(BaseModel):
    configuration: RoundConfigurationResponse


class FederationRoundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    federation_id: str
    round_number: int
    status: str

    global_model_version: str | None

    participating_clients: int
    accepted_updates: int
    quarantined_updates: int

    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    configuration: RoundConfigurationResponse