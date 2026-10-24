"""
Pydantic schemas for hospital dataset management.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# CREATE DATASET
# ============================================================================

class DatasetCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=200,
    )

    dataset_type: str = Field(
        default="IMAGE_CLASSIFICATION",
        min_length=2,
        max_length=100,
    )

    sample_count: int = Field(
        default=0,
        ge=0,
    )

    num_classes: int = Field(
        default=10,
        ge=1,
    )


# ============================================================================
# UPDATE DATASET
# ============================================================================

class DatasetUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    dataset_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    num_classes: int | None = Field(
        default=None,
        ge=1,
    )


# ============================================================================
# CREATE DATASET VERSION - METADATA MODE
# ============================================================================

class DatasetVersionCreate(BaseModel):
    version: str = Field(
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z0-9._-]+$",
    )

    sample_count: int = Field(
        default=0,
        ge=0,
    )

    fingerprint: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
    )


# ============================================================================
# LINK / IMPORT DATASET VERSION
# ============================================================================

class DatasetLinkImportRequest(BaseModel):
    version: str = Field(
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z0-9._-]+$",
    )

    record_link: str = Field(
        min_length=2,
        description="HTTP/HTTPS record URL or local filesystem path to records",
    )

    format: str = Field(
        default="AUTO",
        description="Format: AUTO, NPZ, CSV, or RECORDS_ARCHIVE",
    )



# ============================================================================
# RESPONSES
# ============================================================================

class DatasetVersionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    dataset_id: str
    version: str
    sample_count: int
    fingerprint: str | None
    created_at: datetime


class DatasetResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    hospital_id: str
    name: str
    dataset_type: str
    sample_count: int
    num_classes: int
    is_active: bool
    created_at: datetime
    versions: list[DatasetVersionResponse] = []


# ============================================================================
# DATASET UPLOAD RESPONSE
# ============================================================================

class DatasetUploadResponse(BaseModel):
    dataset_id: str
    dataset_version_id: str
    hospital_id: str
    version: str
    filename: str
    file_size: int
    fingerprint: str
    sample_count: int
    num_classes: int
    storage_status: str
    validation_status: str
    message: str
