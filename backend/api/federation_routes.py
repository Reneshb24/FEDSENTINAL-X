from __future__ import annotations

import json

from backend.core.types import RoundStatus
from backend.layers.layer3_influence.subset_sampler import (
    create_validation_loader,
)
from backend.models.cnn import FedSentinelCNN
from backend.models.update import create_model_update
from backend.services.global_model_service import GlobalModelService
from backend.services.update_artifact_service import UpdateArtifactService
from data.dataset import load_mnist_test

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.api.dependencies import get_orchestrator
from backend.schemas import incidents
from backend.services.federation_service import FederationService
from backend.security.hashing import hash_state_dict
from backend.services.round_orchestrator import RoundOrchestrator
from backend.services.round_persistence_service import (
    RoundPersistenceService,
)

from backend.auth.dependencies import get_current_user, require_admin
from backend.schemas.federation import (
    FederationCreate,
    FederationResponse,
    FederationUpdate,
    MembershipActionRequest,
    MembershipCreate,
    MembershipResponse,
)
from backend.schemas.federation_round import (
    FederationRoundCreate,
    FederationRoundResponse,
)
from backend.services.federation_management_service import (
    FederationManagementService,
)
from backend.services.round_management_service import (
    RoundManagementService,
)
from backend.storage.database import get_db
from backend.storage.models import (
    Federation,
    FederationMembership,
    FederationRound,
    Hospital,
    Model,
    ModelUpdate,
    ModelVersion,
    User,
)


router = APIRouter(
    prefix="/federations",
    tags=["Federations"],
)


# ============================================================
# HELPERS
# ============================================================


def get_federation(
    db: Session,
    federation_id: str,
) -> Federation:

    federation = (
        db.query(Federation)
        .filter(Federation.id == federation_id)
        .first()
    )

    if not federation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Federation not found.",
        )

    return federation


def get_hospital(
    db: Session,
    hospital_id: str,
) -> Hospital:

    hospital = (
        db.query(Hospital)
        .filter(Hospital.id == hospital_id)
        .first()
    )

    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found.",
        )

    return hospital


def get_membership(
    db: Session,
    federation_id: str,
    hospital_id: str,
) -> FederationMembership:

    membership = (
        db.query(FederationMembership)
        .filter(
            FederationMembership.federation_id == federation_id,
            FederationMembership.hospital_id == hospital_id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Federation membership not found.",
        )

    return membership


def round_to_response(
    federation_round: FederationRound,
) -> FederationRoundResponse:

    configuration = json.loads(
        federation_round.config_json or "{}"
    )

    return FederationRoundResponse(
        id=federation_round.id,
        federation_id=federation_round.federation_id,
        round_number=federation_round.round_number,
        status=federation_round.status,
        global_model_version=(
            federation_round.global_model_version
        ),
        participating_clients=(
            federation_round.participating_clients
        ),
        accepted_updates=(
            federation_round.accepted_updates
        ),
        quarantined_updates=(
            federation_round.quarantined_updates
        ),
        started_at=federation_round.started_at,
        completed_at=federation_round.completed_at,
        created_at=federation_round.created_at,
        configuration=configuration,
    )
def get_federation_round(
    db: Session,
    federation_id: str,
    round_id: str,
) -> FederationRound:

    federation_round = (
        db.query(FederationRound)
        .filter(
            FederationRound.id == round_id,
            FederationRound.federation_id == federation_id,
        )
        .first()
    )

    if not federation_round:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Federation round not found.",
        )

    return federation_round

# ============================================================
# FEDERATION
# ============================================================


@router.get(
    "",
    response_model=list[FederationResponse],
)
def list_federations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Federation)
        .order_by(Federation.created_at.desc())
        .all()
    )


