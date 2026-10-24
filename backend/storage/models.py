from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.storage.database import Base


def generate_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================
# HOSPITAL
# ============================================================

class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        index=True,
        nullable=False,
    )

    # Operational information
    contact_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    contact_phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Federation eligibility
    is_eligible: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Security state
    security_status: Mapped[str] = mapped_column(
        String(30),
        default="TRUSTED",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    removed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    removal_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="hospital",
    )

    memberships: Mapped[list["FederationMembership"]] = relationship(
        back_populates="hospital",
    )

    datasets: Mapped[list["Dataset"]] = relationship(
        back_populates="hospital",
    )

    updates: Mapped[list["ModelUpdate"]] = relationship(
        back_populates="hospital",
    )

    trust_records: Mapped[list["TrustRecord"]] = relationship(
        back_populates="hospital",
    )


# ============================================================
# USER
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    hospital_id: Mapped[str | None] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=True,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    hospital: Mapped["Hospital | None"] = relationship(
        back_populates="users",
    )


# ============================================================
# FEDERATION
# ============================================================

class Federation(Base):
    __tablename__ = "federations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="ACTIVE",
        index=True,
        nullable=False,
    )

    dataset_name: Mapped[str] = mapped_column(
        String(100),
        default="MNIST",
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(200),
        default="FedSentinel CNN",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    memberships: Mapped[list["FederationMembership"]] = relationship(
        back_populates="federation",
    )

    rounds: Mapped[list["FederationRound"]] = relationship(
        back_populates="federation",
    )


# ============================================================
# FEDERATION MEMBERSHIP
# ============================================================

class FederationMembership(Base):
    __tablename__ = "federation_memberships"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    federation_id: Mapped[str] = mapped_column(
        ForeignKey("federations.id"),
        nullable=False,
        index=True,
    )

    hospital_id: Mapped[str] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="ACTIVE",
        index=True,
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    left_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    leave_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    federation: Mapped["Federation"] = relationship(
        back_populates="memberships",
    )

    hospital: Mapped["Hospital"] = relationship(
        back_populates="memberships",
    )

    __table_args__ = (
        UniqueConstraint(
            "federation_id",
            "hospital_id",
            name="uq_federation_hospital",
        ),
    )


# ============================================================
# DATASET
# ============================================================

class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    hospital_id: Mapped[str] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    dataset_type: Mapped[str] = mapped_column(
        String(100),
        default="IMAGE_CLASSIFICATION",
        nullable=False,
    )

    sample_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    num_classes: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    hospital: Mapped["Hospital"] = relationship(
        back_populates="datasets",
    )

    versions: Mapped[list["DatasetVersion"]] = relationship(
        back_populates="dataset",
    )


# ============================================================
# DATASET VERSION
# ============================================================

class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id"),
        nullable=False,
        index=True,
    )

    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    sample_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    fingerprint: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    dataset: Mapped["Dataset"] = relationship(
        back_populates="versions",
    )


# ============================================================
# MODEL
# ============================================================

class Model(Base):
    __tablename__ = "models"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    architecture: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    framework: Mapped[str] = mapped_column(
        String(100),
        default="PyTorch",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    versions: Mapped[list["ModelVersion"]] = relationship(
        back_populates="model",
    )


# ============================================================
# MODEL VERSION
# ============================================================

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    model_id: Mapped[str] = mapped_column(
        ForeignKey("models.id"),
        nullable=False,
        index=True,
    )

    version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    parent_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    round_id: Mapped[str | None] = mapped_column(
        ForeignKey("federation_rounds.id"),
        nullable=True,
        index=True,
    )

    model_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    security_status: Mapped[str] = mapped_column(
        String(50),
        default="VALIDATED",
        nullable=False,
    )

    validation_accuracy: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    accepted_update_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    quarantined_update_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    model: Mapped["Model"] = relationship(
        back_populates="versions",
    )

    round: Mapped["FederationRound | None"] = relationship(
        back_populates="model_versions",
    )


# ============================================================
# FEDERATED ROUND
# ============================================================

class FederationRound(Base):
    __tablename__ = "federation_rounds"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    federation_id: Mapped[str] = mapped_column(
        ForeignKey("federations.id"),
        nullable=False,
        index=True,
    )

    round_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="CREATED",
        index=True,
        nullable=False,
    )

    global_model_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    participating_clients: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    config_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    accepted_updates: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    quarantined_updates: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    federation: Mapped["Federation"] = relationship(
        back_populates="rounds",
    )

    model_versions: Mapped[list["ModelVersion"]] = relationship(
        back_populates="round",
    )

    updates: Mapped[list["ModelUpdate"]] = relationship(
        back_populates="round",
    )

    __table_args__ = (
        UniqueConstraint(
            "federation_id",
            "round_number",
            name="uq_federation_round_number",
        ),
    )


# ============================================================
# MODEL UPDATE
# ============================================================

class ModelUpdate(Base):
    __tablename__ = "model_updates"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    round_id: Mapped[str] = mapped_column(
        ForeignKey("federation_rounds.id"),
        nullable=False,
        index=True,
    )

    hospital_id: Mapped[str] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True,
    )

    num_examples: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    artifact_hash: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    artifact_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    artifact_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    l0_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
    )

    detection_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        index=True,
        nullable=False,
    )

    trust_status: Mapped[str] = mapped_column(
        String(50),
        default="REVIEW",
        index=True,
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(50),
        default="REVIEW",
        nullable=False,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    round: Mapped["FederationRound"] = relationship(
        back_populates="updates",
    )

    hospital: Mapped["Hospital"] = relationship(
        back_populates="updates",
    )

    evidence: Mapped[list["UpdateEvidence"]] = relationship(
        back_populates="update",
    )


# ============================================================
# UPDATE EVIDENCE
# ============================================================

class UpdateEvidence(Base):
    __tablename__ = "update_evidence"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    update_id: Mapped[str] = mapped_column(
        ForeignKey("model_updates.id"),
        nullable=False,
        index=True,
    )

    layer: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    signal: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    update: Mapped["ModelUpdate"] = relationship(
        back_populates="evidence",
    )


# ============================================================
# TRUST RECORD
# ============================================================

class TrustRecord(Base):
    __tablename__ = "trust_records"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    hospital_id: Mapped[str] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True,
    )

    round_id: Mapped[str | None] = mapped_column(
        ForeignKey("federation_rounds.id"),
        nullable=True,
        index=True,
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    hospital: Mapped["Hospital"] = relationship(
        back_populates="trust_records",
    )


# ============================================================
# INCIDENT
# ============================================================

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    hospital_id: Mapped[str | None] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=True,
        index=True,
    )

    round_id: Mapped[str | None] = mapped_column(
        ForeignKey("federation_rounds.id"),
        nullable=True,
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    threat_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="OPEN",
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    incident_code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    recommended_action: Mapped[str] = mapped_column(
        String(50),
        default="REVIEW",
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    evidence_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
        nullable=False,
    )

    assigned_to: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    resolution_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


# ============================================================
# ADMIN ACTION
# ============================================================

class AdminAction(Base):
    __tablename__ = "admin_actions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    actor_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    hospital_id: Mapped[str | None] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    previous_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    new_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result: Mapped[str] = mapped_column(
        String(50),
        default="SUCCESS",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )


# ============================================================
# REFRESH SESSION
# ============================================================

class RefreshSession(Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    token_hash: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    replaced_by_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )


# ============================================================
# AUDIT EVENT
# ============================================================

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    actor_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    resource_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result: Mapped[str] = mapped_column(
        String(50),
        default="SUCCESS",
        nullable=False,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    session_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    metadata_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )
