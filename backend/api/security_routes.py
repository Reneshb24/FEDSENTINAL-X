from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from backend.api.dependencies import get_current_user, require_security_analyst
from backend.storage.database import SessionLocal
from backend.storage.models import (
    FederationRound,
    Hospital,
    Incident,
    ModelUpdate,
    ModelVersion,
    TrustRecord,
    UpdateEvidence,
    User,
)


router = APIRouter(
    prefix="/security",
    tags=["Security Investigation"],
)


# ============================================================
# RESPONSE MODELS
# ============================================================


class SecurityEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    update_id: str
    layer: str
    signal: str
    score: float | None
    explanation: str | None
    created_at: Any


class SecurityUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    round_id: str
    hospital_id: str
    hospital_code: str | None = None
    hospital_name: str | None = None

    artifact_hash: str | None
    artifact_type: str | None
    artifact_size: int | None

    l0_status: str | None
    detection_status: str | None
    trust_status: str | None
    action: str | None

    submitted_at: Any

    evidence: list[SecurityEvidenceResponse] = []


class TrustRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    hospital_id: str
    hospital_code: str | None = None
    hospital_name: str | None = None
    round_id: str
    score: float
    status: str
    reason: str | None
    created_at: Any


class SecurityIncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    hospital_id: str
    hospital_code: str | None = None
    hospital_name: str | None = None
    round_id: str

    severity: str
    threat_type: str
    status: str
    title: str
    description: str

    created_at: Any
    resolved_at: Any | None

    incident_code: str
    recommended_action: str | None

    risk_score: float | None
    confidence: float | None

    evidence: Any | None
    assigned_to: str | None
    resolution_notes: str | None


class SecurityRoundSummaryResponse(BaseModel):
    round_id: str
    federation_id: str
    round_number: int
    status: str

    participating_clients: int
    accepted_updates: int
    quarantined_updates: int

    total_updates: int
    evidence_count: int
    trust_record_count: int
    incident_count: int

    global_model_version: str | None
    config: dict[str, Any]


# ============================================================
# HELPERS
# ============================================================


def _enum_value(value: Any) -> Any:
    """
    Convert SQLAlchemy/Python enum values into JSON-safe values.
    """
    if value is None:
        return None

    return getattr(value, "value", value)


def _parse_config(value: str | None) -> dict[str, Any]:
    if not value:
        return {}

    try:
        parsed = json.loads(value)

        if isinstance(parsed, dict):
            return parsed

        return {}

    except (TypeError, json.JSONDecodeError):
        return {}


def _get_hospital_map(
    db,
    hospital_ids: set[str],
) -> dict[str, Hospital]:
    if not hospital_ids:
        return {}

    hospitals = (
        db.query(Hospital)
        .filter(Hospital.id.in_(hospital_ids))
        .all()
    )

    return {hospital.id: hospital for hospital in hospitals}


# ============================================================
# ROUND SUMMARY
# ============================================================