@router.post(
    "",
    response_model=FederationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_federation(
    payload: FederationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return FederationManagementService.create_federation(
        db,
        actor_user_id=current_user.id,
        **payload.model_dump(),
    )


@router.get(
    "/{federation_id}",
    response_model=FederationResponse,
)
def get_federation_details(
    federation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_federation(db, federation_id)


@router.patch(
    "/{federation_id}",
    response_model=FederationResponse,
)
def update_federation(
    federation_id: str,
    payload: FederationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    federation = get_federation(db, federation_id)

    data = payload.model_dump(exclude_unset=True)

    return FederationManagementService.update_federation(
        db,
        federation,
        actor_user_id=current_user.id,
        name=data.get("name"),
        description=data.get("description"),
        dataset_name=data.get("dataset_name"),
        model_name=data.get("model_name"),
        federation_status=data.get("status"),
    )


# ============================================================
# FEDERATION MEMBERS
# ============================================================


@router.get(
    "/{federation_id}/members",
    response_model=list[MembershipResponse],
)
def list_members(
    federation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    get_federation(db, federation_id)

    return (
        db.query(FederationMembership)
        .filter(
            FederationMembership.federation_id == federation_id
        )
        .order_by(FederationMembership.joined_at.desc())
        .all()
    )


@router.post(
    "/{federation_id}/members",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    federation_id: str,
    payload: MembershipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    federation = get_federation(db, federation_id)
    hospital = get_hospital(db, payload.hospital_id)

    return FederationManagementService.add_hospital(
        db,
        federation,
        hospital,
        actor_user_id=current_user.id,
        reason=payload.reason,
    )


@router.post(
    "/{federation_id}/members/{hospital_id}/remove",
    response_model=MembershipResponse,
)
def remove_member(
    federation_id: str,
    hospital_id: str,
    payload: MembershipActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    get_federation(db, federation_id)

    membership = get_membership(
        db,
        federation_id,
        hospital_id,
    )

    return FederationManagementService.remove_hospital(
        db,
        membership,
        actor_user_id=current_user.id,
        reason=payload.reason,
    )


# ============================================================
# FEDERATION ROUNDS
# ============================================================


@router.post(
    "/{federation_id}/rounds",
    response_model=FederationRoundResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_federation_round(
    federation_id: str,
    payload: FederationRoundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Create a persistent, reproducible federation round
    configuration.

    This endpoint does NOT execute the FL round.

    Execution remains the responsibility of
    FederationService + RoundOrchestrator.
    """

    federation = get_federation(
        db,
        federation_id,
    )

    # Concurrency rule: only one active execution per federation
    running_round = (
        db.query(FederationRound)
        .filter(
            FederationRound.federation_id == federation_id,
            FederationRound.status == "RUNNING",
        )
        .first()
    )
    if running_round is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Cannot create round: Round R-{running_round.round_number} "
                f"is currently RUNNING. Complete or cancel it first."
            ),
        )

    federation_round = (
        RoundManagementService.create_round(
            db,
            federation,
            actor_user_id=current_user.id,
            configuration=payload.configuration.model_dump(),
        )
    )

    return round_to_response(
        federation_round
    )


@router.get(
    "/{federation_id}/rounds",
    response_model=list[FederationRoundResponse],
)
def list_federation_rounds(
    federation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all persistent rounds for a federation.
    """

    get_federation(
        db,
        federation_id,
    )

    rounds = (
        db.query(FederationRound)
        .filter(
            FederationRound.federation_id == federation_id
        )
        .order_by(
            FederationRound.round_number.desc()
        )
        .all()
    )

    return [
        round_to_response(round_)
        for round_ in rounds
    ]
@router.post(
    "/{federation_id}/rounds/{round_id}/start",
    response_model=FederationRoundResponse,
)
def start_federation_round(
    federation_id: str,
    round_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    orchestrator: RoundOrchestrator = Depends(get_orchestrator),
):
    """
    Start a persisted federation round.

    The saved configuration is used to construct the FL execution
    service. Security analysis remains inside the existing
    RoundOrchestrator + SecurityPipeline.
    """

    federation = get_federation(
        db,
        federation_id,
    )

    federation_round = get_federation_round(
        db,
        federation_id,
        round_id,
    )

    # ------------------------------------------------------------
    # Load persisted configuration
    # ------------------------------------------------------------

    try:
        configuration = json.loads(
            federation_round.config_json or "{}"
        )

        # Historical rounds predate execution_mode.
        # Preserve their original simulator behavior.
        configuration.setdefault(
            "execution_mode",
            "SIMULATION",
        )

    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored round configuration is invalid JSON.",
        ) from exc

    execution_mode = configuration["execution_mode"]

    if execution_mode not in {"SIMULATION", "HOSPITAL"}:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Unsupported round execution mode: "
                f"{execution_mode}"
            ),
        )

    required_keys = {
        "num_clients",
        "seed",
        "concentration",
        "local_epochs",
        "batch_size",
        "learning_rate",
        "validation_sample_size",
        "validation_batch_size",
        "device",
        "inject_attack",
        "attack_scale",
    }

    missing = required_keys.difference(configuration.keys())

    if missing:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Round configuration is incomplete. "
                f"Missing: {sorted(missing)}"
            ),
        )

    # ------------------------------------------------------------
    # Validate federation participants again at execution time
    # ------------------------------------------------------------

    eligible_count = (
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
        .count()
    )

    if eligible_count < configuration["num_clients"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Only {eligible_count} eligible active hospital(s) "
                f"are available, but the round requires "
                f"{configuration['num_clients']}."
            ),
        )

    # ------------------------------------------------------------
    # Prevent duplicate execution
    # ------------------------------------------------------------

    if federation_round.status != "CREATED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Round '{round_id}' is already "
                f"'{federation_round.status}'."
            ),
        )

    # Concurrency rule: prevent concurrent RUNNING rounds
    running_round = (
        db.query(FederationRound)
        .filter(
            FederationRound.federation_id == federation.id,
            FederationRound.status == "RUNNING",
            FederationRound.id != round_id,
        )
        .first()
    )
    if running_round is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Cannot start round: Round R-{running_round.round_number} "
                f"is already RUNNING. Complete or cancel it first."
            ),
        )

    # ------------------------------------------------------------
    # Create the matching in-memory security round
    # ------------------------------------------------------------

    try:
        orchestrator.create_round(
            round_id=round_id,
            target_clients=configuration["num_clients"],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    # ------------------------------------------------------------
    # Persist RUNNING
    # ------------------------------------------------------------

    RoundManagementService.mark_started(
        db,
        federation_round,
        actor_user_id=current_user.id,
    )

    # ------------------------------------------------------------
    # HOSPITAL EXECUTION MODE
    #
    # The round is now open for real hospital submissions.
    # Do NOT execute the server-side simulator.
    # ------------------------------------------------------------

    if execution_mode == "HOSPITAL":
        try:
            orchestrator.create_round(
                round_id=round_id,
                target_clients=configuration.get("num_clients", federation_round.participating_clients or 2),
            )
        except Exception:
            pass
        return round_to_response(
            federation_round
        )

    # ------------------------------------------------------------
    # SIMULATION EXECUTION MODE
    # ------------------------------------------------------------

    federation_service = FederationService(
        orchestrator=orchestrator,
        num_clients=configuration["num_clients"],
        seed=configuration["seed"],
        concentration=configuration["concentration"],
        local_epochs=configuration["local_epochs"],
        batch_size=configuration["batch_size"],
        learning_rate=configuration["learning_rate"],
        validation_sample_size=configuration[
            "validation_sample_size"
        ],
        validation_batch_size=configuration[
            "validation_batch_size"
        ],
        device=configuration["device"],
    )

    # ------------------------------------------------------------
    # Execute actual FL + security pipeline
    # ------------------------------------------------------------

    try:

        federation_service.execute(
            round_id=round_id,
            inject_attack=configuration["inject_attack"],
            attack_scale=configuration["attack_scale"],
        )

    except Exception as exc:

        db.rollback()

        RoundManagementService.mark_failed(
            db,
            federation_round,
            actor_user_id=current_user.id,
            reason=f"Round execution failed: {exc}",
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Round execution failed: {exc}",
        ) from exc

    # ------------------------------------------------------------
    # Read actual security result
    # ------------------------------------------------------------

    managed_round = orchestrator.get_round(
        round_id
    )

    result = managed_round.result

    if result is None:
        RoundManagementService.mark_failed(
            db,
            federation_round,
            actor_user_id=current_user.id,
            reason="Execution completed without a security result.",
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Execution completed without a security result.",
        )

    incidents = orchestrator.get_incidents()

    round_incidents = [
        incident
        for incident in incidents
        if incident.round_id == round_id
    ]

    RoundPersistenceService().persist_round(
        db,
        federation=federation,
        federation_round=federation_round,
        result=result,
        incidents=round_incidents,
    )

    accepted_count = len(
        result.accepted_updates
    )

    quarantined_count = len(
        result.quarantined_updates
    )

    # ------------------------------------------------------------
    # Global model identity
    # ------------------------------------------------------------

    model_hash = (
        hash_state_dict(result.global_state)
        if result.global_state is not None
        else None
    )

    global_model_version = (
        f"round-{federation_round.round_number}"
    )

    # ------------------------------------------------------------
    # Persist actual result
    # ------------------------------------------------------------

    federation_round = (
        RoundManagementService.mark_completed(
            db,
            federation_round,
            actor_user_id=current_user.id,
            accepted_updates=accepted_count,
            quarantined_updates=quarantined_count,
            global_model_version=global_model_version,
        )
    )

    return round_to_response(
        federation_round
    )

# ============================================================
# HOSPITAL ROUND FINALIZATION
# ============================================================

@router.post(
    "/{federation_id}/rounds/{round_id}/finalize",
    response_model=FederationRoundResponse,
)
def finalize_hospital_round(
    federation_id: str,
    round_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    orchestrator: RoundOrchestrator = Depends(get_orchestrator),
):
    """
    Finalize a real hospital-executed round.

    All submitted hospital updates are loaded from their verified
    SafeTensors artifacts and passed through the existing:

        L0 ? L1 ? L2 ? L3 ? L4 ? L5 ? Trust ? Safe Aggregation

    pipeline.

    No hospital update is accepted merely because it was submitted.
    """

    federation = get_federation(
        db,
        federation_id,
    )

    federation_round = get_federation_round(
        db,
        federation_id,
        round_id,
    )

    if federation_round.status != "RUNNING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Round must be RUNNING before finalization. "
                f"Current status: {federation_round.status}."
            ),
        )

    # ------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------

    try:
        configuration = json.loads(
            federation_round.config_json or "{}"
        )
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored round configuration is invalid JSON.",
        ) from exc

    execution_mode = configuration.get(
        "execution_mode",
        "SIMULATION",
    )

    if execution_mode != "HOSPITAL":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only HOSPITAL rounds can be finalized through this endpoint.",
        )

    # ------------------------------------------------------------
    # Load submitted updates
    # ------------------------------------------------------------

    persisted_updates = (
        db.query(ModelUpdate)
        .filter(
            ModelUpdate.round_id == round_id,
        )
        .order_by(
            ModelUpdate.submitted_at.asc()
        )
        .all()
    )

    if not persisted_updates:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No hospital updates have been submitted.",
        )

    required_clients = configuration.get(
        "num_clients",
        federation_round.participating_clients,
    )

    if len(persisted_updates) < required_clients:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Only {len(persisted_updates)} hospital update(s) "
                f"have been submitted, but {required_clients} "
                f"are required before finalization."
            ),
        )

    # ------------------------------------------------------------
    # Load verified update artifacts
    # ------------------------------------------------------------

    artifact_service = UpdateArtifactService()
    runtime_updates = []

    for persisted in persisted_updates:
        if not persisted.artifact_hash:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Update {persisted.id} has no artifact hash."
                ),
            )

        if persisted.artifact_type != "safetensors":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Update {persisted.id} has unsupported artifact type."
                ),
            )

        try:
            delta = artifact_service.load_verified(
                round_id=round_id,
                hospital_id=persisted.hospital_id,
                update_id=persisted.id,
                expected_hash=persisted.artifact_hash,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Update artifact verification failed for "
                    f"{persisted.id}: {exc}"
                ),
            ) from exc

        runtime_updates.append(
            create_model_update(
                update_id=persisted.id,
                client_id=persisted.hospital_id,
                round_id=round_id,
                delta=delta,
                num_examples=persisted.num_examples,
            )
        )

    # ------------------------------------------------------------
    # Load latest verified global model
    # ------------------------------------------------------------

    global_model_service = GlobalModelService()

    try:
        (
            model_version,
            global_state,
        ) = global_model_service.load_latest_verified(
            db,
            federation=federation,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load verified global model: {exc}",
        ) from exc

    # ------------------------------------------------------------
    # Validation loader
    # ------------------------------------------------------------

    try:
        test_dataset = load_mnist_test()

        validation_loader = create_validation_loader(
            dataset=test_dataset,
            sample_size=configuration.get(
                "validation_sample_size",
                1000,
            ),
            batch_size=configuration.get(
                "validation_batch_size",
                64,
            ),
            seed=configuration.get(
                "seed",
                42,
            ),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create validation loader: {exc}",
        ) from exc

    # ------------------------------------------------------------
    # Execute the EXISTING security pipeline
    # ------------------------------------------------------------

    try:
        try:
            managed_round = orchestrator.round_manager.get_round(round_id)
            if managed_round.status != RoundStatus.CREATED:
                managed_round.status = RoundStatus.CREATED
        except KeyError:
            orchestrator.create_round(
                round_id=round_id,
                target_clients=len(runtime_updates),
            )

        result = orchestrator.execute_round(
            round_id=round_id,
            updates=runtime_updates,
            global_state=global_state,
            model_factory=FedSentinelCNN,
            validation_loader=validation_loader,
            device=configuration.get(
                "device",
                "cpu",
            ),
        )
    except Exception as exc:
        db.rollback()

        RoundManagementService.mark_failed(
            db,
            federation_round,
            actor_user_id=current_user.id,
            reason=f"Hospital round finalization failed: {exc}",
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hospital round security processing failed: {exc}",
        ) from exc

    # ------------------------------------------------------------
    # Persist security result
    # ------------------------------------------------------------

    incidents = orchestrator.get_incidents()

    round_incidents = [
        incident
        for incident in incidents
        if incident.round_id == round_id
    ]

    try:
        RoundPersistenceService().persist_round(
            db,
            federation=federation,
            federation_round=federation_round,
            result=result,
            incidents=round_incidents,
        )
    except Exception as exc:
        db.rollback()

        RoundManagementService.mark_failed(
            db,
            federation_round,
            actor_user_id=current_user.id,
            reason=f"Round persistence failed: {exc}",
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hospital round persistence failed: {exc}",
        ) from exc

    # ------------------------------------------------------------
    # Complete persistent round
    # ------------------------------------------------------------

    accepted_count = len(
        result.accepted_updates
    )

    quarantined_count = len(
        result.quarantined_updates
    )

    global_model_version = (
        f"round-{federation_round.round_number}"
    )

    federation_round = (
        RoundManagementService.mark_completed(
            db,
            federation_round,
            actor_user_id=current_user.id,
            accepted_updates=accepted_count,
            quarantined_updates=quarantined_count,
            global_model_version=global_model_version,
        )
    )

    return round_to_response(
        federation_round
    )

