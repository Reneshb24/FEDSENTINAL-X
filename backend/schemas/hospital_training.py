from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HospitalTrainingRequest(BaseModel):
    round_id: str = Field(
        min_length=1,
        max_length=36,
    )

    federation_id: str = Field(
        min_length=1,
        max_length=36,
    )

    dataset_id: str = Field(
        min_length=1,
        max_length=36,
    )

    dataset_version: str = Field(
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z0-9._-]+$",
    )


class HospitalTrainingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    update_id: str
    hospital_id: str
    federation_id: str
    round_id: str

    dataset_id: str
    dataset_version_id: str
    dataset_version: str

    num_examples: int
    epochs_completed: int
    training_loss: float

    artifact_hash: str
    artifact_type: str
    artifact_size: int

    security_status: str
    action: str

    message: str
    submitted_at: datetime | None = None
