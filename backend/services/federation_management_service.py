from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.services.audit import record_audit
from backend.storage.models import (
    Federation,
    FederationMembership,
    Hospital,
)


class FederationManagementService:

    @staticmethod
    def create_federation(
        db: Session,
        *,
        actor_user_id: str,
        name: str,
        description: str | None = None,
        dataset_name: str | None = None,
        model_name: str | None = None,
    ) -> Federation:

        federation = Federation(
            name=name,
            description=description,
            status="ACTIVE",
            dataset_name=dataset_name,
            model_name=model_name,
        )

        db.add(federation)
        db.commit()
        db.refresh(federation)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="FEDERATION_CREATED",
            resource_type="federation",
            resource_id=federation.id,
            reason="Federation created.",
            result="SUCCESS",
        )

        return federation

    @staticmethod
    def update_federation(
        db: Session,
        federation: Federation,
        *,
        actor_user_id: str,
        name: str | None = None,
        description: str | None = None,
        dataset_name: str | None = None,
        model_name: str | None = None,
        federation_status: str | None = None,
    ) -> Federation:

        if name is not None:
            federation.name = name

        if description is not None:
            federation.description = description

        if dataset_name is not None:
            federation.dataset_name = dataset_name

        if model_name is not None:
            federation.model_name = model_name

        if federation_status is not None:
            federation.status = federation_status

        db.commit()
        db.refresh(federation)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="FEDERATION_UPDATED",
            resource_type="federation",
            resource_id=federation.id,
            reason="Federation updated.",
            result="SUCCESS",
        )

        return federation

    @staticmethod
    def add_hospital(
        db: Session,
        federation: Federation,
        hospital: Hospital,
        *,
        actor_user_id: str,
        reason: str | None = None,
    ) -> FederationMembership:

        if federation.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Federation is not active.",
            )

        if hospital.status != "ACTIVE" or not hospital.is_eligible:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hospital must be active and eligible.",
            )

        existing = (
            db.query(FederationMembership)
            .filter(
                FederationMembership.federation_id == federation.id,
                FederationMembership.hospital_id == hospital.id,
            )
            .first()
        )

        if existing:
            if existing.status == "ACTIVE":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Hospital is already an active federation member.",
                )

            existing.status = "ACTIVE"
            existing.joined_at = datetime.now(timezone.utc)
            existing.left_at = None
            existing.leave_reason = None

            db.commit()
            db.refresh(existing)

            record_audit(
                db,
                actor_user_id=actor_user_id,
                action="FEDERATION_MEMBERSHIP_RESTORED",
                resource_type="federation_membership",
                resource_id=existing.id,
                reason=reason or "Hospital membership restored.",
                result="SUCCESS",
            )

            return existing

        membership = FederationMembership(
            federation_id=federation.id,
            hospital_id=hospital.id,
            status="ACTIVE",
            joined_at=datetime.now(timezone.utc),
        )

        db.add(membership)
        db.commit()
        db.refresh(membership)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="FEDERATION_MEMBER_ADDED",
            resource_type="federation_membership",
            resource_id=membership.id,
            reason=reason or "Hospital added to federation.",
            result="SUCCESS",
        )

        return membership

    @staticmethod
    def remove_hospital(
        db: Session,
        membership: FederationMembership,
        *,
        actor_user_id: str,
        reason: str | None = None,
    ) -> FederationMembership:

        if membership.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hospital is not an active federation member.",
            )

        membership.status = "LEFT"
        membership.left_at = datetime.now(timezone.utc)
        membership.leave_reason = reason

        db.commit()
        db.refresh(membership)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="FEDERATION_MEMBER_REMOVED",
            resource_type="federation_membership",
            resource_id=membership.id,
            reason=reason or "Hospital left federation.",
            result="SUCCESS",
        )

        return membership
