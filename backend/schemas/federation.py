from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FederationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: str | None = None
    dataset_name: str | None = Field(default=None, max_length=200)
    model_name: str | None = Field(default=None, max_length=200)


class FederationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    dataset_name: str | None = Field(default=None, max_length=200)
    model_name: str | None = Field(default=None, max_length=200)
    status: str | None = Field(default=None, max_length=50)


class FederationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    status: str
    dataset_name: str | None
    model_name: str | None
    created_at: datetime


class MembershipCreate(BaseModel):
    hospital_id: str
    reason: str | None = Field(default=None, max_length=1000)


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    federation_id: str
    hospital_id: str
    status: str
    joined_at: datetime | None
    left_at: datetime | None
    leave_reason: str | None


class MembershipActionRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=1000)
