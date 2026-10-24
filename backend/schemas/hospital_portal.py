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