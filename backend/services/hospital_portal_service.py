from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.auth.security import hash_password
from backend.schemas.hospital import (
    HospitalStaffCreateRequest,
    HospitalStaffUpdateRequest,
    HospitalUpdate,
)
from backend.services.audit import record_audit
from backend.storage.models import (
    Dataset,
    FederationMembership,
    Incident,
    ModelUpdate,
    TrustRecord,
    Hospital,
    User,
)


class HospitalPortalService:

    # ========================================================================
    # GET HOSPITAL
    # ========================================================================

    @staticmethod
    def get_hospital(
        db: Session,
        hospital_id: str,
    ) -> Hospital | None:

        return (
            db.query(Hospital)
            .filter(
                Hospital.id == hospital_id,
            )
            .first()
        )

    # ========================================================================
    # GET FEDERATION MEMBERSHIP
    # ========================================================================

    @staticmethod
    def get_membership(
        db: Session,
        hospital_id: str,
    ) -> FederationMembership | None:

        return (
            db.query(FederationMembership)
            .filter(
                FederationMembership.hospital_id
                == hospital_id,

                FederationMembership.status == "ACTIVE",
            )
            .first()
        )

    # ========================================================================
    # DASHBOARD
    # ========================================================================

    @staticmethod
    def get_dashboard(
        db: Session,
        hospital_id: str,
    ) -> dict:

        hospital = (
            db.query(Hospital)
            .filter(
                Hospital.id == hospital_id,
            )
            .first()
        )

        if hospital is None:
            raise ValueError(
                "Hospital not found"
            )

        # --------------------------------------------------------------------
        # Federation
        # --------------------------------------------------------------------

        membership = (
            db.query(FederationMembership)
            .filter(
                FederationMembership.hospital_id
                == hospital_id,

                FederationMembership.status == "ACTIVE",
            )
            .first()
        )

        # --------------------------------------------------------------------
        # Datasets
        # --------------------------------------------------------------------

        datasets = (
            db.query(Dataset)
            .filter(
                Dataset.hospital_id == hospital_id,
            )
            .all()
        )

        active_datasets = [
            dataset
            for dataset in datasets
            if dataset.is_active
        ]

        # --------------------------------------------------------------------
        # Updates
        # --------------------------------------------------------------------

        updates = (
            db.query(ModelUpdate)
            .filter(
                ModelUpdate.hospital_id == hospital_id,
            )
            .all()
        )

        accepted_updates = [
            update
            for update in updates
            if update.action == "ACCEPT"
        ]

        quarantined_updates = [
            update
            for update in updates
            if update.action == "QUARANTINE"
        ]

        # --------------------------------------------------------------------
        # Trust
        # --------------------------------------------------------------------

        latest_trust = (
            db.query(TrustRecord)
            .filter(
                TrustRecord.hospital_id
                == hospital_id,
            )
            .order_by(
                TrustRecord.created_at.desc()
            )
            .first()
        )

        # --------------------------------------------------------------------
        # Incidents
        # --------------------------------------------------------------------

        open_incidents = (
            db.query(Incident)
            .filter(
                Incident.hospital_id == hospital_id,
                Incident.status == "OPEN",
            )
            .count()
        )

        return {
            "hospital": hospital,

            "federation_member": (
                membership is not None
            ),

            "membership_status": (
                membership.status
                if membership
                else None
            ),

            "total_datasets": len(datasets),

            "active_datasets": len(
                active_datasets
            ),

            "total_updates": len(updates),

            "accepted_updates": len(
                accepted_updates
            ),

            "quarantined_updates": len(
                quarantined_updates
            ),

            "trust_score": (
                latest_trust.score
                if latest_trust
                else None
            ),

            "trust_status": (
                latest_trust.status
                if latest_trust
                else None
            ),

            "open_incidents": open_incidents,
        }

    # ========================================================================
    # STATUS
    # ========================================================================

    @staticmethod
    def get_status(
        db: Session,
        hospital_id: str,
    ) -> dict:

        hospital = (
            db.query(Hospital)
            .filter(
                Hospital.id == hospital_id,
            )
            .first()
        )

        if hospital is None:
            raise ValueError(
                "Hospital not found"
            )

        membership = (
            db.query(FederationMembership)
            .filter(
                FederationMembership.hospital_id
                == hospital_id,

                FederationMembership.status == "ACTIVE",
            )
            .first()
        )

        return {
            "hospital_id": hospital.id,

            "status": hospital.status,

            "security_status": (
                hospital.security_status
            ),

            "is_eligible": (
                hospital.is_eligible
            ),

            "federation_member": (
                membership is not None
            ),

            "membership_status": (
                membership.status
                if membership
                else None
            ),
        }

    # ========================================================================
    # STAFF / TEAM MANAGEMENT
    # ========================================================================

    @staticmethod
    def get_staff(
        db: Session,
        hospital_id: str,
    ) -> list[User]:
        return (
            db.query(User)
            .filter(User.hospital_id == hospital_id)
            .order_by(User.created_at.asc())
            .all()
        )

    @staticmethod
    def create_staff(
        db: Session,
        *,
        hospital_id: str,
        actor_user_id: str,
        payload: HospitalStaffCreateRequest,
    ) -> User:
        email = payload.email.strip().lower()
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists.",
            )

        valid_roles = ["HOSPITAL_ADMIN", "HOSPITAL_OPERATOR", "HOSPITAL_ANALYST"]
        role = payload.role.strip().upper() if payload.role else "HOSPITAL_OPERATOR"
        if role not in valid_roles:
            role = "HOSPITAL_OPERATOR"

        new_user = User(
            email=email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name.strip(),
            role=role,
            hospital_id=hospital_id,
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_STAFF_CREATED",
            resource_type="user",
            resource_id=new_user.id,
            result="SUCCESS",
            metadata={
                "hospital_id": hospital_id,
                "staff_email": email,
                "role": role,
            },
        )
        return new_user

    @staticmethod
    def update_staff(
        db: Session,
        *,
        hospital_id: str,
        actor_user_id: str,
        user_id: str,
        payload: HospitalStaffUpdateRequest,
    ) -> User:
        target_user = (
            db.query(User)
            .filter(
                User.id == user_id,
                User.hospital_id == hospital_id,
            )
            .first()
        )
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff member not found in this hospital enclave.",
            )

        if payload.is_active is False and target_user.id == actor_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own administrator account.",
            )

        if payload.full_name is not None:
            target_user.full_name = payload.full_name.strip()
        if payload.role is not None:
            role = payload.role.strip().upper()
            if role in ["HOSPITAL_ADMIN", "HOSPITAL_OPERATOR", "HOSPITAL_ANALYST"]:
                target_user.role = role
        if payload.is_active is not None:
            target_user.is_active = payload.is_active

        db.commit()
        db.refresh(target_user)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_STAFF_UPDATED",
            resource_type="user",
            resource_id=target_user.id,
            result="SUCCESS",
            metadata={
                "hospital_id": hospital_id,
                "is_active": target_user.is_active,
                "role": target_user.role,
            },
        )
        return target_user

    # ========================================================================
    # PROFILE MANAGEMENT
    # ========================================================================

    @staticmethod
    def update_profile(
        db: Session,
        *,
        hospital_id: str,
        actor_user_id: str,
        payload: HospitalUpdate,
    ) -> Hospital:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found.",
            )

        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            if hasattr(hospital, key) and value is not None:
                setattr(hospital, key, value.strip() if isinstance(value, str) else value)

        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_PROFILE_UPDATED",
            resource_type="hospital",
            resource_id=hospital.id,
            result="SUCCESS",
            metadata=data,
        )
        return hospital

    # ========================================================================
    # SUBMITTED UPDATES
    # ========================================================================

    @staticmethod
    def get_updates(
        db: Session,
        hospital_id: str,
    ) -> list[dict]:
        updates = (
            db.query(ModelUpdate)
            .filter(ModelUpdate.hospital_id == hospital_id)
            .order_by(ModelUpdate.submitted_at.desc())
            .all()
        )
        result = []
        for u in updates:
            r = u.round
            result.append({
                "id": u.id,
                "round_id": u.round_id,
                "round_number": r.round_number if r else None,
                "num_examples": u.num_examples,
                "artifact_hash": u.artifact_hash,
                "artifact_type": u.artifact_type,
                "artifact_size": u.artifact_size,
                "l0_status": u.l0_status,
                "detection_status": u.detection_status,
                "trust_status": u.trust_status,
                "action": u.action,
                "submitted_at": u.submitted_at,
            })
        return result
