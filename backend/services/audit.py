from __future__ import annotations

import json

from sqlalchemy.orm import Session

from backend.storage.models import AuditEvent


def record_audit(
    db: Session,
    *,
    actor_user_id: str | None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    reason: str | None = None,
    result: str = "SUCCESS",
    ip_address: str | None = None,
    session_id: str | None = None,
    metadata: dict | None = None,
) -> AuditEvent:

    event = AuditEvent(
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        reason=reason,
        result=result,
        ip_address=ip_address,
        session_id=session_id,
        metadata_json=json.dumps(metadata or {}),
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event