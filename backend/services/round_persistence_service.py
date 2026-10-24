from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from backend.models.update import ModelUpdate as RuntimeModelUpdate
from backend.services.incident_manager import ManagedIncident
from backend.services.model_artifact_service import ModelArtifactService
from backend.services.security_pipeline import SecurityRoundResult
from backend.storage.models import (
    Federation,
    FederationRound,
    Hospital,
    Incident,
    Model,
    ModelUpdate,
    ModelVersion,
    TrustRecord,
    UpdateEvidence,
)


class RoundPersistenceService:
    """
    Persist the authoritative result of a completed security round.

    This service does NOT perform:
        - detection
        - attribution
        - trust evaluation
        - quarantine decisions
        - aggregation

    It only converts already-produced runtime results into durable
    database records and persists the secured global model artifact.
    """

    def __init__(self) -> None:
        self.model_artifact_service = ModelArtifactService()

    # ============================================================
    # Helpers
    # ============================================================

    @staticmethod
    def _enum_value(
        value: Any,
        default: str = "",
    ) -> str:
        if value is None:
            return default

        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )

    @staticmethod
    def _hospital_map(
        db: Session,
    ) -> dict[str, Hospital]:
        """
        Build a lookup supporting both:

            Runtime clients:
                H1, H2, ..., H20

            Persisted hospitals:
                H01, H02, ..., H20
        """

        hospitals = db.query(Hospital).all()

        hospital_map: dict[str, Hospital] = {}

        for hospital in hospitals:
            hospital_map[hospital.id] = hospital
            hospital_map[hospital.code] = hospital

            if hospital.code.startswith("H"):
                suffix = hospital.code[1:]

                if suffix.isdigit():
                    normalized_code = f"H{int(suffix)}"

                    hospital_map.setdefault(
                        normalized_code,
                        hospital,
                    )

        return hospital_map

    # ============================================================
    # Evidence persistence
    # ============================================================

    @staticmethod
    def _persist_evidence(
        db: Session,
        *,
        update_id: str,
        result: Any,
    ) -> None:
        """
        Persist only evidence actually produced by L0-L5
        and the Trust Engine.
        """

        evidence_rows: list[UpdateEvidence] = []

        # --------------------------------------------------------
        # L0 — Artifact Validation
        # --------------------------------------------------------

        evidence_rows.append(
            UpdateEvidence(
                update_id=update_id,
                layer="L0",
                signal="artifact_validation",
                score=None,
                explanation=(
                    "L0 artifact validation passed."
                    if result.layer0_passed
                    else "L0 artifact validation failed."
                ),
            )
        )

        evidence_rows.append(
            UpdateEvidence(
                update_id=update_id,
                layer="L0",
                signal="forensic_eligibility",
                score=(
                    1.0
                    if result.layer0_forensic_eligible
                    else 0.0
                ),
                explanation=(
                    "Update is eligible for forensic analysis."
                    if result.layer0_forensic_eligible
                    else "Update is not eligible for forensic analysis."
                ),
            )
        )

        # --------------------------------------------------------
        # L1 — Privacy-Safe Inspection
        # --------------------------------------------------------

        if result.fingerprint is not None:
            evidence_rows.append(
                UpdateEvidence(
                    update_id=update_id,
                    layer="L1",
                    signal="privacy_safe_fingerprint",
                    score=None,
                    explanation=(
                        "Privacy-safe update fingerprint generated."
                    ),
                )
            )

        # --------------------------------------------------------
        # L2 — Robust Anomaly Detection
        # --------------------------------------------------------

        layer2 = result.layer2

        if layer2 is not None:
            evidence_rows.extend(
                [
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L2",
                        signal="anomaly_score",
                        score=float(
                            layer2.anomaly_score
                        ),
                        explanation=(
                            f"L2 anomaly score: "
                            f"{layer2.anomaly_score:.2f}"
                        ),
                    ),
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L2",
                        signal="z_score",
                        score=float(
                            layer2.z_score
                        ),
                        explanation=(
                            f"L2 robust z-score: "
                            f"{layer2.z_score:.4f}"
                        ),
                    ),
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L2",
                        signal="peer_similarity",
                        score=float(
                            layer2.peer_similarity
                        ),
                        explanation=(
                            f"L2 peer similarity: "
                            f"{layer2.peer_similarity:.4f}"
                        ),
                    ),
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L2",
                        signal="outlier",
                        score=(
                            1.0
                            if layer2.is_outlier
                            else 0.0
                        ),
                        explanation=(
                            "L2 update classified as an outlier."
                            if layer2.is_outlier
                            else (
                                "L2 update remained within "
                                "the peer baseline."
                            )
                        ),
                    ),
                ]
            )

        # --------------------------------------------------------
        # L3 — Influence Analysis
        # --------------------------------------------------------

        layer3 = result.layer3

        if layer3 is not None:
            evidence_rows.extend(
                [
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L3",
                        signal="influence_score",
                        score=float(
                            layer3.influence_score
                        ),
                        explanation=(
                            f"L3 influence score: "
                            f"{layer3.influence_score:+.4f}"
                        ),
                    ),
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L3",
                        signal="validation_delta",
                        score=float(
                            layer3.validation_delta
                        ),
                        explanation=(
                            f"L3 validation delta: "
                            f"{layer3.validation_delta:+.6f}"
                        ),
                    ),
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L3",
                        signal="harmful_influence",
                        score=(
                            1.0
                            if layer3.harmful_influence
                            else 0.0
                        ),
                        explanation=(
                            "L3 reports harmful influence."
                            if layer3.harmful_influence
                            else (
                                "L3 does not report "
                                "harmful influence."
                            )
                        ),
                    ),
                ]
            )

        # --------------------------------------------------------
        # L4 — Counterfactual Simulation
        # --------------------------------------------------------

        layer4 = result.layer4

        if layer4 is not None:
            evidence_rows.extend(
                [
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L4",
                        signal="accuracy_delta",
                        score=float(
                            layer4.accuracy_delta
                        ),
                        explanation=(
                            f"L4 counterfactual accuracy delta: "
                            f"{layer4.accuracy_delta:+.6f}"
                        ),
                    ),
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L4",
                        signal="loss_delta",
                        score=float(
                            layer4.loss_delta
                        ),
                        explanation=(
                            f"L4 counterfactual loss delta: "
                            f"{layer4.loss_delta:+.6f}"
                        ),
                    ),
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L4",
                        signal="harmful_counterfactual",
                        score=(
                            1.0
                            if layer4.harmful_counterfactual
                            else 0.0
                        ),
                        explanation=(
                            "L4 reports harmful "
                            "counterfactual impact."
                            if layer4.harmful_counterfactual
                            else (
                                "L4 does not report harmful "
                                "counterfactual impact."
                            )
                        ),
                    ),
                ]
            )

        # --------------------------------------------------------
        # L5 — Attribution
        # --------------------------------------------------------

        layer5 = result.layer5

        if layer5 is not None:
            evidence_rows.extend(
                [
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L5",
                        signal="attribution_score",
                        score=float(
                            layer5.evidence_score
                        ),
                        explanation=(
                            f"L5 attribution evidence score: "
                            f"{layer5.evidence_score:.2f}"
                        ),
                    ),
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L5",
                        signal="hypothesis",
                        score=None,
                        explanation=(
                            "L5 hypothesis: "
                            f"{RoundPersistenceService._enum_value(
                                layer5.hypothesis
                            )}"
                        ),
                    ),
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L5",
                        signal="confidence",
                        score=float(
                            layer5.confidence
                        ),
                        explanation=(
                            f"L5 attribution confidence: "
                            f"{layer5.confidence:.4f}"
                        ),
                    ),
                ]
            )

            for explanation in layer5.supporting_evidence:
                evidence_rows.append(
                    UpdateEvidence(
                        update_id=update_id,
                        layer="L5",
                        signal="supporting_evidence",
                        score=None,
                        explanation=str(
                            explanation
                        ),
                    )
                )

        # --------------------------------------------------------
        # Trust Engine
        # --------------------------------------------------------

        trust = result.trust

        if trust is not None:
            evidence_rows.extend(
                [
                    UpdateEvidence(
                        update_id=update_id,
                        layer="TRUST",
                        signal="risk_score",
                        score=float(
                            trust.risk_score
                        ),
                        explanation=(
                            f"Trust risk score: "
                            f"{trust.risk_score:.2f}"
                        ),
                    ),
                    UpdateEvidence(
                        update_id=update_id,
                        layer="TRUST",
                        signal="confidence",
                        score=float(
                            trust.confidence
                        ),
                        explanation=(
                            f"Trust confidence: "
                            f"{trust.confidence:.4f}"
                        ),
                    ),
                    UpdateEvidence(
                        update_id=update_id,
                        layer="TRUST",
                        signal="decision",
                        score=None,
                        explanation=(
                            "Trust decision: "
                            f"{RoundPersistenceService._enum_value(
                                trust.action
                            )}"
                        ),
                    ),
                    UpdateEvidence(
                        update_id=update_id,
                        layer="TRUST",
                        signal="reason",
                        score=None,
                        explanation=str(
                            trust.reason
                        ),
                    ),
                ]
            )

        if evidence_rows:
            db.add_all(evidence_rows)

    # ============================================================
    # Main persistence operation
    # ============================================================

    def persist_round(
        self,
        db: Session,
        *,
        federation: Federation,
        federation_round: FederationRound,
        result: SecurityRoundResult,
        incidents: list[ManagedIncident],
    ) -> None:
        """
        Persist one completed security round.

        Persistence includes:

            1. Model updates
            2. L0-L5 evidence
            3. Trust records
            4. Incidents
            5. Secured global model artifact
            6. ModelVersion lineage

        The security pipeline itself has already completed before
        this method is called.
        """

        # --------------------------------------------------------
        # Round-level idempotency
        # --------------------------------------------------------

        hospital_map = self._hospital_map(db)

        accepted_ids = {
            update.update_id
            for update in result.accepted_updates
        }

        quarantined_ids = {
            update.update_id
            for update in result.quarantined_updates
        }

        all_runtime_updates = (
            result.accepted_updates
            + result.quarantined_updates
        )

        # ========================================================
        # Model Updates + Evidence + Trust
        # ========================================================

        for (
            client_id,
            client_result,
        ) in result.client_results.items():

            hospital = hospital_map.get(client_id)

            if hospital is None:
                raise ValueError(
                    f"No hospital exists for client "
                    f"'{client_id}'."
                )

            runtime_update = next(
                (
                    update
                    for update in all_runtime_updates
                    if update.update_id
                    == client_result.update_id
                ),
                None,
            )

            if runtime_update is None:
                raise ValueError(
                    f"Runtime update "
                    f"'{client_result.update_id}' "
                    f"was not found in the round result."
                )

            # ----------------------------------------------------
            # Detection status
            # ----------------------------------------------------

            if (
                client_result.update_id
                in quarantined_ids
            ):
                detection_status = "QUARANTINED"

            elif (
                client_result.update_id
                in accepted_ids
            ):
                detection_status = "ACCEPTED"

            else:
                detection_status = "REVIEW"

            # ----------------------------------------------------
            # L0 status
            # ----------------------------------------------------

            l0_status = (
                "PASSED"
                if client_result.layer0_passed
                else "FAILED"
            )

            # ----------------------------------------------------
            # Trust status
            # ----------------------------------------------------

            trust = client_result.trust

            trust_status = (
                self._enum_value(
                    trust.status,
                    "REVIEW",
                )
                if trust is not None
                else "REVIEW"
            )

            action = (
                self._enum_value(
                    trust.action,
                    "REVIEW",
                )
                if trust is not None
                else "REVIEW"
            )

            # ----------------------------------------------------
            # Durable update record
            # ----------------------------------------------------

            persisted_update = (
                db.query(ModelUpdate)
                .filter(
                    ModelUpdate.id
                    == client_result.update_id,
                    ModelUpdate.round_id
                    == federation_round.id,
                )
                .first()
            )

            if persisted_update is None:
                persisted_update = ModelUpdate(
                    id=client_result.update_id,
                    round_id=federation_round.id,
                    hospital_id=hospital.id,
                    num_examples=runtime_update.num_examples,
                    artifact_hash=None,
                    artifact_type=None,
                    artifact_size=None,
                    l0_status=l0_status,
                    detection_status=detection_status,
                    trust_status=trust_status,
                    action=action,
                    submitted_at=runtime_update.created_at,
                )

                db.add(persisted_update)

            else:
                # The hospital submission already created this row.
                # Preserve its artifact provenance and update only
                # the security-analysis state.
                persisted_update.num_examples = (
                    runtime_update.num_examples
                )
                persisted_update.l0_status = l0_status
                persisted_update.detection_status = (
                    detection_status
                )
                persisted_update.trust_status = trust_status
                persisted_update.action = action

                if persisted_update.submitted_at is None:
                    persisted_update.submitted_at = (
                        runtime_update.created_at
                    )

            db.flush()

            # ----------------------------------------------------
            # Security evidence
            # ----------------------------------------------------

            self._persist_evidence(
                db,
                update_id=persisted_update.id,
                result=client_result,
            )

            # ----------------------------------------------------
            # Trust record
            # ----------------------------------------------------

            if trust is not None:
                existing_trust = (
                    db.query(TrustRecord)
                    .filter(
                        TrustRecord.hospital_id
                        == hospital.id,
                        TrustRecord.round_id
                        == federation_round.id,
                    )
                    .first()
                )

                if existing_trust is None:
                    db.add(
                        TrustRecord(
                            hospital_id=hospital.id,
                            round_id=federation_round.id,
                            score=float(
                                trust.risk_score
                            ),
                            status=trust_status,
                            reason=trust.reason,
                        )
                    )
                else:
                    existing_trust.score = float(
                        trust.risk_score
                    )
                    existing_trust.status = trust_status
                    existing_trust.reason = trust.reason

        db.flush()

        # ========================================================
        # Incidents
        # ========================================================

        for incident in incidents:

            client_id = incident.primary_client_id

            hospital = (
                hospital_map.get(client_id)
                if client_id is not None
                else None
            )

            if (
                hospital is None
                and client_id is not None
            ):
                raise ValueError(
                    f"No hospital exists for incident "
                    f"client '{client_id}'."
                )

            existing_incident = (
                db.query(Incident)
                .filter(
                    Incident.incident_code
                    == incident.incident_id
                )
                .first()
            )

            if existing_incident is not None:
                continue

            evidence_payload = {
                "update_ids": [
                    client_result.update_id
                    for client_result
                    in result.client_results.values()
                    if client_result.client_id
                    == client_id
                ],
                "client_ids": incident.affected_clients,
                "round_ids": [incident.round_id],
                "evidence_items": incident.evidence,
            }

            db.add(
                Incident(
                    incident_code=incident.incident_id,
                    hospital_id=(
                        hospital.id
                        if hospital is not None
                        else None
                    ),
                    round_id=federation_round.id,
                    severity=self._enum_value(
                        incident.severity,
                        "INFO",
                    ),
                    threat_type=self._enum_value(
                        incident.hypothesis,
                        "NONE",
                    ),
                    status=incident.status,
                    title=incident.title,
                    description=incident.description,
                    recommended_action=self._enum_value(
                        incident.recommended_action,
                        "REVIEW",
                    ),
                    risk_score=float(
                        incident.risk_score
                    ),
                    confidence=float(
                        incident.confidence
                    ),
                    evidence_json=json.dumps(
                        evidence_payload,
                        sort_keys=True,
                    ),
                    assigned_to=None,
                    created_at=incident.created_at,
                    resolved_at=incident.resolved_at,
                    resolution_notes=incident.resolution,
                )
            )

        db.flush()

        # ========================================================
        # Model
        # ========================================================

        model = (
            db.query(Model)
            .filter(
                Model.name
                == federation.model_name
            )
            .first()
        )

        if model is None:
            model = Model(
                name=federation.model_name,
                architecture="FedSentinel CNN",
                framework="PyTorch",
                is_active=True,
            )

            db.add(model)
            db.flush()

        # ========================================================
        # Model Version / Lineage
        # ========================================================

        previous_version = (
            db.query(ModelVersion)
            .filter(
                ModelVersion.model_id
                == model.id
            )
            .order_by(
                ModelVersion.created_at.desc()
            )
            .first()
        )

        global_model_version = (
            f"round-{federation_round.round_number}"
        )

        # --------------------------------------------------------
        # Persist the actual secured global model artifact.
        #
        # ModelArtifactService:
        #
        #   - validates tensors
        #   - writes .safetensors
        #   - calculates the model hash
        #   - performs atomic file replacement
        #
        # The returned hash is therefore the hash of the
        # persisted model artifact.
        # --------------------------------------------------------

        (
            artifact_path,
            model_hash,
            artifact_size,
        ) = self.model_artifact_service.save(
            model_name=federation.model_name,
            version=global_model_version,
            state_dict=result.global_state,
        )

        # Keep the local variable intentionally available for
        # debugging/logging without changing the database schema.
        _ = artifact_path
        _ = artifact_size

        # --------------------------------------------------------
        # Persist model lineage
        # --------------------------------------------------------

        existing_model_version = (
            db.query(ModelVersion)
            .filter(
                ModelVersion.model_id == model.id,
                ModelVersion.round_id
                == federation_round.id,
            )
            .first()
        )

        if existing_model_version is None:
            db.add(
                ModelVersion(
                model_id=model.id,
                version=global_model_version,
                parent_version=(
                    previous_version.version
                    if previous_version is not None
                    else None
                ),
                round_id=federation_round.id,
                model_hash=model_hash,
                security_status=(
                    "QUARANTINED_UPDATES_FILTERED"
                    if result.quarantined_updates
                    else "VALIDATED"
                ),
                validation_accuracy=None,
                accepted_update_count=len(
                    result.accepted_updates
                ),
                quarantined_update_count=len(
                    result.quarantined_updates
                ),
            )
            )

        # ========================================================
        # Commit
        # ========================================================

        db.commit()


