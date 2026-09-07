"""
Pydantic schemas for federated clients.
"""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from backend.core.types import ClientStatus, TrustStatus


ClientId = Annotated[str, Field(min_length=1, max_length=64)]


class ClientBase(BaseModel):
    """Common fields shared by client schemas."""

    model_config = ConfigDict(extra="forbid")

    client_id: ClientId
    name: str = Field(min_length=1, max_length=128)
    status: ClientStatus = ClientStatus.ACTIVE


class ClientCreate(ClientBase):
    """Schema used when registering a new federated client."""

    pass


class ClientTrustSummary(BaseModel):
    """Current trust information for a client."""

    model_config = ConfigDict(extra="forbid")

    trust_score: float = Field(ge=0.0, le=100.0)
    trust_status: TrustStatus
    rounds_observed: int = Field(default=0, ge=0)
    suspicious_rounds: int = Field(default=0, ge=0)
    last_updated: datetime


class ClientResponse(ClientBase):
    """Client representation returned by the API."""

    trust: ClientTrustSummary | None = None
    last_seen: datetime | None = None


class ClientListResponse(BaseModel):
    """Collection of clients returned by the API."""

    model_config = ConfigDict(extra="forbid")

    clients: list[ClientResponse]
    total: int = Field(ge=0)