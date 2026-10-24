from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from backend.schemas.hospital_training import (
    HospitalTrainingRequest,
    HospitalTrainingResponse,
)
from backend.services.hospital_training_service import (
    HospitalTrainingService,
)
from backend.services.update_artifact_service import (
    UpdateArtifactService,
)
from backend.storage.models import (
    Federation,
    FederationMembership,
    FederationRound,
    Hospital,
    ModelUpdate,
)

from sqlalchemy.orm import Session

from backend.auth.dependencies import (
    ensure_hospital_access,
    require_hospital_access,
)
from backend.schemas.hospital_portal import (
    HospitalDashboardResponse,
    HospitalProfileResponse,
    HospitalStatusResponse,
)
from backend.services.hospital_portal_service import (
    HospitalPortalService,
)
from backend.storage.database import get_db
from backend.storage.models import User


router = APIRouter(
    prefix="/hospital",
    tags=["Hospital Portal"],
)


# ============================================================================
# CURRENT HOSPITAL PROFILE
# ============================================================================

@router.get(
    "/me",
    response_model=HospitalProfileResponse,
    summary="Get current hospital profile",
)
def get_my_hospital(
    current_user: User = Depends(
        require_hospital_access
    ),
    db: Session = Depends(get_db),
):
    hospital_id = current_user.hospital_id

    if hospital_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with a hospital",
        )

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    hospital = (
        HospitalPortalService.get_hospital(
            db,
            hospital_id,
        )
    )

    if hospital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found",
        )

    return hospital


# ============================================================================
# CURRENT HOSPITAL DASHBOARD
# ============================================================================

