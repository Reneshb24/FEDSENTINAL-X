from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.storage.database import get_db
from backend.auth.dependencies import require_security_analyst
from backend.schemas.audit import (
    AuditEventListResponse,
    AuditEventResponse,
)
from backend.services.audit_service import AuditService


router = APIRouter(
    prefix="/audit",
    tags=["Audit Trail"],
)


@router.get(
    "",
    response_model=AuditEventListResponse,
    summary="List audit events",
)
def list_audit_events(
    action: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    resource_id: str | None = Query(default=None),
    result: str | None = Query(default=None),
    actor_user_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(require_security_analyst),
):
    events, total = AuditService.list_events(
        db,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        result=result,
        actor_user_id=actor_user_id,
        limit=limit,
        offset=offset,
    )

    return AuditEventListResponse(
        value=events,
        count=total,
    )


@router.get(
    "/{event_id}",
    response_model=AuditEventResponse,
    summary="Get an audit event",
)
def get_audit_event(
    event_id: str,
    db: Session = Depends(get_db),
    _user=Depends(require_security_analyst),
):
    event = AuditService.get_event(db, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit event not found",
        )

    return event