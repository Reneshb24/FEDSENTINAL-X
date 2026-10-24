"""
Hospital Portal dataset APIs.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import UploadFile
from fastapi import status
from sqlalchemy.orm import Session

from backend.api.dependencies import (
    ensure_hospital_access,
    require_hospital_access,
)
from backend.schemas.dataset import (
    DatasetCreate,
    DatasetLinkImportRequest,
    DatasetResponse,
    DatasetUpdate,
    DatasetVersionCreate,
    DatasetVersionResponse,
    DatasetUploadResponse,
)
from backend.services.dataset_service import DatasetService
from backend.storage.database import get_db
from backend.storage.models import User


router = APIRouter(
    prefix="/hospital/datasets",
    tags=["Hospital Datasets"],
)


# ============================================================================
# LIST MY DATASETS
# ============================================================================

@router.get(
    "",
    response_model=list[DatasetResponse],
)
def list_my_datasets(
    current_user: User = Depends(require_hospital_access),
    db: Session = Depends(get_db),
):
    hospital_id = current_user.hospital_id

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    return DatasetService.list_datasets(
        db,
        hospital_id=hospital_id,
    )


# ============================================================================
# CREATE DATASET
# ============================================================================

@router.post(
    "",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dataset(
    payload: DatasetCreate,
    current_user: User = Depends(require_hospital_access),
    db: Session = Depends(get_db),
):
    hospital_id = current_user.hospital_id

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    return DatasetService.create_dataset(
        db,
        hospital_id=hospital_id,
        actor_user_id=current_user.id,
        payload=payload,
    )


# ============================================================================
# GET DATASET
# ============================================================================

@router.get(
    "/{dataset_id}",
    response_model=DatasetResponse,
)
def get_dataset(
    dataset_id: str,
    current_user: User = Depends(require_hospital_access),
    db: Session = Depends(get_db),
):
    hospital_id = current_user.hospital_id

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    return DatasetService.get_dataset(
        db,
        hospital_id=hospital_id,
        dataset_id=dataset_id,
    )


# ============================================================================
# UPDATE DATASET
# ============================================================================

@router.patch(
    "/{dataset_id}",
    response_model=DatasetResponse,
)
def update_dataset(
    dataset_id: str,
    payload: DatasetUpdate,
    current_user: User = Depends(require_hospital_access),
    db: Session = Depends(get_db),
):
    hospital_id = current_user.hospital_id

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    return DatasetService.update_dataset(
        db,
        hospital_id=hospital_id,
        actor_user_id=current_user.id,
        dataset_id=dataset_id,
        payload=payload,
    )


# ============================================================================
# CREATE DATASET VERSION
# ============================================================================

@router.post(
    "/{dataset_id}/versions",
    response_model=DatasetVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dataset_version(
    dataset_id: str,
    payload: DatasetVersionCreate,
    current_user: User = Depends(require_hospital_access),
    db: Session = Depends(get_db),
):
    hospital_id = current_user.hospital_id

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    return DatasetService.create_version(
        db,
        hospital_id=hospital_id,
        actor_user_id=current_user.id,
        dataset_id=dataset_id,
        payload=payload,
    )


# ============================================================================
# LIST DATASET VERSIONS
# ============================================================================

@router.get(
    "/{dataset_id}/versions",
    response_model=list[DatasetVersionResponse],
)
def list_dataset_versions(
    dataset_id: str,
    current_user: User = Depends(require_hospital_access),
    db: Session = Depends(get_db),
):
    hospital_id = current_user.hospital_id

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    return DatasetService.list_versions(
        db,
        hospital_id=hospital_id,
        dataset_id=dataset_id,
    )


# ============================================================================
# ACTIVATE DATASET
# ============================================================================

@router.post(
    "/{dataset_id}/activate",
    response_model=DatasetResponse,
)
def activate_dataset(
    dataset_id: str,
    current_user: User = Depends(require_hospital_access),
    db: Session = Depends(get_db),
):
    hospital_id = current_user.hospital_id

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    return DatasetService.set_active(
        db,
        hospital_id=hospital_id,
        actor_user_id=current_user.id,
        dataset_id=dataset_id,
        active=True,
    )


# ============================================================================
# DEACTIVATE DATASET
# ============================================================================

@router.post(
    "/{dataset_id}/deactivate",
    response_model=DatasetResponse,
)
def deactivate_dataset(
    dataset_id: str,
    current_user: User = Depends(require_hospital_access),
    db: Session = Depends(get_db),
):
    hospital_id = current_user.hospital_id

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    return DatasetService.set_active(
        db,
        hospital_id=hospital_id,
        actor_user_id=current_user.id,
        dataset_id=dataset_id,
        active=False,
    )


# ============================================================================
# REAL DATASET UPLOAD
# ============================================================================

@router.post(
    "/{dataset_id}/versions/upload",
    response_model=DatasetUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_dataset_version(
    dataset_id: str,
    version: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_hospital_access),
    db: Session = Depends(get_db),
):
    """
    Upload a real hospital-local dataset version.

    The uploaded artifact is validated locally and stored under
    the hospital's dataset storage boundary.

    Only metadata/fingerprint/sample statistics are persisted in
    the FedSentinel database.
    """

    hospital_id = current_user.hospital_id

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    (
        dataset_version,
        file_size,
        fingerprint,
        class_count,
    ) = DatasetService.upload_version(
        db,
        hospital_id=hospital_id,
        actor_user_id=current_user.id,
        dataset_id=dataset_id,
        version_name=version,
        upload=file,
    )

    return DatasetUploadResponse(
        dataset_id=dataset_version.dataset_id,
        dataset_version_id=dataset_version.id,
        hospital_id=hospital_id,
        version=dataset_version.version,
        filename=file.filename or "dataset.npz",
        file_size=file_size,
        fingerprint=fingerprint,
        sample_count=dataset_version.sample_count,
        num_classes=class_count,
        storage_status="STORED_LOCALLY",
        validation_status="VALIDATED",
        message=(
            "Dataset uploaded, validated and stored "
            "within the hospital dataset boundary."
        ),
    )


# ============================================================================
# LINK / REMOTE RECORD IMPORT
# ============================================================================

@router.post(
    "/{dataset_id}/versions/link",
    response_model=DatasetUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def link_dataset_version(
    dataset_id: str,
    payload: DatasetLinkImportRequest,
    current_user: User = Depends(require_hospital_access),
    db: Session = Depends(get_db),
):
    """
    Import a real hospital-local dataset version from an external record URL,
    EHR record link, or local filesystem path.

    The dataset is fetched, validated against structural CNN constraints,
    stored securely inside the hospital boundary, and registered.
    """
    hospital_id = current_user.hospital_id

    ensure_hospital_access(
        current_user,
        hospital_id,
    )

    (
        dataset_version,
        file_size,
        fingerprint,
        class_count,
    ) = DatasetService.import_version_from_link(
        db,
        hospital_id=hospital_id,
        actor_user_id=current_user.id,
        dataset_id=dataset_id,
        version_name=payload.version,
        record_link=payload.record_link,
        format_type=payload.format,
    )

    return DatasetUploadResponse(
        dataset_id=dataset_version.dataset_id,
        dataset_version_id=dataset_version.id,
        hospital_id=hospital_id,
        version=dataset_version.version,
        filename=f"record_link_{payload.version}.npz",
        file_size=file_size,
        fingerprint=fingerprint,
        sample_count=dataset_version.sample_count,
        num_classes=class_count,
        storage_status="STORED_LOCALLY",
        validation_status="VALIDATED",
        message=(
            f"Record data from '{payload.record_link}' successfully processed, "
            f"validated ({dataset_version.sample_count} samples), and stored within hospital boundary."
        ),
    )
