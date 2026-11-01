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
    address: str | None = None
    location: str | None = None
    country: str | None = None
    region: str | None = None
    website: str | None = None
    institution_type: str | None = None
    description: str | None = None


class HospitalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    location: str | None = None
    country: str | None = None
    region: str | None = None
    website: str | None = None
    institution_type: str | None = None
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
    address: str | None = None
    location: str | None = None
    country: str | None = None
    region: str | None = None
    website: str | None = None
    institution_type: str | None = None
    description: str | None = None
    admin_name: str | None = None
    admin_email: str
    admin_password: str = Field(
        min_length=8,
        max_length=128,
    )


class HospitalAdminCreate(BaseModel):
    email: str
    password: str = Field(
        min_length=8,
        max_length=128,
    )
    full_name: str | None = None


class HospitalRegistrationResponse(BaseModel):
    id: str
    code: str
    name: str
    status: str
    application_status: str
    message: str


class HospitalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str

    status: str
    application_status: str = "APPROVED"
    security_status: str
    is_eligible: bool
    is_simulation: bool = False

    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    location: str | None = None
    country: str | None = None
    region: str | None = None
    website: str | None = None
    institution_type: str | None = None
    description: str | None = None
    rejection_reason: str | None = None

    created_at: datetime
    updated_at: datetime
    removed_at: datetime | None = None
    removal_reason: str | None = None


class HospitalActionRequest(BaseModel):
    reason: str | None = Field(
        default=None,
        max_length=1000,
    )


class HospitalApplicationReviewRequest(BaseModel):
    notes: str | None = Field(
        default=None,
        max_length=1000,
    )


class HospitalApplicationApprovalRequest(BaseModel):
    federation_id: str | None = None
    notes: str | None = Field(
        default=None,
        max_length=1000,
    )


class HospitalApplicationRejectionRequest(BaseModel):
    rejection_reason: str = Field(
        min_length=3,
        max_length=1000,
    )


class HospitalStaffCreateRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=200)
    role: str = Field(default="HOSPITAL_OPERATOR")


class HospitalStaffUpdateRequest(BaseModel):
    is_active: bool | None = None
    role: str | None = None
    full_name: str | None = None


class HospitalStaffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str | None = None
    role: str
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime
