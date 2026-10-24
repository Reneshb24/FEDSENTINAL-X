from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_user_id: str | None
    action: str
    resource_type: str | None
    resource_id: str | None
    reason: str | None
    result: str
    ip_address: str | None
    session_id: str | None
    metadata_json: str
    created_at: datetime


class AuditEventListResponse(BaseModel):
    value: list[AuditEventResponse]
    count: int