"""
FedSentinel round orchestration coordinator.

RoundOrchestrator connects the existing:
    - RoundManager
    - SecurityPipeline
    - IncidentManager
    - EventManager

It does not implement security detection itself.

Its responsibility is to coordinate a complete round and produce
the operational events and incidents associated with that round.
"""

from __future__ import annotations

from typing import Any

from backend.core.types import (
    Action,
    EventType,
    RoundStatus,
    ThreatHypothesis,
)
from backend.models.model_utils import StateDict
from backend.models.update import ModelUpdate
from backend.services.event_manager import (
    EventManager,
    SecurityEventRecord,
)
from backend.services.incident_manager import (
    IncidentManager,
    ManagedIncident,
)
from backend.services.round_manager import (
    ManagedRound,
    RoundManager,
)
from backend.services.security_pipeline import (
    SecurityRoundResult,
)


class RoundOrchestrator:
    """
    Coordinate a complete FedSentinel round.

    Responsibilities:

        1. Create the round.
        2. Emit operational events.
        3. Execute RoundManager.
        4. Create incidents when required.
        5. Emit final security events.
        6. Return the SecurityRoundResult.

    Detection logic remains inside SecurityPipeline.
    """

    def __init__(
        self,
        *,
        round_manager: RoundManager | None = None,
        incident_manager: IncidentManager | None = None,
        event_manager: EventManager | None = None,
    ) -> None:

        self.round_manager = (
            round_manager
            if round_manager is not None
            else RoundManager()
        )

        self.incident_manager = (
            incident_manager
            if incident_manager is not None
            else IncidentManager()
        )

        self.event_manager = (
            event_manager
            if event_manager is not None
            else EventManager()
        )

    # ---------------------------------------------------------
    # Event helpers
    # ---------------------------------------------------------

    def _emit(
        self,
        *,
        event_id: str,
        event_type: EventType,
        message: str,
        round_id: str,
        client_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> SecurityEventRecord:

        return self.event_manager.emit(
            event_id=event_id,
            event_type=event_type,
            message=message,
            round_id=round_id,
            client_id=client_id,
            data=data,
        )

    # ---------------------------------------------------------
    # Round creation
    # ---------------------------------------------------------

    def create_round(
        self,
        *,
        round_id: str,
        target_clients: int,
    ) -> ManagedRound:
        """
        Create a round and emit ROUND_STARTED.

        The round itself remains in CREATED state until execution begins.
        """

        managed_round = self.round_manager.create_round(
            round_id=round_id,
            target_clients=target_clients,
        )

        self._emit(
            event_id=f"{round_id}-round-created",
            event_type=EventType.ROUND_STARTED,
            message=(
                f"Security round {round_id} created for "
                f"{target_clients} clients."
            ),
            round_id=round_id,
            data={
                "target_clients": target_clients,
                "status": RoundStatus.CREATED.value,
            },
        )

        return managed_round

    # ---------------------------------------------------------
    # Update events
    # ---------------------------------------------------------

    def _emit_update_events(
        self,
        *,
        round_id: str,
        updates: list[ModelUpdate],
    ) -> None:
        """
        Emit one CLIENT_UPDATE_RECEIVED event for each update.
        """

        for update in updates:
            self._emit(
                event_id=(
                    f"{round_id}-"
                    f"{update.client_id}-update-received"
                ),
                event_type=EventType.CLIENT_UPDATE_RECEIVED,
                message=(
                    f"Update received from client "
                    f"{update.client_id}."
                ),
                round_id=round_id,
                client_id=update.client_id,
                data={
                    "update_id": update.update_id,
                    "num_examples": update.num_examples,
                },
            )

    # ---------------------------------------------------------
    # Security result events
    # ---------------------------------------------------------

    def _emit_security_events(
        self,
        *,
        round_id: str,
        result: SecurityRoundResult,
    ) -> None:
        """
        Translate completed security evidence into operational events.

        No new security decision is created here.
        """

        for client_id, client_result in (
            result.client_results.items()
        ):
            # -------------------------------------------------
            # L0
            # -------------------------------------------------

            self._emit(
                event_id=f"{round_id}-{client_id}-integrity",
                event_type=EventType.INTEGRITY_CHECKED,
                message=(
                    f"Integrity validation completed for "
                    f"client {client_id}."
                ),
                round_id=round_id,
                client_id=client_id,
                data={
                    "passed": client_result.layer0_passed,
                    "forensic_eligible": (
                        client_result.layer0_forensic_eligible
                    ),
                },
            )

            # -------------------------------------------------
            # L1
            # -------------------------------------------------

            if client_result.fingerprint is not None:
                self._emit(
                    event_id=(
                        f"{round_id}-{client_id}-fingerprint"
                    ),
                    event_type=EventType.FINGERPRINT_GENERATED,
                    message=(
                        f"Privacy-safe fingerprint generated for "
                        f"client {client_id}."
                    ),
                    round_id=round_id,
                    client_id=client_id,
                    data={
                        "dimension": (
                            client_result.fingerprint.dimension
                        ),
                        "vector_hash": (
                            client_result.fingerprint.vector_hash
                        ),
                    },
                )

            # -------------------------------------------------
            # L2
            # -------------------------------------------------

            if client_result.layer2 is not None:
                detection = client_result.layer2

                if detection.is_outlier:
                    self._emit(
                        event_id=(
                            f"{round_id}-"
                            f"{client_id}-anomaly"
                        ),
                        event_type=EventType.ANOMALY_DETECTED,
                        message=(
                            f"Anomaly detected for client "
                            f"{client_id}."
                        ),
                        round_id=round_id,
                        client_id=client_id,
                        data={
                            "anomaly_score": (
                                detection.anomaly_score
                            ),
                            "z_score": detection.z_score,
                            "peer_similarity": (
                                detection.peer_similarity
                            ),
                            "is_outlier": detection.is_outlier,
                        },
                    )

                # -------------------------------------------------
                # Quarantine
                # -------------------------------------------------

                if client_result.quarantined:
                    self._emit(
                        event_id=(
                            f"{round_id}-"
                            f"{client_id}-quarantined"
                        ),
                        event_type=EventType.UPDATE_QUARANTINED,
                        message=(
                            f"Update from client {client_id} "
                            f"was quarantined."
                        ),
                        round_id=round_id,
                        client_id=client_id,
                        data={
                            "reason": detection.reason,
                            "anomaly_score": (
                                detection.anomaly_score
                            ),
                        },
                    )

            # -------------------------------------------------
            # L3
            # -------------------------------------------------

            if client_result.layer3 is not None:
                influence = client_result.layer3

                self._emit(
                    event_id=(
                        f"{round_id}-"
                        f"{client_id}-influence"
                    ),
                    event_type=EventType.INFLUENCE_TEST_COMPLETED,
                    message=(
                        f"Influence analysis completed for "
                        f"client {client_id}."
                    ),
                    round_id=round_id,
                    client_id=client_id,
                    data={
                        "influence_score": (
                            influence.influence_score
                        ),
                        "validation_delta": (
                            influence.validation_delta
                        ),
                        "harmful_influence": (
                            influence.harmful_influence
                        ),
                    },
                )

            # -------------------------------------------------
            # L4
            # -------------------------------------------------

            if client_result.layer4 is not None:
                counterfactual = client_result.layer4

                self._emit(
                    event_id=(
                        f"{round_id}-"
                        f"{client_id}-counterfactual"
                    ),
                    event_type=(
                        EventType.COUNTERFACTUAL_TEST_COMPLETED
                    ),
                    message=(
                        f"Counterfactual analysis completed for "
                        f"client {client_id}."
                    ),
                    round_id=round_id,
                    client_id=client_id,
                    data={
                        "accuracy_delta": (
                            counterfactual.accuracy_delta
                        ),
                        "loss_delta": (
                            counterfactual.loss_delta
                        ),
                        "harmful_counterfactual": (
                            counterfactual.harmful_counterfactual
                        ),
                    },
                )

            # -------------------------------------------------
            # L5
            # -------------------------------------------------

            if client_result.layer5 is not None:
                attribution = client_result.layer5

                self._emit(
                    event_id=(
                        f"{round_id}-"
                        f"{client_id}-attribution"
                    ),
                    event_type=EventType.ATTRIBUTION_UPDATED,
                    message=(
                        f"Threat attribution updated for "
                        f"client {client_id}."
                    ),
                    round_id=round_id,
                    client_id=client_id,
                    data={
                        "hypothesis": (
                            attribution.hypothesis.value
                        ),
                        "confidence": (
                            attribution.confidence
                        ),
                        "evidence_score": (
                            attribution.evidence_score
                        ),
                    },
                )

            # -------------------------------------------------
            # Trust
            # -------------------------------------------------

            if client_result.trust is not None:
                trust = client_result.trust

                self._emit(
                    event_id=(
                        f"{round_id}-"
                        f"{client_id}-trust"
                    ),
                    event_type=EventType.TRUST_UPDATED,
                    message=(
                        f"Trust decision updated for "
                        f"client {client_id}."
                    ),
                    round_id=round_id,
                    client_id=client_id,
                    data={
                        "risk_score": trust.risk_score,
                        "confidence": trust.confidence,
                        "status": trust.status.value,
                        "action": trust.action.value,
                        "hypothesis": trust.hypothesis.value,
                    },
                )

    # ---------------------------------------------------------
    # Main orchestration
    # ---------------------------------------------------------

    def execute_round(
        self,
        *,
        round_id: str,
        updates: list[ModelUpdate],
        global_state: StateDict,
        model_factory: Any,
        validation_loader: Any,
        device: str = "cpu",
    ) -> SecurityRoundResult:
        """
        Execute one complete operational security round.
        """

        managed_round = self.round_manager.get_round(
            round_id
        )

        if managed_round.status != RoundStatus.CREATED:
            raise RuntimeError(
                f"Round '{round_id}' must be in CREATED state "
                f"before orchestration."
            )

        self._emit_update_events(
            round_id=round_id,
            updates=updates,
        )

        # -----------------------------------------------------
        # Security pipeline
        # -----------------------------------------------------

        result = self.round_manager.execute_round(
            round_id=round_id,
            updates=updates,
            global_state=global_state,
            model_factory=model_factory,
            validation_loader=validation_loader,
            device=device,
        )

        # -----------------------------------------------------
        # Security events
        # -----------------------------------------------------

        self._emit_security_events(
            round_id=round_id,
            result=result,
        )

        # -----------------------------------------------------
        # Aggregation event
        # -----------------------------------------------------

        self._emit(
            event_id=f"{round_id}-aggregation-completed",
            event_type=EventType.AGGREGATION_COMPLETED,
            message=(
                f"Safe aggregation completed for round "
                f"{round_id}."
            ),
            round_id=round_id,
            data={
                "total_updates": result.total_updates,
                "accepted_updates": len(
                    result.accepted_updates
                ),
                "quarantined_updates": len(
                    result.quarantined_updates
                ),
            },
        )

        # -----------------------------------------------------
        # Incidents
        # -----------------------------------------------------

        incidents = self.incident_manager.create_from_round(
            round_result=result,
        )

        for incident in incidents:
            self._emit(
                event_id=(
                    f"{round_id}-"
                    f"{incident.primary_client_id}-incident"
                ),
                event_type=EventType.INCIDENT_CREATED,
                message=(
                    f"Security incident created for client "
                    f"{incident.primary_client_id}."
                ),
                round_id=round_id,
                client_id=incident.primary_client_id,
                data={
                    "incident_id": incident.incident_id,
                    "severity": incident.severity.value,
                    "hypothesis": incident.hypothesis.value,
                    "recommended_action": (
                        incident.recommended_action.value
                    ),
                },
            )

        # -----------------------------------------------------
        # Global model secured
        # -----------------------------------------------------

        self._emit(
            event_id=f"{round_id}-global-model-secured",
            event_type=EventType.GLOBAL_MODEL_SECURED,
            message=(
                f"Global model secured after security processing "
                f"for round {round_id}."
            ),
            round_id=round_id,
            data={
                "accepted_updates": len(
                    result.accepted_updates
                ),
                "quarantined_updates": len(
                    result.quarantined_updates
                ),
                "incident_required": result.incident_required,
            },
        )

        return result

    # ---------------------------------------------------------
    # Accessors
    # ---------------------------------------------------------

    def get_round(
        self,
        round_id: str,
    ) -> ManagedRound:
        """
        Get a managed round.
        """

        return self.round_manager.get_round(
            round_id
        )

    def get_incidents(
        self,
    ) -> list[ManagedIncident]:
        """
        Return all managed incidents.
        """

        return self.incident_manager.list_incidents()

    def get_events(
        self,
        *,
        round_id: str | None = None,
        client_id: str | None = None,
    ) -> list[SecurityEventRecord]:
        """
        Return operational events using optional filters.
        """

        return self.event_manager.query(
            round_id=round_id,
            client_id=client_id,
        )

    def clear(self) -> None:
        """
        Clear all in-memory orchestration state.
        """

        self.round_manager.clear()
        self.incident_manager.clear()
        self.event_manager.clear()