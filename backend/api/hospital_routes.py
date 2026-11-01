"""
Hospital API routes for FedSentinel.

Administrative routes are protected by require_admin.

Hospital registration is public, but newly registered hospitals
remain PENDING until explicitly approved by an administrator.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from backend.auth.dependencies import require_admin
from backend.schemas.hospital import (
    HospitalActionRequest,
    HospitalAdminCreate,
    HospitalApplicationApprovalRequest,
    HospitalApplicationRejectionRequest,
    HospitalApplicationReviewRequest,
    HospitalCreate,
    HospitalRegistrationRequest,
    HospitalRegistrationResponse,
    HospitalResponse,
    HospitalUpdate,
)
from backend.services.hospital_service import HospitalService
from backend.storage.database import get_db
from backend.storage.models import Hospital
from backend.storage.models import User


router = APIRouter(
    prefix="/hospitals",
    tags=["Hospitals"],
)


# ============================================================================
# Helpers
# ============================================================================

def get_hospital(
    db: Session,
    hospital_id: str,
) -> Hospital:

    hospital = (
        db.query(Hospital)
        .filter(Hospital.id == hospital_id)
        .first()
    )

    if hospital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found.",
        )

    return hospital


# ============================================================================
# PUBLIC REGISTRATION
# ============================================================================

@router.post(
    "/register",
    response_model=HospitalRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new hospital",
)
def register_hospital(
    payload: HospitalRegistrationRequest,
    db: Session = Depends(get_db),
):
    """
    Public hospital registration.

    The hospital receives PENDING status and cannot participate
    in federation rounds until an administrator approves it.
    """

    hospital = HospitalService.register_hospital(
        db,
        payload,
    )

    return HospitalRegistrationResponse(
        id=hospital.id,
        code=hospital.code,
        name=hospital.name,
        status=hospital.status,
        application_status=hospital.application_status,
        message=(
            "Hospital registered and authorized successfully in federation cohort."
            if hospital.status == "ACTIVE"
            else "Hospital registered successfully. Awaiting administrator approval."
        ),
    )


# ============================================================================
# ADMIN — LIST
# ============================================================================

@router.get(
    "",
    response_model=list[HospitalResponse],
)
def list_hospitals(
    include_simulation: bool = False,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = db.query(Hospital)
    if not include_simulation:
        query = query.filter(Hospital.is_simulation.is_(False))
    if status:
        query = query.filter(Hospital.status == status.upper())
    return (
        query
        .order_by(Hospital.created_at.desc())
        .all()
    )


# ============================================================================
# ADMIN — APPLICATIONS QUEUE
# ============================================================================

@router.get(
    "/applications",
    response_model=list[HospitalResponse],
    summary="List institutional registration applications",
)
def list_applications(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return HospitalService.list_applications(
        db,
        status_filter=status_filter,
    )


@router.post(
    "/{hospital_id}/review",
    response_model=HospitalResponse,
    summary="Mark application as under review",
)
def review_hospital_application(
    hospital_id: str,
    payload: HospitalApplicationReviewRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = get_hospital(db, hospital_id)
    notes = payload.notes if payload else None
    return HospitalService.review_application(
        db,
        actor_user_id=current_user.id,
        hospital=hospital,
        notes=notes,
    )


@router.post(
    "/{hospital_id}/application-approve",
    response_model=HospitalResponse,
    summary="Approve institutional application and enroll in federation",
)
def approve_hospital_application(
    hospital_id: str,
    payload: HospitalApplicationApprovalRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = get_hospital(db, hospital_id)
    federation_id = payload.federation_id if payload else None
    notes = payload.notes if payload else None
    return HospitalService.approve_application(
        db,
        actor_user_id=current_user.id,
        hospital=hospital,
        federation_id=federation_id,
        notes=notes,
    )


@router.post(
    "/{hospital_id}/application-reject",
    response_model=HospitalResponse,
    summary="Reject institutional application with mandatory reason",
)
def reject_hospital_application(
    hospital_id: str,
    payload: HospitalApplicationRejectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = get_hospital(db, hospital_id)
    return HospitalService.reject_application(
        db,
        actor_user_id=current_user.id,
        hospital=hospital,
        rejection_reason=payload.rejection_reason,
    )


# ============================================================================
# ADMIN — CREATE
# ============================================================================

@router.post(
    "",
    response_model=HospitalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hospital(
    payload: HospitalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return HospitalService.create_hospital(
        db,
        actor_user_id=current_user.id,
        **payload.model_dump(),
    )


# ============================================================================
# ADMIN — GET
# ============================================================================

@router.get(
    "/{hospital_id}",
    response_model=HospitalResponse,
)
def get_hospital_details(
    hospital_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return get_hospital(
        db,
        hospital_id,
    )


# ============================================================================
# ADMIN — UPDATE
# ============================================================================

@router.post(
    "/{hospital_id}/admin",
    status_code=status.HTTP_201_CREATED,
)
def create_hospital_admin(
    hospital_id: str,
    payload: HospitalAdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = get_hospital(
        db,
        hospital_id,
    )

    admin = HospitalService.create_hospital_admin(
        db,
        actor_user_id=current_user.id,
        hospital=hospital,
        email=payload.email,
        password=payload.password,
    )

    return {
        "id": admin.id,
        "email": admin.email,
        "role": admin.role,
        "hospital_id": admin.hospital_id,
        "is_active": admin.is_active,
    }


@router.patch(
    "/{hospital_id}",
    response_model=HospitalResponse,
)
def update_hospital(
    hospital_id: str,
    payload: HospitalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = get_hospital(
        db,
        hospital_id,
    )

    return HospitalService.update_hospital(
        db,
        actor_user_id=current_user.id,
        hospital=hospital,
        **payload.model_dump(
            exclude_unset=True
        ),
    )


# ============================================================================
# ADMIN — APPROVE
# ============================================================================

@router.post(
    "/{hospital_id}/approve",
    response_model=HospitalResponse,
)
def approve_hospital(
    hospital_id: str,
    payload: HospitalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = get_hospital(
        db,
        hospital_id,
    )

    return HospitalService.approve(
        db,
        actor_user_id=current_user.id,
        hospital=hospital,
        reason=payload.reason,
    )


# ============================================================================
# ADMIN — SUSPEND
# ============================================================================

@router.post(
    "/{hospital_id}/suspend",
    response_model=HospitalResponse,
)
def suspend_hospital(
    hospital_id: str,
    payload: HospitalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = get_hospital(
        db,
        hospital_id,
    )

    return HospitalService.suspend(
        db,
        actor_user_id=current_user.id,
        hospital=hospital,
        reason=payload.reason,
    )


# ============================================================================
# ADMIN — RESTORE
# ============================================================================

@router.post(
    "/{hospital_id}/restore",
    response_model=HospitalResponse,
)
def restore_hospital(
    hospital_id: str,
    payload: HospitalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = get_hospital(
        db,
        hospital_id,
    )

    return HospitalService.restore(
        db,
        hospital,
        actor_user_id=current_user.id,
        reason=payload.reason,
    )


# ============================================================================
# ADMIN — QUARANTINE
# ============================================================================

@router.post(
    "/{hospital_id}/quarantine",
    response_model=HospitalResponse,
)
def quarantine_hospital(
    hospital_id: str,
    payload: HospitalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = get_hospital(
        db,
        hospital_id,
    )

    return HospitalService.quarantine(
        db,
        actor_user_id=current_user.id,
        hospital=hospital,
        reason=payload.reason,
    )


# ============================================================================
# ADMIN — RELEASE
# ============================================================================

@router.post(
    "/{hospital_id}/release",
    response_model=HospitalResponse,
)
def release_hospital(
    hospital_id: str,
    payload: HospitalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = get_hospital(
        db,
        hospital_id,
    )

    return HospitalService.release(
        db,
        actor_user_id=current_user.id,
        hospital=hospital,
        reason=payload.reason,
    )


# ============================================================================
# ADMIN — REMOVE
# ============================================================================

@router.post(
    "/{hospital_id}/remove",
    response_model=HospitalResponse,
)
def remove_hospital(
    hospital_id: str,
    payload: HospitalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = get_hospital(
        db,
        hospital_id,
    )

    return HospitalService.remove(
        db,
        actor_user_id=current_user.id,
        hospital=hospital,
        reason=payload.reason,
    )


# ============================================================================
# ADMIN — REVOKE
# ============================================================================

@router.post(
    "/{hospital_id}/revoke",
    response_model=HospitalResponse,
)
def revoke_hospital(
    hospital_id: str,
    payload: HospitalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = get_hospital(
        db,
        hospital_id,
    )

    return HospitalService.revoke(
        db,
        actor_user_id=current_user.id,
        hospital=hospital,
        reason=payload.reason,
    )