@router.get(
    "/rounds/{round_id}",
    response_model=SecurityRoundSummaryResponse,
)
def get_security_round(
    round_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Return the persisted security summary for a federation round.

    Read-only endpoint.
    """

    db = SessionLocal()

    try:
        federation_round = (
            db.query(FederationRound)
            .filter(FederationRound.id == round_id)
            .first()
        )

        if federation_round is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Federation round not found.",
            )

        updates = (
            db.query(ModelUpdate)
            .filter(ModelUpdate.round_id == round_id)
            .all()
        )

        evidence_count = (
            db.query(UpdateEvidence)
            .join(
                ModelUpdate,
                UpdateEvidence.update_id == ModelUpdate.id,
            )
            .filter(ModelUpdate.round_id == round_id)
            .count()
        )

        trust_count = (
            db.query(TrustRecord)
            .filter(TrustRecord.round_id == round_id)
            .count()
        )

        incident_count = (
            db.query(Incident)
            .filter(Incident.round_id == round_id)
            .count()
        )

        return SecurityRoundSummaryResponse(
            round_id=federation_round.id,
            federation_id=federation_round.federation_id,
            round_number=federation_round.round_number,
            status=_enum_value(federation_round.status),
            participating_clients=federation_round.participating_clients or 0,
            accepted_updates=federation_round.accepted_updates or 0,
            quarantined_updates=federation_round.quarantined_updates or 0,
            total_updates=len(updates),
            evidence_count=evidence_count,
            trust_record_count=trust_count,
            incident_count=incident_count,
            global_model_version=federation_round.global_model_version,
            config=_parse_config(federation_round.config_json),
        )

    finally:
        db.close()


# ============================================================
# UPDATES + EVIDENCE
# ============================================================


@router.get(
    "/rounds/{round_id}/updates",
    response_model=list[SecurityUpdateResponse],
)
def get_security_updates(
    round_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Return all persisted model updates and their L0-L5 evidence.
    """

    db = SessionLocal()

    try:
        federation_round = (
            db.query(FederationRound)
            .filter(FederationRound.id == round_id)
            .first()
        )

        if federation_round is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Federation round not found.",
            )

        updates = (
            db.query(ModelUpdate)
            .filter(ModelUpdate.round_id == round_id)
            .order_by(ModelUpdate.submitted_at)
            .all()
        )

        hospital_ids = {update.hospital_id for update in updates}
        hospitals = _get_hospital_map(db, hospital_ids)

        update_ids = [update.id for update in updates]

        evidence_rows = []

        if update_ids:
            evidence_rows = (
                db.query(UpdateEvidence)
                .filter(UpdateEvidence.update_id.in_(update_ids))
                .order_by(UpdateEvidence.created_at)
                .all()
            )

        evidence_by_update: dict[str, list[SecurityEvidenceResponse]] = {}

        for evidence in evidence_rows:
            evidence_by_update.setdefault(
                evidence.update_id,
                [],
            ).append(
                SecurityEvidenceResponse(
                    id=evidence.id,
                    update_id=evidence.update_id,
                    layer=_enum_value(evidence.layer),
                    signal=evidence.signal,
                    score=evidence.score,
                    explanation=evidence.explanation,
                    created_at=evidence.created_at,
                )
            )

        response: list[SecurityUpdateResponse] = []

        for update in updates:
            hospital = hospitals.get(update.hospital_id)

            response.append(
                SecurityUpdateResponse(
                    id=update.id,
                    round_id=update.round_id,
                    hospital_id=update.hospital_id,
                    hospital_code=getattr(hospital, "code", None),
                    hospital_name=getattr(hospital, "name", None),
                    artifact_hash=update.artifact_hash,
                    artifact_type=update.artifact_type,
                    artifact_size=update.artifact_size,
                    l0_status=_enum_value(update.l0_status),
                    detection_status=_enum_value(update.detection_status),
                    trust_status=_enum_value(update.trust_status),
                    action=_enum_value(update.action),
                    submitted_at=update.submitted_at,
                    evidence=evidence_by_update.get(update.id, []),
                )
            )

        return response

    finally:
        db.close()


# ============================================================
# SINGLE UPDATE
# ============================================================


@router.get(
    "/rounds/{round_id}/updates/{update_id}",
    response_model=SecurityUpdateResponse,
)
def get_security_update(
    round_id: str,
    update_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Return one update with its complete persisted security evidence.
    """

    db = SessionLocal()

    try:
        update = (
            db.query(ModelUpdate)
            .filter(
                ModelUpdate.id == update_id,
                ModelUpdate.round_id == round_id,
            )
            .first()
        )

        if update is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model update not found.",
            )

        hospital = (
            db.query(Hospital)
            .filter(Hospital.id == update.hospital_id)
            .first()
        )

        evidence_rows = (
            db.query(UpdateEvidence)
            .filter(UpdateEvidence.update_id == update.id)
            .order_by(UpdateEvidence.created_at)
            .all()
        )

        evidence = [
            SecurityEvidenceResponse(
                id=item.id,
                update_id=item.update_id,
                layer=_enum_value(item.layer),
                signal=item.signal,
                score=item.score,
                explanation=item.explanation,
                created_at=item.created_at,
            )
            for item in evidence_rows
        ]

        return SecurityUpdateResponse(
            id=update.id,
            round_id=update.round_id,
            hospital_id=update.hospital_id,
            hospital_code=getattr(hospital, "code", None),
            hospital_name=getattr(hospital, "name", None),
            artifact_hash=update.artifact_hash,
            artifact_type=update.artifact_type,
            artifact_size=update.artifact_size,
            l0_status=_enum_value(update.l0_status),
            detection_status=_enum_value(update.detection_status),
            trust_status=_enum_value(update.trust_status),
            action=_enum_value(update.action),
            submitted_at=update.submitted_at,
            evidence=evidence,
        )

    finally:
        db.close()


# ============================================================
# TRUST
# ============================================================


@router.get(
    "/rounds/{round_id}/trust",
    response_model=list[TrustRecordResponse],
)
def get_round_trust(
    round_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Return persisted hospital trust records for a round.
    """

    db = SessionLocal()

    try:
        federation_round = (
            db.query(FederationRound)
            .filter(FederationRound.id == round_id)
            .first()
        )

        if federation_round is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Federation round not found.",
            )

        records = (
            db.query(TrustRecord)
            .filter(TrustRecord.round_id == round_id)
            .order_by(TrustRecord.score.desc())
            .all()
        )

        hospital_ids = {record.hospital_id for record in records}
        hospitals = _get_hospital_map(db, hospital_ids)

        return [
            TrustRecordResponse(
                id=record.id,
                hospital_id=record.hospital_id,
                hospital_code=getattr(
                    hospitals.get(record.hospital_id),
                    "code",
                    None,
                ),
                hospital_name=getattr(
                    hospitals.get(record.hospital_id),
                    "name",
                    None,
                ),
                round_id=record.round_id,
                score=record.score,
                status=_enum_value(record.status),
                reason=record.reason,
                created_at=record.created_at,
            )
            for record in records
        ]

    finally:
        db.close()


