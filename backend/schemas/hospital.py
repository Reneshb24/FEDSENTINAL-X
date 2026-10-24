from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HospitalCreate(BaseModel):
    code: str = Field(
        min_length=2,
        max_length=50,
        pattern=r"^[A-Za-z0-9_-]+$",
    )
    name: str = Field(min_length=2, max_length=200)
    contact_email: str | None = None
    contact_phone: str | None = None
    location: str | None = None
    description: str | None = None


class HospitalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    contact_email: str | None = None
    contact_phone: str | None = None
    location: str | None = None
    description: str | None = None

class HospitalRegistrationRequest(BaseModel):
    code: str = Field(
        min_length=2,
        max_length=50,
        pattern=r"^[A-Za-z0-9_-]+$",
    )

    name: str = Field(
        min_length=2,
        max_length=200,
    )

    contact_email: str

    contact_phone: str | None = None

    location: str | None = None

    description: str | None = None

    admin_email: str

    admin_password: str = Field(
        min_length=8,
        max_length=128,
    )

    auto_enroll: bool = True
class HospitalAdminCreate(BaseModel):
    email: str
    password: str = Field(
        min_length=8,
        max_length=128,
    )

class HospitalRegistrationResponse(BaseModel):
    id: str
    code: str
    name: str
    status: str
    message: str
class HospitalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str

    status: str
    security_status: str
    is_eligible: bool

    contact_email: str | None
    contact_phone: str | None
    location: str | None
    description: str | None

    created_at: datetime
    updated_at: datetime
    removed_at: datetime | None
    removal_reason: str | None


class HospitalActionRequest(BaseModel):
    reason: str | None = Field(
        default=None,
        max_length=1000,
    )
