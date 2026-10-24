from __future__ import annotations

from sqlalchemy.orm import Session

from backend.storage.models import (
    Dataset,
    FederationMembership,
    Incident,
    ModelUpdate,
    TrustRecord,
    Hospital,
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