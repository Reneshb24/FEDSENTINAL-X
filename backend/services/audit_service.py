from __future__ import annotations

from sqlalchemy.orm import Session

from backend.storage.models import AuditEvent


class AuditService:

    @staticmethod
    def list_events(
        db: Session,
        *,
        action: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        result: str | None = None,
        actor_user_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[AuditEvent], int]:

        query = db.query(AuditEvent)

        if action:
            query = query.filter(AuditEvent.action == action)

        if resource_type:
            query = query.filter(
                AuditEvent.resource_type == resource_type
            )

        if resource_id:
            query = query.filter(
                AuditEvent.resource_id == resource_id
            )

        if result:
            query = query.filter(
                AuditEvent.result == result
            )

        if actor_user_id:
            query = query.filter(
                AuditEvent.actor_user_id == actor_user_id
            )

        total = query.count()

        events = (
            query
            .order_by(AuditEvent.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return events, total


    @staticmethod
    def get_event(
        db: Session,
        event_id: str,
    ) -> AuditEvent | None:

        return (
            db.query(AuditEvent)
            .filter(AuditEvent.id == event_id)
            .first()
        )