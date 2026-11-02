"""
Hospital lifecycle and registration services for FedSentinel.
"""

from __future__ import annotations

from datetime import datetime
from datetime import timezone

from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from backend.auth.roles import Role
from backend.auth.security import hash_password
from backend.schemas.hospital import HospitalRegistrationRequest
from backend.services.audit import record_audit
from backend.storage.models import AdminAction
from backend.storage.models import Hospital
from backend.storage.models import User


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HospitalService:

    # ========================================================================
    # REGISTER HOSPITAL
    # ========================================================================

    @staticmethod
    def register_hospital(
        db: Session,
        payload: HospitalRegistrationRequest,
    ) -> Hospital:
        """
        Public hospital registration.

        Registration creates:
            - a PENDING hospital
            - a HOSPITAL_ADMIN user

        The hospital is NOT federation eligible until an administrator
        explicitly approves it.
        """

        code = payload.code.strip().upper()
        admin_email = payload.admin_email.strip().lower()

        # --------------------------------------------------------------------
        # Validate hospital code
        # --------------------------------------------------------------------

        existing_hospital = (
            db.query(Hospital)
            .filter(Hospital.code == code)
            .first()
        )

        if existing_hospital is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hospital code already exists.",
            )

        # --------------------------------------------------------------------
        # Validate administrator email
        # --------------------------------------------------------------------

        existing_user = (
            db.query(User)
            .filter(User.email == admin_email)
            .first()
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Administrator email already exists.",
            )

        # --------------------------------------------------------------------
        # Create hospital (Application submitted, pending admin review)
        # --------------------------------------------------------------------

        hospital = Hospital(
            code=code,
            name=payload.name.strip(),
            status="PENDING",
            application_status="SUBMITTED",
            security_status="TRUSTED",
            is_eligible=False,
            is_simulation=False,
            contact_email=payload.contact_email.strip().lower(),
            contact_phone=payload.contact_phone,
            address=getattr(payload, "address", None),
            location=payload.location or getattr(payload, "address", None),
            country=getattr(payload, "country", None),
            region=getattr(payload, "region", None),
            website=getattr(payload, "website", None),
            institution_type=getattr(payload, "institution_type", "CLINICAL_CENTER") or "CLINICAL_CENTER",
            description=payload.description,
        )

        db.add(hospital)

        # Generate hospital ID before creating the user.
        db.flush()

        # --------------------------------------------------------------------
        # Create hospital administrator (Account ready for application tracking)
        # --------------------------------------------------------------------

        admin_name = getattr(payload, "admin_name", None) or f"{hospital.name} Administrator"
        hospital_admin = User(
            email=admin_email,
            password_hash=hash_password(
                payload.admin_password
            ),
            role=Role.HOSPITAL_ADMIN.value,
            hospital_id=hospital.id,
            is_active=True,
            failed_login_attempts=0,
            locked_until=None,
            last_login_at=None,
            full_name=admin_name,
        )

        db.add(hospital_admin)
        db.commit()
        db.refresh(hospital)

        # --------------------------------------------------------------------
        # Audit
        # --------------------------------------------------------------------

        record_audit(
            db,
            actor_user_id=hospital_admin.id,
            action="HOSPITAL_REGISTERED",
            resource_type="hospital",
            resource_id=hospital.id,
            reason="Hospital self-registration",
            result="SUCCESS",
            metadata={
                "hospital_code": hospital.code,
                "hospital_name": hospital.name,
                "admin_user_id": hospital_admin.id,
                "status": hospital.status,
                "is_eligible": hospital.is_eligible,
            },
        )

        return hospital

    # ========================================================================
    # CREATE
    # ========================================================================

    @staticmethod
    def create_hospital(
        db: Session,
        *,
        actor_user_id: str,
        code: str,
        name: str,
        contact_email: str | None = None,
        contact_phone: str | None = None,
        location: str | None = None,
        description: str | None = None,
    ) -> Hospital:

        code = code.strip().upper()

        existing = (
            db.query(Hospital)
            .filter(Hospital.code == code)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hospital code already exists.",
            )

        hospital = Hospital(
            code=code,
            name=name.strip(),
            status="PENDING",
            security_status="TRUSTED",
            is_eligible=False,
            contact_email=(
                contact_email.strip().lower()
                if contact_email
                else None
            ),
            contact_phone=contact_phone,
            location=location,
            description=description,
        )

        db.add(hospital)
        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_CREATED",
            resource_type="hospital",
            resource_id=hospital.id,
            result="SUCCESS",
            metadata={
                "code": hospital.code,
                "name": hospital.name,
            },
        )

        return hospital

    # ========================================================================
    # UPDATE
    # ========================================================================

    @staticmethod
    def create_hospital_admin(
        db: Session,
        *,
        actor_user_id: str,
        hospital: Hospital,
        email: str,
        password: str,
    ) -> User:

        if hospital.status == "REVOKED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Revoked hospitals cannot receive administrators.",
            )

        admin_email = email.strip().lower()

        existing_user = (
            db.query(User)
            .filter(User.email == admin_email)
            .first()
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User email already exists.",
            )

        existing_admin = (
            db.query(User)
            .filter(
                User.hospital_id == hospital.id,
                User.role == Role.HOSPITAL_ADMIN.value,
                User.is_active.is_(True),
            )
            .first()
        )

        if existing_admin is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hospital already has an active administrator.",
            )

        hospital_admin = User(
            email=admin_email,
            password_hash=hash_password(password),
            role=Role.HOSPITAL_ADMIN.value,
            hospital_id=hospital.id,
            is_active=True,
            failed_login_attempts=0,
            locked_until=None,
            last_login_at=None,
        )

        db.add(hospital_admin)
        db.commit()
        db.refresh(hospital_admin)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_ADMIN_CREATED",
            resource_type="hospital_user",
            resource_id=hospital_admin.id,
            reason="Administrator account created for hospital",
            result="SUCCESS",
            metadata={
                "hospital_id": hospital.id,
                "hospital_code": hospital.code,
                "admin_user_id": hospital_admin.id,
                "admin_email": hospital_admin.email,
            },
        )

        return hospital_admin


    @staticmethod
    def update_hospital(
        db: Session,
        *,
        actor_user_id: str,
        hospital: Hospital,
        name: str | None = None,
        contact_email: str | None = None,
        contact_phone: str | None = None,
        location: str | None = None,
        description: str | None = None,
        security_status: str | None = None,
        security_tier: str | None = None,
    ) -> Hospital:

        if hospital.status == "REVOKED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Revoked hospitals cannot be edited.",
            )

        if name is not None:
            hospital.name = name.strip()

        if contact_email is not None:
            hospital.contact_email = contact_email.strip().lower()

        if contact_phone is not None:
            hospital.contact_phone = contact_phone

        if location is not None:
            hospital.location = location

        if description is not None:
            hospital.description = description

        tier = security_status or security_tier
        if tier is not None:
            clean_tier = tier.strip().upper()
            valid_tiers = {"TRUSTED", "PROBATION", "HIGH_RISK", "QUARANTINED", "SUSPENDED"}
            if clean_tier not in valid_tiers:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid security tier '{clean_tier}'. Allowed tiers: {sorted(valid_tiers)}",
                )
            hospital.security_status = clean_tier
            if clean_tier in {"SUSPENDED", "QUARANTINED"}:
                hospital.is_eligible = False
            else:
                hospital.is_eligible = True

        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_UPDATED",
            resource_type="hospital",
            resource_id=hospital.id,
            result="SUCCESS",
        )

        return hospital

    # ========================================================================
    # APPROVE
    # ========================================================================

    @staticmethod
    def approve(
        db: Session,
        *,
        actor_user_id: str,
        hospital: Hospital,
        reason: str | None = None,
    ) -> Hospital:

        previous = hospital.status

        if previous != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Hospital cannot be approved from "
                    f"{previous}."
                ),
            )

        hospital.status = "ACTIVE"
        hospital.is_eligible = True

        db.add(
            AdminAction(
                actor_user_id=actor_user_id,
                hospital_id=hospital.id,
                action="APPROVE_HOSPITAL",
                previous_status=previous,
                new_status=hospital.status,
                reason=reason,
                result="SUCCESS",
            )
        )

        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_APPROVED",
            resource_type="hospital",
            resource_id=hospital.id,
            reason=reason,
            result="SUCCESS",
        )

        return hospital

    # ========================================================================
    # SUSPEND
    # ========================================================================

    @staticmethod
    def suspend(
        db: Session,
        *,
        actor_user_id: str,
        hospital: Hospital,
        reason: str | None = None,
    ) -> Hospital:

        previous = hospital.status

        if previous not in {"ACTIVE", "DEGRADED"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Hospital cannot be suspended from "
                    f"{previous}."
                ),
            )

        hospital.status = "SUSPENDED"
        hospital.is_eligible = False

        db.add(
            AdminAction(
                actor_user_id=actor_user_id,
                hospital_id=hospital.id,
                action="SUSPEND_HOSPITAL",
                previous_status=previous,
                new_status=hospital.status,
                reason=reason,
                result="SUCCESS",
            )
        )

        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_SUSPENDED",
            resource_type="hospital",
            resource_id=hospital.id,
            reason=reason,
            result="SUCCESS",
        )

        return hospital

    # ========================================================================
    # RESTORE
    # ========================================================================

    @staticmethod
    def restore(
        db: Session,
        hospital: Hospital,
        *,
        actor_user_id: str,
        reason: str | None = None,
    ) -> Hospital:

        if hospital.status != "SUSPENDED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Hospital cannot be restored from "
                    f"{hospital.status}."
                ),
            )

        previous_status = hospital.status

        hospital.status = "ACTIVE"
        hospital.is_eligible = True
        hospital.security_status = "TRUSTED"
        hospital.updated_at = utc_now()

        db.add(
            AdminAction(
                actor_user_id=actor_user_id,
                hospital_id=hospital.id,
                action="RESTORE",
                previous_status=previous_status,
                new_status=hospital.status,
                reason=reason,
                result="SUCCESS",
            )
        )

        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_RESTORED",
            resource_type="hospital",
            resource_id=hospital.id,
            reason=reason,
            result="SUCCESS",
        )

        return hospital

    # ========================================================================
    # QUARANTINE
    # ========================================================================

    @staticmethod
    def quarantine(
        db: Session,
        *,
        actor_user_id: str,
        hospital: Hospital,
        reason: str | None = None,
    ) -> Hospital:

        if hospital.status == "REVOKED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Revoked hospitals cannot be quarantined."
                ),
            )

        previous = hospital.status

        hospital.status = "QUARANTINED"
        hospital.security_status = "QUARANTINED"
        hospital.is_eligible = False

        db.add(
            AdminAction(
                actor_user_id=actor_user_id,
                hospital_id=hospital.id,
                action="QUARANTINE_HOSPITAL",
                previous_status=previous,
                new_status=hospital.status,
                reason=reason,
                result="SUCCESS",
            )
        )

        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_QUARANTINED",
            resource_type="hospital",
            resource_id=hospital.id,
            reason=reason,
            result="SUCCESS",
        )

        return hospital

    # ========================================================================
    # RELEASE QUARANTINE
    # ========================================================================

    @staticmethod
    def release(
        db: Session,
        *,
        actor_user_id: str,
        hospital: Hospital,
        reason: str | None = None,
    ) -> Hospital:

        if hospital.status != "QUARANTINED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hospital is not quarantined.",
            )

        hospital.status = "ACTIVE"
        hospital.security_status = "TRUSTED"
        hospital.is_eligible = True

        db.add(
            AdminAction(
                actor_user_id=actor_user_id,
                hospital_id=hospital.id,
                action="RELEASE_HOSPITAL",
                previous_status="QUARANTINED",
                new_status="ACTIVE",
                reason=reason,
                result="SUCCESS",
            )
        )

        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_RELEASED",
            resource_type="hospital",
            resource_id=hospital.id,
            reason=reason,
            result="SUCCESS",
        )

        return hospital

    # ========================================================================
    # REMOVE FROM FEDERATION
    # ========================================================================

    @staticmethod
    def remove(
        db: Session,
        *,
        actor_user_id: str,
        hospital: Hospital,
        reason: str | None = None,
    ) -> Hospital:

        if hospital.status == "REVOKED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hospital is already revoked.",
            )

        previous = hospital.status

        hospital.status = "INACTIVE"
        hospital.is_eligible = False
        hospital.removed_at = utc_now()
        hospital.removal_reason = reason

        db.add(
            AdminAction(
                actor_user_id=actor_user_id,
                hospital_id=hospital.id,
                action="REMOVE_HOSPITAL",
                previous_status=previous,
                new_status="INACTIVE",
                reason=reason,
                result="SUCCESS",
            )
        )

        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_REMOVED",
            resource_type="hospital",
            resource_id=hospital.id,
            reason=reason,
            result="SUCCESS",
        )

        return hospital

    # ========================================================================
    # REVOKE
    # ========================================================================

    @staticmethod
    def revoke(
        db: Session,
        *,
        actor_user_id: str,
        hospital: Hospital,
        reason: str | None = None,
    ) -> Hospital:

        previous = hospital.status

        if previous == "REVOKED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hospital is already revoked.",
            )

        hospital.status = "REVOKED"
        hospital.is_eligible = False
        hospital.security_status = "REVOKED"

        db.add(
            AdminAction(
                actor_user_id=actor_user_id,
                hospital_id=hospital.id,
                action="REVOKE_HOSPITAL",
                previous_status=previous,
                new_status="REVOKED",
                reason=reason,
                result="SUCCESS",
            )
        )

        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_REVOKED",
            resource_type="hospital",
            resource_id=hospital.id,
            reason=reason,
            result="SUCCESS",
        )

        return hospital
    # ========================================================================
    # INSTITUTIONAL APPLICATION QUEUE & REVIEW
    # ========================================================================

    @staticmethod
    def list_applications(
        db: Session,
        status_filter: str | None = None,
    ) -> list[Hospital]:
        """
        List all hospital applications awaiting review, under review, or rejected.
        Excludes simulated nodes.
        """
        query = db.query(Hospital).filter(Hospital.is_simulation.is_(False))
        if status_filter:
            query = query.filter(Hospital.application_status == status_filter.upper())
        else:
            query = query.filter(
                (Hospital.application_status.in_(["SUBMITTED", "UNDER_REVIEW", "REJECTED"])) |
                (Hospital.status == "PENDING")
            )
        return query.order_by(Hospital.created_at.desc()).all()

    @staticmethod
    def review_application(
        db: Session,
        *,
        actor_user_id: str,
        hospital: Hospital,
        notes: str | None = None,
    ) -> Hospital:
        """
        Move a submitted hospital application to UNDER_REVIEW.
        """
        previous = hospital.application_status
        hospital.application_status = "UNDER_REVIEW"
        hospital.updated_at = utc_now()

        db.add(
            AdminAction(
                actor_user_id=actor_user_id,
                hospital_id=hospital.id,
                action="REVIEW_HOSPITAL_APPLICATION",
                previous_status=previous,
                new_status="UNDER_REVIEW",
                reason=notes,
                result="SUCCESS",
            )
        )
        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_APPLICATION_UNDER_REVIEW",
            resource_type="hospital_application",
            resource_id=hospital.id,
            reason=notes,
            result="SUCCESS",
        )
        return hospital

    @staticmethod
    def approve_application(
        db: Session,
        *,
        actor_user_id: str,
        hospital: Hospital,
        federation_id: str | None = None,
        notes: str | None = None,
    ) -> Hospital:
        """
        Approve an institutional application:
        - Marks application_status = 'APPROVED'
        - Sets hospital status = 'ACTIVE' and is_eligible = True
        - Automatically enrolls in the target federation membership
        """
        from backend.storage.models import Federation, FederationMembership

        previous = hospital.status
        hospital.status = "ACTIVE"
        hospital.application_status = "APPROVED"
        hospital.is_eligible = True
        hospital.security_status = "TRUSTED"
        hospital.rejection_reason = None
        hospital.updated_at = utc_now()

        # Assign federation membership
        target_fed_id = federation_id
        if not target_fed_id:
            fed = db.query(Federation).first()
            if fed:
                target_fed_id = fed.id

        if target_fed_id:
            existing_mem = (
                db.query(FederationMembership)
                .filter(
                    FederationMembership.federation_id == target_fed_id,
                    FederationMembership.hospital_id == hospital.id,
                )
                .first()
            )
            if existing_mem:
                existing_mem.status = "ACTIVE"
            else:
                new_mem = FederationMembership(
                    federation_id=target_fed_id,
                    hospital_id=hospital.id,
                    status="ACTIVE",
                    joined_at=utc_now(),
                )
                db.add(new_mem)

        db.add(
            AdminAction(
                actor_user_id=actor_user_id,
                hospital_id=hospital.id,
                action="APPROVE_HOSPITAL_APPLICATION",
                previous_status=previous,
                new_status="ACTIVE",
                reason=notes or "Application approved by global administrator",
                result="SUCCESS",
            )
        )
        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_APPLICATION_APPROVED",
            resource_type="hospital_application",
            resource_id=hospital.id,
            reason=notes,
            result="SUCCESS",
            metadata={
                "federation_id": target_fed_id,
                "hospital_code": hospital.code,
            },
        )
        return hospital

    @staticmethod
    def reject_application(
        db: Session,
        *,
        actor_user_id: str,
        hospital: Hospital,
        rejection_reason: str,
    ) -> Hospital:
        """
        Reject an institutional application with a mandatory reason:
        - Marks application_status = 'REJECTED'
        - Sets hospital status = 'REJECTED' and is_eligible = False
        - Deactivates any federation membership
        """
        from backend.storage.models import FederationMembership

        if not rejection_reason or len(rejection_reason.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A valid mandatory rejection reason must be supplied.",
            )

        previous = hospital.status
        hospital.status = "REJECTED"
        hospital.application_status = "REJECTED"
        hospital.is_eligible = False
        hospital.rejection_reason = rejection_reason.strip()
        hospital.updated_at = utc_now()

        # Deactivate memberships if any
        mems = db.query(FederationMembership).filter(FederationMembership.hospital_id == hospital.id).all()
        for m in mems:
            m.status = "INACTIVE"

        db.add(
            AdminAction(
                actor_user_id=actor_user_id,
                hospital_id=hospital.id,
                action="REJECT_HOSPITAL_APPLICATION",
                previous_status=previous,
                new_status="REJECTED",
                reason=rejection_reason.strip(),
                result="SUCCESS",
            )
        )
        db.commit()
        db.refresh(hospital)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="HOSPITAL_APPLICATION_REJECTED",
            resource_type="hospital_application",
            resource_id=hospital.id,
            reason=rejection_reason.strip(),
            result="SUCCESS",
            metadata={
                "hospital_code": hospital.code,
                "rejection_reason": rejection_reason.strip(),
            },
        )
        return hospital
