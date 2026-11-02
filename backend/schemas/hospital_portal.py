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


# ============================================================================
# DISEASE PREDICTION / INFERENCE SCHEMAS
# ============================================================================

class ClinicalFeatures(BaseModel):
    pregnancies: float = 0.0
    glucose: float = 120.0
    blood_pressure: float = 70.0
    skin_thickness: float = 20.0
    insulin: float = 80.0
    bmi: float = 25.0
    diabetes_pedigree: float = 0.5
    age: float = 35.0


class DifferentialDiagnosis(BaseModel):
    condition: str
    probability: float
    confidence_tier: str


class DiseasePredictionRequest(BaseModel):
    patient_id: str | None = None
    modality: str = "AUTO"  # "IMAGE", "TEXT", "STRUCTURED_VITALS", "AUTO"
    condition: str = "AUTO_DETECT"
    image_data: str | None = None  # Base64 data URL
    clinical_text: str | None = None  # Clinical notes / EHR text
    features: ClinicalFeatures | None = None


class DiseasePredictionResponse(BaseModel):
    prediction_id: str
    patient_id: str | None = None
    modality: str
    condition: str
    model_version: str
    prediction: str
    probability: float
    risk_level: str
    enclave_privacy: str
    findings_summary: str
    extracted_features: dict[str, str | float] | None = None
    differentials: list[DifferentialDiagnosis] | None = None
    biomarker_importance: dict[str, float]
    clinical_recommendation: str
    is_out_of_distribution: bool = False
    contributing_hospitals: list[dict[str, str | int]] | None = None
    executed_at: datetime


# ============================================================================
# GLOBAL MODEL STATUS SCHEMAS
# ============================================================================

class GlobalModelContextResponse(BaseModel):
    federation_id: str
    federation_name: str
    model_name: str
    version: str
    model_hash: str
    architecture: str
    total_parameters: int
    input_shape: str
    output_shape: str
    convergence_status: str
    synchronization_status: str
    last_updated_at: datetime | None = None
    round_number: int | None = None
    total_rounds: int
    accepted_updates_total: int
    quarantined_updates_total: int