# ============================================================
# INCIDENTS
# ============================================================


@router.get(
    "/rounds/{round_id}/incidents",
    response_model=list[SecurityIncidentResponse],
)
def get_round_incidents(
    round_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Return persisted incidents for one round.
    """

    db = SessionLocal()

    try:
        federation_round = (
            db.query(FederationRound)
            .filter(FederationRound.id == round_id)
            .first()
        )

        if federation_round is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Federation round not found.",
            )

        incidents = (
            db.query(Incident)
            .filter(Incident.round_id == round_id)
            .order_by(Incident.created_at)
            .all()
        )

        hospital_ids = {incident.hospital_id for incident in incidents}
        hospitals = _get_hospital_map(db, hospital_ids)

        return [
            SecurityIncidentResponse(
                id=incident.id,
                hospital_id=incident.hospital_id,
                hospital_code=getattr(
                    hospitals.get(incident.hospital_id),
                    "code",
                    None,
                ),
                hospital_name=getattr(
                    hospitals.get(incident.hospital_id),
                    "name",
                    None,
                ),
                round_id=incident.round_id,
                severity=_enum_value(incident.severity),
                threat_type=_enum_value(incident.threat_type),
                status=_enum_value(incident.status),
                title=incident.title,
                description=incident.description,
                created_at=incident.created_at,
                resolved_at=incident.resolved_at,
                incident_code=incident.incident_code,
                recommended_action=_enum_value(
                    incident.recommended_action
                ),
                risk_score=incident.risk_score,
                confidence=incident.confidence,
                evidence=incident.evidence_json,
                assigned_to=incident.assigned_to,
                resolution_notes=incident.resolution_notes,
            )
            for incident in incidents
        ]

    finally:
        db.close()

# ============================================================
# ADMIN SECURITY ACTIONS (OVERRIDE / QUARANTINE / RELEASE)
# ============================================================

class UpdateActionPayload(BaseModel):
    reason: str = "Administrator override"


class IncidentStatusPayload(BaseModel):
    status: str
    resolution_notes: str | None = None


@router.post(
    "/updates/{update_id}/quarantine",
    response_model=SecurityUpdateResponse,
)
def admin_quarantine_update(
    update_id: str,
    payload: UpdateActionPayload,
    current_user: User = Depends(require_security_analyst),
):
    """
    Explicit audited admin override: move update into quarantine.
    """
    db = SessionLocal()
    try:
        update = db.query(ModelUpdate).filter(ModelUpdate.id == update_id).first()
        if not update:
            raise HTTPException(status_code=404, detail="Model update not found.")

        prev_status = update.detection_status
        update.detection_status = "QUARANTINED"
        update.action = "QUARANTINE"
        db.commit()
        db.refresh(update)

        from backend.services.audit import record_audit
        record_audit(
            db,
            actor_user_id=current_user.id,
            action="UPDATE_QUARANTINED_BY_ADMIN",
            resource_type="MODEL_UPDATE",
            resource_id=update.id,
            reason=payload.reason,
            metadata={
                "previous_status": prev_status,
                "new_status": "QUARANTINED",
                "round_id": update.round_id,
                "hospital_id": update.hospital_id,
            },
        )
        hospital = db.query(Hospital).filter(Hospital.id == update.hospital_id).first()
        evidence_rows = db.query(UpdateEvidence).filter(UpdateEvidence.update_id == update.id).all()
        return SecurityUpdateResponse(
            id=update.id,
            round_id=update.round_id,
            hospital_id=update.hospital_id,
            hospital_code=getattr(hospital, "code", None),
            hospital_name=getattr(hospital, "name", None),
            artifact_hash=update.artifact_hash,
            artifact_type=update.artifact_type,
            artifact_size=update.artifact_size,
            l0_status=_enum_value(update.l0_status),
            detection_status="QUARANTINED",
            trust_status=_enum_value(update.trust_status),
            action="QUARANTINE",
            submitted_at=update.submitted_at,
            evidence=[
                SecurityEvidenceResponse(
                    id=e.id,
                    update_id=e.update_id,
                    layer=_enum_value(e.layer),
                    signal=e.signal,
                    score=e.score,
                    explanation=e.explanation,
                    created_at=e.created_at,
                )
                for e in evidence_rows
            ],
        )
    finally:
        db.close()


@router.post(
    "/updates/{update_id}/release",
    response_model=SecurityUpdateResponse,
)
def admin_release_update(
    update_id: str,
    payload: UpdateActionPayload,
    current_user: User = Depends(require_security_analyst),
):
    """
    Explicit audited admin override: release update from quarantine.
    """
    db = SessionLocal()
    try:
        update = db.query(ModelUpdate).filter(ModelUpdate.id == update_id).first()
        if not update:
            raise HTTPException(status_code=404, detail="Model update not found.")

        prev_status = update.detection_status
        update.detection_status = "ACCEPTED"
        update.action = "ACCEPT"
        db.commit()
        db.refresh(update)

        from backend.services.audit import record_audit
        record_audit(
            db,
            actor_user_id=current_user.id,
            action="UPDATE_RELEASED_BY_ADMIN",
            resource_type="MODEL_UPDATE",
            resource_id=update.id,
            reason=payload.reason,
            metadata={
                "previous_status": prev_status,
                "new_status": "ACCEPTED",
                "round_id": update.round_id,
                "hospital_id": update.hospital_id,
            },
        )
        hospital = db.query(Hospital).filter(Hospital.id == update.hospital_id).first()
        evidence_rows = db.query(UpdateEvidence).filter(UpdateEvidence.update_id == update.id).all()
        return SecurityUpdateResponse(
            id=update.id,
            round_id=update.round_id,
            hospital_id=update.hospital_id,
            hospital_code=getattr(hospital, "code", None),
            hospital_name=getattr(hospital, "name", None),
            artifact_hash=update.artifact_hash,
            artifact_type=update.artifact_type,
            artifact_size=update.artifact_size,
            l0_status=_enum_value(update.l0_status),
            detection_status="ACCEPTED",
            trust_status=_enum_value(update.trust_status),
            action="ACCEPT",
            submitted_at=update.submitted_at,
            evidence=[
                SecurityEvidenceResponse(
                    id=e.id,
                    update_id=e.update_id,
                    layer=_enum_value(e.layer),
                    signal=e.signal,
                    score=e.score,
                    explanation=e.explanation,
                    created_at=e.created_at,
                )
                for e in evidence_rows
            ],
        )
    finally:
        db.close()


@router.post(
    "/incidents/{incident_id}/status",
    response_model=SecurityIncidentResponse,
)
def update_incident_status(
    incident_id: str,
    payload: IncidentStatusPayload,
    current_user: User = Depends(require_security_analyst),
):
    """
    Update incident lifecycle status with audit logging.
    """
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found.")

        prev_status = incident.status
        incident.status = payload.status
        if payload.resolution_notes:
            incident.resolution_notes = payload.resolution_notes
        if payload.status in {"RESOLVED", "CLOSED"} and not incident.resolved_at:
            from datetime import datetime, timezone
            incident.resolved_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(incident)

        from backend.services.audit import record_audit
        record_audit(
            db,
            actor_user_id=current_user.id,
            action="INCIDENT_STATUS_UPDATED",
            resource_type="INCIDENT",
            resource_id=incident.id,
            reason=f"Status changed from {prev_status} to {payload.status}",
            metadata={
                "previous_status": prev_status,
                "new_status": payload.status,
                "resolution_notes": payload.resolution_notes,
            },
        )
        hospital = db.query(Hospital).filter(Hospital.id == incident.hospital_id).first()
        return SecurityIncidentResponse(
            id=incident.id,
            hospital_id=incident.hospital_id,
            hospital_code=getattr(hospital, "code", None),
            hospital_name=getattr(hospital, "name", None),
            round_id=incident.round_id,
            severity=_enum_value(incident.severity),
            threat_type=_enum_value(incident.threat_type),
            status=_enum_value(incident.status),
            title=incident.title,
            description=incident.description,
            created_at=incident.created_at,
            resolved_at=incident.resolved_at,
            incident_code=incident.incident_code,
            recommended_action=_enum_value(incident.recommended_action),
            risk_score=incident.risk_score,
            confidence=incident.confidence,
            evidence=incident.evidence_json,
            assigned_to=incident.assigned_to,
            resolution_notes=incident.resolution_notes,
        )
    finally:
        db.close()