@router.get(
    "/dashboard",
    response_model=HospitalDashboardResponse,
    summary="Get hospital dashboard",
)
def get_my_dashboard(
    current_user: User = Depends(
        require_hospital_access
    ),
    db: Session = Depends(get_db),
):
    hospital_id = current_user.hospital_id

    if hospital_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with a hospital",
        )

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    try:
        return HospitalPortalService.get_dashboard(
            db,
            hospital_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================================
# CURRENT HOSPITAL SECURITY / MEMBERSHIP STATUS
# ============================================================================

@router.get(
    "/status",
    response_model=HospitalStatusResponse,
    summary="Get current hospital status",
)
def get_my_status(
    current_user: User = Depends(
        require_hospital_access
    ),
    db: Session = Depends(get_db),
):
    hospital_id = current_user.hospital_id

    if hospital_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with a hospital",
        )

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    try:
        return HospitalPortalService.get_status(
            db,
            hospital_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

# ============================================================================
# LOCAL FEDERATED TRAINING / UPDATE SUBMISSION
# ============================================================================

@router.post(
    "/training",
    response_model=HospitalTrainingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Train locally and submit a federated model update",
)
def submit_local_training(
    payload: HospitalTrainingRequest,
    current_user: User = Depends(
        require_hospital_access
    ),
    db: Session = Depends(get_db),
):
    """
    Perform genuine hospital-local training.

    The hospital never supplies the global model itself.
    The training service loads the latest server-verified model.

    The resulting update is persisted as a SafeTensors artifact
    and registered in the database.

    Security analysis is intentionally deferred until the admin
    finalizes the hospital round so L2 can compare peer updates.
    """

    hospital_id = current_user.hospital_id

    if hospital_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with a hospital",
        )

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    # ------------------------------------------------------------
    # Verify hospital
    # ------------------------------------------------------------

    hospital = (
        db.query(Hospital)
        .filter(
            Hospital.id == hospital_id,
        )
        .first()
    )

    if hospital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found.",
        )

    if hospital.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital is not active.",
        )

    if not hospital.is_eligible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital is not eligible for federation participation.",
        )

    # ------------------------------------------------------------
    # Verify federation
    # ------------------------------------------------------------

    federation = (
        db.query(Federation)
        .filter(
            Federation.id == payload.federation_id,
            Federation.status == "ACTIVE",
        )
        .first()
    )

    if federation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active federation not found.",
        )

    # ------------------------------------------------------------
    # Verify exact federation membership
    # ------------------------------------------------------------

    membership = (
        db.query(FederationMembership)
        .filter(
            FederationMembership.federation_id
            == payload.federation_id,
            FederationMembership.hospital_id
            == hospital_id,
            FederationMembership.status == "ACTIVE",
        )
        .first()
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital is not an active member of this federation.",
        )

    # ------------------------------------------------------------
    # Verify round
    # ------------------------------------------------------------

    federation_round = (
        db.query(FederationRound)
        .filter(
            FederationRound.id == payload.round_id,
            FederationRound.federation_id
            == payload.federation_id,
        )
        .first()
    )

    if federation_round is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Federation round not found.",
        )

    if federation_round.status != "RUNNING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Round is not accepting hospital submissions. "
                f"Current status: {federation_round.status}."
            ),
        )

    # ------------------------------------------------------------
    # Verify execution mode
    # ------------------------------------------------------------

    try:
        configuration = json.loads(
            federation_round.config_json or "{}"
        )
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored round configuration is invalid JSON.",
        ) from exc

    execution_mode = configuration.get(
        "execution_mode",
        "SIMULATION",
    )

    if execution_mode != "HOSPITAL":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This round is not configured for hospital execution.",
        )

    # ------------------------------------------------------------
    # Prevent duplicate hospital submission
    # ------------------------------------------------------------

    existing_update = (
        db.query(ModelUpdate)
        .filter(
            ModelUpdate.round_id == payload.round_id,
            ModelUpdate.hospital_id == hospital_id,
        )
        .first()
    )

    if existing_update is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Hospital has already submitted an update for this round.",
        )

    # ------------------------------------------------------------
    # Train locally from the verified global model
    # ------------------------------------------------------------

    training_service = HospitalTrainingService(
        local_epochs=configuration.get("local_epochs", 1),
        batch_size=configuration.get("batch_size", 32),
        learning_rate=configuration.get("learning_rate", 0.001),
        device=configuration.get("device", "cpu"),
    )

    try:
        training_result = training_service.train_from_federation(
            db,
            hospital_id=hospital_id,
            federation_id=payload.federation_id,
            dataset_id=payload.dataset_id,
            version=payload.dataset_version,
            round_id=payload.round_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hospital training failed: {exc}",
        ) from exc

    # ------------------------------------------------------------
    # Persist SafeTensors update artifact
    # ------------------------------------------------------------

    artifact_service = UpdateArtifactService()

    try:
        (
            artifact_path,
            artifact_hash,
            artifact_size,
        ) = artifact_service.save(
            round_id=payload.round_id,
            hospital_id=hospital_id,
            update_id=training_result.update.update_id,
            delta=training_result.update.delta,
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Update artifact persistence failed: {exc}",
        ) from exc

    # ------------------------------------------------------------
    # Persist update metadata
    # ------------------------------------------------------------

    persisted_update = ModelUpdate(
        id=training_result.update.update_id,
        round_id=payload.round_id,
        hospital_id=hospital_id,
        num_examples=training_result.num_examples,
        artifact_hash=artifact_hash,
        artifact_type="safetensors",
        artifact_size=artifact_size,
        l0_status="PENDING",
        detection_status="PENDING",
        trust_status="REVIEW",
        action="REVIEW",
        submitted_at=training_result.update.created_at,
    )

    db.add(persisted_update)

    try:
        db.commit()
        db.refresh(persisted_update)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Update metadata persistence failed: {exc}",
        ) from exc

    return HospitalTrainingResponse(
        update_id=training_result.update.update_id,
        hospital_id=hospital_id,
        federation_id=payload.federation_id,
        round_id=payload.round_id,
        dataset_id=training_result.dataset_id,
        dataset_version_id=training_result.dataset_version_id,
        dataset_version=training_result.dataset_version,
        num_examples=training_result.num_examples,
        epochs_completed=training_result.epochs_completed,
        training_loss=training_result.training_loss,
        artifact_hash=artifact_hash,
        artifact_type="safetensors",
        artifact_size=artifact_size,
        security_status="PENDING_ANALYSIS",
        action="REVIEW",
        message=(
            "Local training completed. "
            "Update securely stored and queued for round security analysis."
        ),
        submitted_at=training_result.update.created_at,
    )
