from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ============================================================================
# HOSPITAL PROFILE
# ============================================================================

class HospitalProfileResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

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


# ============================================================================
# HOSPITAL DASHBOARD
# ============================================================================

class HospitalDashboardResponse(BaseModel):
    hospital: HospitalProfileResponse

    federation_member: bool

    membership_status: str | None

    total_datasets: int
    active_datasets: int

    total_updates: int
    accepted_updates: int
    quarantined_updates: int

    trust_score: float | None
    trust_status: str | None

    open_incidents: int


# ============================================================================
# SIMPLE STATUS RESPONSE
# ============================================================================

class HospitalStatusResponse(BaseModel):
    hospital_id: str

    status: str

    security_status: str

    is_eligible: bool

    federation_member: bool

    membership_status: str | None
