from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.core.types import (
    Action,
    ThreatHypothesis,
    ThreatLevel,
    TrustStatus,
)
from backend.services.incident_manager import (
    IncidentManager,
)
from backend.services.security_pipeline import (
    ClientSecurityResult,
    SecurityRoundResult,
)


def make_client_result(
    client_id: str = "H11",
) -> ClientSecurityResult:
    result = ClientSecurityResult(
        client_id=client_id,
        update_id=f"update-{client_id}",
    )

    return result


def make_quarantined_result(
    client_id: str = "H11",
) -> ClientSecurityResult:
    result = make_client_result(client_id)

    class Trust:
        status = TrustStatus.QUARANTINED
        action = Action.QUARANTINE
        hypothesis = ThreatHypothesis.MODEL_POISONING
        risk_score = 80.0

    result.trust = Trust()
    result.quarantined = True

    result.evidence_items = [
        "L0 validation failed.",
        "L2 anomaly detected.",
    ]

    return result


def make_round_result(
    result: ClientSecurityResult,
) -> SecurityRoundResult:
    now = datetime.now(timezone.utc)

    return SecurityRoundResult(
        round_id="round-001",
        started_at=now,
        completed_at=now,
        total_updates=1,
        accepted_updates=[],
        quarantined_updates=[],
        client_results={
            result.client_id: result,
        },
        global_state=None,
        incident_required=True,
    )


def test_create_incident() -> None:
    manager = IncidentManager()

    result = make_quarantined_result()

    incident = manager.create_incident(
        incident_id="INC-round-001-H11",
        round_id="round-001",
        client_result=result,
    )

    assert incident.incident_id == "INC-round-001-H11"
    assert incident.round_id == "round-001"
    assert incident.primary_client_id == "H11"
    assert incident.status == "OPEN"
    assert incident.severity == ThreatLevel.CRITICAL
    assert incident.hypothesis == ThreatHypothesis.MODEL_POISONING
    assert incident.recommended_action == Action.QUARANTINE
    assert "H11" in incident.affected_clients


def test_duplicate_incident_rejected() -> None:
    manager = IncidentManager()

    result = make_quarantined_result()

    manager.create_incident(
        incident_id="INC-round-001-H11",
        round_id="round-001",
        client_result=result,
    )

    with pytest.raises(ValueError):
        manager.create_incident(
            incident_id="INC-round-001-H11",
            round_id="round-001",
            client_result=result,
        )


def test_create_from_round() -> None:
    manager = IncidentManager()

    result = make_quarantined_result()

    round_result = make_round_result(result)

    incidents = manager.create_from_round(
        round_result=round_result,
    )

    assert len(incidents) == 1
    assert incidents[0].primary_client_id == "H11"


def test_clean_client_does_not_create_incident() -> None:
    manager = IncidentManager()

    result = make_client_result("H1")

    round_result = make_round_result(result)

    incidents = manager.create_from_round(
        round_result=round_result,
    )

    assert incidents == []


def test_get_incident() -> None:
    manager = IncidentManager()

    result = make_quarantined_result()

    manager.create_incident(
        incident_id="INC-round-001-H11",
        round_id="round-001",
        client_result=result,
    )

    incident = manager.get_incident(
        "INC-round-001-H11"
    )

    assert incident.primary_client_id == "H11"


def test_missing_incident_rejected() -> None:
    manager = IncidentManager()

    with pytest.raises(KeyError):
        manager.get_incident("does-not-exist")


def test_resolve_incident() -> None:
    manager = IncidentManager()

    result = make_quarantined_result()

    manager.create_incident(
        incident_id="INC-round-001-H11",
        round_id="round-001",
        client_result=result,
    )

    incident = manager.resolve_incident(
        incident_id="INC-round-001-H11",
        resolution="Client update quarantined and excluded from aggregation.",
    )

    assert incident.status == "RESOLVED"
    assert incident.resolution is not None
    assert incident.resolved_at is not None


def test_reopen_incident() -> None:
    manager = IncidentManager()

    result = make_quarantined_result()

    manager.create_incident(
        incident_id="INC-round-001-H11",
        round_id="round-001",
        client_result=result,
    )

    manager.resolve_incident(
        incident_id="INC-round-001-H11",
        resolution="Incident investigated.",
    )

    incident = manager.reopen_incident(
        incident_id="INC-round-001-H11",
    )

    assert incident.status == "OPEN"
    assert incident.resolution is None
    assert incident.resolved_at is None


def test_invalid_resolution_rejected() -> None:
    manager = IncidentManager()

    result = make_quarantined_result()

    manager.create_incident(
        incident_id="INC-round-001-H11",
        round_id="round-001",
        client_result=result,
    )

    with pytest.raises(ValueError):
        manager.resolve_incident(
            incident_id="INC-round-001-H11",
            resolution="   ",
        )


def test_list_incidents() -> None:
    manager = IncidentManager()

    first = make_quarantined_result("H11")
    second = make_quarantined_result("H12")

    manager.create_incident(
        incident_id="INC-round-001-H11",
        round_id="round-001",
        client_result=first,
    )

    manager.create_incident(
        incident_id="INC-round-001-H12",
        round_id="round-001",
        client_result=second,
    )

    incidents = manager.list_incidents()

    assert len(incidents) == 2
    assert incidents[0].primary_client_id == "H11"
    assert incidents[1].primary_client_id == "H12"