# ============================================================
# ROUND LIFECYCLE MANAGEMENT (CANCEL / FAIL / RESET)
# ============================================================

@router.post(
    "/{federation_id}/rounds/{round_id}/cancel",
    response_model=FederationRoundResponse,
)
def cancel_federation_round(
    federation_id: str,
    round_id: str,
    payload: dict | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Cancel a CREATED or RUNNING federation round with an audited reason.
    """
    get_federation(db, federation_id)
    federation_round = get_federation_round(db, federation_id, round_id)
    reason = (payload or {}).get("reason") if isinstance(payload, dict) else "Round cancelled by administrator."
    reason = reason or "Round cancelled by administrator."

    cancelled = RoundManagementService.mark_cancelled(
        db,
        federation_round,
        actor_user_id=current_user.id,
        reason=reason,
    )
    return round_to_response(cancelled)


@router.post(
    "/{federation_id}/rounds/{round_id}/fail",
    response_model=FederationRoundResponse,
)
def fail_federation_round(
    federation_id: str,
    round_id: str,
    payload: dict | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Mark a RUNNING federation round as FAILED with an audited reason.
    """
    get_federation(db, federation_id)
    federation_round = get_federation_round(db, federation_id, round_id)
    reason = (payload or {}).get("reason") if isinstance(payload, dict) else "Round marked failed by administrator."
    reason = reason or "Round marked failed by administrator."

    failed = RoundManagementService.mark_failed(
        db,
        federation_round,
        actor_user_id=current_user.id,
        reason=reason,
    )
    return round_to_response(failed)


@router.post(
    "/{federation_id}/rounds/{round_id}/reset",
    response_model=FederationRoundResponse,
)
def reset_federation_round(
    federation_id: str,
    round_id: str,
    payload: dict | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Reset a FAILED or RUNNING federation round back to CREATED state.
    """
    get_federation(db, federation_id)
    federation_round = get_federation_round(db, federation_id, round_id)
    reason = (payload or {}).get("reason") if isinstance(payload, dict) else "Round reset by administrator."
    reason = reason or "Round reset by administrator."

    reset_round = RoundManagementService.reset_failed_round(
        db,
        federation_round,
        actor_user_id=current_user.id,
        reason=reason,
    )
    return round_to_response(reset_round)

@router.get(
    "/{federation_id}/models",
    response_model=dict,
)
def get_federation_models(
    federation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return global model architecture details and all historical model versions with lineage.
    """
    federation = get_federation(db, federation_id)
    model = (
        db.query(Model)
        .filter(Model.name == federation.model_name)
        .first()
    )
    versions = []
    if model:
        raw_versions = (
            db.query(ModelVersion)
            .filter(ModelVersion.model_id == model.id)
            .order_by(ModelVersion.created_at.desc())
            .all()
        )
        versions = [
            {
                "id": v.id,
                "version": v.version,
                "parent_version": v.parent_version,
                "round_id": v.round_id,
                "model_hash": v.model_hash,
                "security_status": v.security_status,
                "validation_accuracy": v.validation_accuracy,
                "accepted_update_count": v.accepted_update_count,
                "quarantined_update_count": v.quarantined_update_count,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
            for v in raw_versions
        ]
    return {
        "model": {
            "id": model.id if model else None,
            "name": model.name if model else federation.model_name,
            "architecture": model.architecture if model else "FedSentinelCNN",
            "framework": model.framework if model else "PyTorch",
            "parameter_count": 105866,
        },
        "versions": versions,
    }

