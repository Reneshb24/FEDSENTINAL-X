from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.services.audit import record_audit
from backend.storage.models import (
    Federation,
    FederationMembership,
    FederationRound,
    Hospital,
)


class RoundManagementService:
    """
    Persistent management of federation rounds.

    Configuration and persistence live here.
    Federated-learning execution remains inside FederationService.
    """

    @staticmethod
    def create_round(
        db: Session,
        federation: Federation,
        *,
        actor_user_id: str,
        configuration: dict,
    ) -> FederationRound:

        if federation.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Rounds can only be created for an ACTIVE federation.",
            )

        requested_clients = configuration["num_clients"]

        memberships = (
            db.query(FederationMembership)
            .join(
                Hospital,
                Hospital.id == FederationMembership.hospital_id,
            )
            .filter(
                FederationMembership.federation_id == federation.id,
                FederationMembership.status == "ACTIVE",
                Hospital.status == "ACTIVE",
                Hospital.is_eligible.is_(True),
            )
            .all()
        )

        if len(memberships) < requested_clients:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Federation has only {len(memberships)} eligible active "
                    f"hospital(s), but {requested_clients} were requested."
                ),
            )

        latest_round = (
            db.query(FederationRound)
            .filter(
                FederationRound.federation_id == federation.id
            )
            .order_by(
                FederationRound.round_number.desc()
            )
            .first()
        )

        next_round_number = (
            1
            if latest_round is None
            else latest_round.round_number + 1
        )

        federation_round = FederationRound(
            federation_id=federation.id,
            round_number=next_round_number,
            status="CREATED",
            participating_clients=requested_clients,
            config_json=json.dumps(
                configuration,
                sort_keys=True,
            ),
        )

        db.add(federation_round)
        db.commit()
        db.refresh(federation_round)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="ROUND_CREATED",
            resource_type="FEDERATION_ROUND",
            resource_id=federation_round.id,
            reason="Federation round configured.",
            metadata={
                "federation_id": federation.id,
                "round_number": next_round_number,
                "participating_clients": requested_clients,
                "configuration": configuration,
            },
        )

        return federation_round

    @staticmethod
    def mark_started(
        db: Session,
        federation_round: FederationRound,
        *,
        actor_user_id: str,
    ) -> FederationRound:

        if federation_round.status != "CREATED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Round '{federation_round.id}' cannot start "
                    f"from status '{federation_round.status}'."
                ),
            )

        federation_round.status = "RUNNING"
        federation_round.started_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(federation_round)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="ROUND_STARTED",
            resource_type="FEDERATION_ROUND",
            resource_id=federation_round.id,
            reason="Federated-learning round execution started.",
            metadata={
                "federation_id": federation_round.federation_id,
                "round_number": federation_round.round_number,
            },
        )

        return federation_round

    @staticmethod
    def mark_completed(
        db: Session,
        federation_round: FederationRound,
        *,
        actor_user_id: str,
        accepted_updates: int,
        quarantined_updates: int,
        global_model_version: str,
    ) -> FederationRound:

        federation_round.status = "COMPLETED"
        federation_round.completed_at = datetime.now(timezone.utc)
        federation_round.accepted_updates = accepted_updates
        federation_round.quarantined_updates = quarantined_updates
        federation_round.global_model_version = global_model_version

        db.commit()
        db.refresh(federation_round)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="ROUND_COMPLETED",
            resource_type="FEDERATION_ROUND",
            resource_id=federation_round.id,
            reason="Federated-learning round completed successfully.",
            metadata={
                "federation_id": federation_round.federation_id,
                "round_number": federation_round.round_number,
                "participating_clients": federation_round.participating_clients,
                "accepted_updates": accepted_updates,
                "quarantined_updates": quarantined_updates,
                "global_model_version": global_model_version,
            },
        )

        return federation_round

    @staticmethod
    def reset_failed_round(
        db: Session,
        federation_round: FederationRound,
        *,
        actor_user_id: str,
        reason: str,
    ) -> FederationRound:

        if federation_round.status not in {"RUNNING", "FAILED"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Round '{federation_round.id}' cannot be reset "
                    f"from status '{federation_round.status}'."
                ),
            )

        federation_round.status = "CREATED"
        federation_round.started_at = None
        federation_round.completed_at = None
        federation_round.accepted_updates = 0
        federation_round.quarantined_updates = 0
        federation_round.global_model_version = None

        db.commit()
        db.refresh(federation_round)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="ROUND_RESET",
            resource_type="FEDERATION_ROUND",
            resource_id=federation_round.id,
            reason=reason,
            metadata={
                "federation_id": federation_round.federation_id,
                "round_number": federation_round.round_number,
            },
        )

        return federation_round

    @staticmethod
    def mark_failed(
        db: Session,
        federation_round: FederationRound,
        *,
        actor_user_id: str,
        reason: str,
    ) -> FederationRound:

        federation_round.status = "FAILED"
        federation_round.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(federation_round)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="ROUND_FAILED",
            resource_type="FEDERATION_ROUND",
            resource_id=federation_round.id,
            reason=reason,
            result="FAILURE",
            metadata={
                "federation_id": federation_round.federation_id,
                "round_number": federation_round.round_number,
            },
        )

        return federation_round

    @staticmethod
    def mark_cancelled(
        db: Session,
        federation_round: FederationRound,
        *,
        actor_user_id: str,
        reason: str,
    ) -> FederationRound:

        if federation_round.status not in {"CREATED", "RUNNING"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Round '{federation_round.id}' cannot be cancelled "
                    f"from status '{federation_round.status}'."
                ),
            )

        federation_round.status = "CANCELLED"
        federation_round.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(federation_round)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="ROUND_CANCELLED",
            resource_type="FEDERATION_ROUND",
            resource_id=federation_round.id,
            reason=reason,
            result="CANCELLED",
            metadata={
                "federation_id": federation_round.federation_id,
                "round_number": federation_round.round_number,
            },
        )

        return federation_round
