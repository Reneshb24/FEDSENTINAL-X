"""
FedSentinel REST API routes.

This module exposes the operational security control plane through
HTTP endpoints.

The routes are intentionally thin:

    HTTP request
        ↓
    Pydantic validation
        ↓
    Existing FedSentinel services
        ↓
    Security / federation / persistence layers

No L0-L5 detection logic belongs in this module.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.api.dependencies import (
    get_federation_service,
    get_orchestrator,
)

from backend.api.hospital_routes import (
    router as hospital_router,
)

from backend.api.federation_routes import (
    router as federation_router,
)

from backend.api.security_routes import (
    router as security_router,
)

from backend.core.types import RoundStatus
from backend.security.hashing import hash_state_dict

from backend.schemas.events import (
    EventBatch,
    SecurityEvent,
)

from backend.schemas.incidents import (
    IncidentEvidence,
    IncidentListResponse,
    IncidentResponse,
)

from backend.schemas.rounds import (
    RoundListResponse,
    RoundMetrics,
    RoundResponse,
)

from backend.services.round_orchestrator import (
    RoundOrchestrator,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["FedSentinel"],
)


# ==================================================================
# Health
# ==================================================================


@router.get(
    "/health",
    summary="Check API health",
)
def health() -> dict[str, str]:
    """
    Return basic API health information.
    """

    return {
        "status": "ok",
        "service": "FedSentinel",
    }


# ==================================================================
# Rounds
# ==================================================================


def _round_to_response(
    managed_round,
) -> RoundResponse:
    """
    Convert an internal ManagedRound into the public API schema.

    Completed-round metrics are derived directly from the actual
    SecurityRoundResult. No security values are fabricated.
    """

    result = managed_round.result

    if result is None:

        metrics = RoundMetrics(
            participating_clients=managed_round.target_clients,
        )

        global_model_hash = None

    else:

        trust_decisions = [
            client_result.trust
            for client_result in result.client_results.values()
            if client_result.trust is not None
        ]

        average_risk_score = None

        if trust_decisions:
            average_risk_score = (
                sum(
                    decision.risk_score
                    for decision in trust_decisions
                )
                / len(trust_decisions)
            )

        metrics = RoundMetrics(
            participating_clients=len(
                result.client_results
            ),
            received_updates=result.total_updates,
            accepted_updates=len(
                result.accepted_updates
            ),
            quarantined_updates=len(
                result.quarantined_updates
            ),
            average_training_loss=None,
            global_validation_accuracy=None,
            average_risk_score=average_risk_score,
        )

        global_model_hash = (
            hash_state_dict(result.global_state)
            if result.global_state is not None
            else None
        )

    return RoundResponse(
        round_id=managed_round.round_id,
        status=managed_round.status,
        target_clients=managed_round.target_clients,
        created_at=managed_round.created_at,
        started_at=managed_round.started_at,
        completed_at=managed_round.completed_at,
        metrics=metrics,
        global_model_hash=global_model_hash,
    )


@router.get(
    "/rounds",
    response_model=RoundListResponse,
    summary="List federated learning rounds",
)
def list_rounds(
    orchestrator: RoundOrchestrator = Depends(
        get_orchestrator
    ),
) -> RoundListResponse:
    """
    Return all managed rounds.

    The current RoundManager stores rounds in memory.
    """

    rounds = orchestrator.round_manager.list_rounds()

    responses = [
        _round_to_response(item)
        for item in rounds
    ]

    return RoundListResponse(
        rounds=responses,
        total=len(responses),
    )


@router.post(
    "/rounds",
    response_model=RoundResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a federated learning round",
)
def create_round(
    round_id: str = Query(
        ...,
        min_length=1,
        max_length=64,
        description="Unique round identifier",
    ),
    target_clients: int = Query(
        20,
        ge=1,
        description="Expected number of participating clients",
    ),
    orchestrator: RoundOrchestrator = Depends(
        get_orchestrator
    ),
) -> RoundResponse:
    """
    Create a new security round.

    Execution is deliberately separate from creation.

    The resulting round remains in CREATED state until the execution
    workflow is invoked.
    """

    try:

        managed_round = orchestrator.create_round(
            round_id=round_id,
            target_clients=target_clients,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return _round_to_response(
        managed_round
    )


@router.get(
    "/rounds/{round_id}",
    response_model=RoundResponse,
    summary="Get a federated learning round",
)
def get_round(
    round_id: str,
    orchestrator: RoundOrchestrator = Depends(
        get_orchestrator
    ),
) -> RoundResponse:
    """
    Return one managed round.
    """

    try:

        managed_round = orchestrator.get_round(
            round_id
        )

    except KeyError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return _round_to_response(
        managed_round
    )


# ==================================================================
# Round execution
# ==================================================================


@router.post(
    "/rounds/{round_id}/execute",
    response_model=RoundResponse,
    summary="Execute a federated learning security round",
)
def execute_round(
    round_id: str,

    inject_attack: bool = Query(
        True,
        description=(
            "Inject the deterministic synthetic demo attack."
        ),
    ),

    attack_scale: float = Query(
        25.0,
        gt=0,
        description=(
            "Synthetic demo attack scale."
        ),
    ),

    orchestrator: RoundOrchestrator = Depends(
        get_orchestrator
    ),

    federation_service=Depends(
        get_federation_service
    ),
) -> RoundResponse:
    """
    Execute a complete simulated federated-learning security round.

    The attack configuration belongs only to the simulation layer.

    The security pipeline independently analyzes the generated
    updates and does not receive attack ground truth.
    """

    try:

        managed_round = orchestrator.get_round(
            round_id
        )

    except KeyError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if (
        managed_round.target_clients
        != federation_service.num_clients
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Round '{round_id}' expects "
                f"{managed_round.target_clients} clients, "
                f"but the configured federation simulator "
                f"uses {federation_service.num_clients} clients."
            ),
        )

    try:

        federation_service.execute(
            round_id=round_id,
            inject_attack=inject_attack,
            attack_scale=attack_scale,
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Round execution failed: {exc}"
            ),
        ) from exc

    return _round_to_response(
        orchestrator.get_round(
            round_id
        )
    )


# ==================================================================
# Events
# ==================================================================


def _event_to_response(
    event,
) -> SecurityEvent:
    """
    Convert an internal SecurityEventRecord to the public API schema.
    """

    return SecurityEvent(
        event_id=event.event_id,
        event_type=event.event_type,
        timestamp=event.timestamp,
        round_id=event.round_id,
        client_id=event.client_id,
        update_id=event.data.get("update_id"),
        message=event.message,
        payload=event.data,
    )


@router.get(
    "/events",
    response_model=EventBatch,
    summary="List security events",
)
def list_events(
    round_id: str | None = Query(
        default=None,
        max_length=64,
    ),

    client_id: str | None = Query(
        default=None,
        max_length=64,
    ),

    orchestrator: RoundOrchestrator = Depends(
        get_orchestrator
    ),
) -> EventBatch:
    """
    Return security events with optional round/client filtering.
    """

    events = orchestrator.get_events(
        round_id=round_id,
        client_id=client_id,
    )

    responses = [
        _event_to_response(event)
        for event in events
    ]

    return EventBatch(
        events=responses,
        total=len(responses),
    )


@router.get(
    "/rounds/{round_id}/events",
    response_model=EventBatch,
    summary="List events for a round",
)
def list_round_events(
    round_id: str,

    orchestrator: RoundOrchestrator = Depends(
        get_orchestrator
    ),
) -> EventBatch:
    """
    Return all security events belonging to a specific round.
    """

    try:

        orchestrator.get_round(
            round_id
        )

    except KeyError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    events = orchestrator.get_events(
        round_id=round_id
    )

    responses = [
        _event_to_response(event)
        for event in events
    ]

    return EventBatch(
        events=responses,
        total=len(responses),
    )


# ==================================================================
# Runtime Incidents
# ==================================================================


def _incident_to_response(
    incident,
) -> IncidentResponse:
    """
    Convert an internal ManagedIncident into the public API schema.

    Runtime incidents are different from persisted database
    incidents exposed by the Security Investigation API.
    """

    evidence = IncidentEvidence(
        client_ids=list(
            incident.affected_clients
        ),

        round_ids=[
            incident.round_id
        ],

        evidence_items=list(
            incident.evidence
        ),
    )

    return IncidentResponse(
        incident_id=incident.incident_id,
        title=incident.title,
        description=incident.description,
        threat_level=incident.severity,
        threat_hypothesis=incident.hypothesis,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        status=incident.status,
        recommended_action=incident.recommended_action,
        risk_score=incident.risk_score,
        confidence=incident.confidence,
        evidence=evidence,
        assigned_to=None,
        resolved_at=incident.resolved_at,
        resolution_notes=incident.resolution,
    )


@router.get(
    "/incidents",
    response_model=IncidentListResponse,
    summary="List runtime security incidents",
)
def list_incidents(
    orchestrator: RoundOrchestrator = Depends(
        get_orchestrator
    ),
) -> IncidentListResponse:
    """
    Return runtime security incidents.

    These are maintained by IncidentManager in memory.
    """

    incidents = orchestrator.get_incidents()

    responses = [
        _incident_to_response(
            incident
        )
        for incident in incidents
    ]

    return IncidentListResponse(
        incidents=responses,
        total=len(responses),
    )


@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentResponse,
    summary="Get a runtime security incident",
)
def get_incident(
    incident_id: str,

    orchestrator: RoundOrchestrator = Depends(
        get_orchestrator
    ),
) -> IncidentResponse:
    """
    Return one runtime security incident.
    """

    try:

        incident = (
            orchestrator
            .incident_manager
            .get_incident(
                incident_id
            )
        )

    except KeyError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return _incident_to_response(
        incident
    )


# ==================================================================
# Router Registration
# ==================================================================
#
# The main router uses /api/v1.
#
# Child routers retain their own prefixes:
#
#   federation_router → /federations
#   hospital_router   → /hospitals
#   security_router   → /security
#
# Therefore the final API paths become:
#
#   /api/v1/federations/...
#   /api/v1/hospitals/...
#   /api/v1/security/...
#
# ==================================================================


router.include_router(
    federation_router
)

router.include_router(
    hospital_router
)

router.include_router(
    security_router
)