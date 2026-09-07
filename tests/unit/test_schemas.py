"""
Unit tests for FedSentinel Pydantic schemas.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from backend.core.types import (
    Action,
    ClientStatus,
    DetectionStatus,
    EventType,
    RoundStatus,
    ThreatHypothesis,
    ThreatLevel,
    TrustStatus,
)
from backend.schemas.clients import (
    ClientCreate,
    ClientTrustSummary,
)
from backend.schemas.detections import (
    DetectionDecision,
    DetectionEvidence,
    DetectionResult,
)
from backend.schemas.events import SecurityEvent
from backend.schemas.incidents import IncidentResponse
from backend.schemas.rounds import RoundResponse
from backend.schemas.updates import (
    UpdateCreate,
    UpdateIntegrity,
    UpdateProvenance,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def now() -> datetime:
    """Return a timestamp for test data."""

    return datetime.now()


# ---------------------------------------------------------------------------
# Client tests
# ---------------------------------------------------------------------------


def test_client_create_valid() -> None:
    client = ClientCreate(
        client_id="H1",
        name="Hospital 1",
    )

    assert client.client_id == "H1"
    assert client.name == "Hospital 1"
    assert client.status == ClientStatus.ACTIVE


def test_client_create_rejects_empty_id() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(
            client_id="",
            name="Hospital 1",
        )


def test_client_trust_score_range() -> None:
    with pytest.raises(ValidationError):
        ClientTrustSummary(
            trust_score=101,
            trust_status=TrustStatus.TRUSTED,
            last_updated=now(),
        )


# ---------------------------------------------------------------------------
# Update tests
# ---------------------------------------------------------------------------


def test_update_create_valid() -> None:
    update = UpdateCreate(
        update_id="U001",
        client_id="H1",
        round_id="R001",
        num_examples=100,
        submitted_at=now(),
        integrity=UpdateIntegrity(
            artifact_hash="abc123",
        ),
        provenance=UpdateProvenance(
            client_id="H1",
            round_id="R001",
            created_at=now(),
        ),
    )

    assert update.update_id == "U001"
    assert update.client_id == "H1"
    assert update.num_examples == 100


def test_update_rejects_zero_examples() -> None:
    with pytest.raises(ValidationError):
        UpdateCreate(
            update_id="U001",
            client_id="H1",
            round_id="R001",
            num_examples=0,
            submitted_at=now(),
            integrity=UpdateIntegrity(
                artifact_hash="abc123",
            ),
            provenance=UpdateProvenance(
                client_id="H1",
                round_id="R001",
                created_at=now(),
            ),
        )


# ---------------------------------------------------------------------------
# Detection tests
# ---------------------------------------------------------------------------


def make_detection() -> DetectionResult:
    """Create a valid detection result for testing."""

    return DetectionResult(
        update_id="U001",
        client_id="H3",
        round_id="R001",
        started_at=now(),
        evidence=DetectionEvidence(),
        decision=DetectionDecision(
            risk_score=78,
            confidence=0.63,
            threat_level=ThreatLevel.HIGH,
            threat_hypothesis=ThreatHypothesis.BACKDOOR,
            status=DetectionStatus.REVIEW,
            recommended_action=Action.REVIEW,
            reason="Multiple independent signals require investigation.",
        ),
    )


def test_detection_valid() -> None:
    detection = make_detection()

    assert detection.update_id == "U001"
    assert detection.client_id == "H3"
    assert detection.decision.risk_score == 78
    assert detection.decision.confidence == 0.63
    assert detection.decision.threat_hypothesis == ThreatHypothesis.BACKDOOR


def test_detection_rejects_invalid_risk_score() -> None:
    with pytest.raises(ValidationError):
        DetectionDecision(
            risk_score=101,
            confidence=0.63,
            threat_level=ThreatLevel.HIGH,
            threat_hypothesis=ThreatHypothesis.BACKDOOR,
            status=DetectionStatus.REVIEW,
            recommended_action=Action.REVIEW,
        )


def test_detection_rejects_invalid_confidence() -> None:
    with pytest.raises(ValidationError):
        DetectionDecision(
            risk_score=78,
            confidence=1.5,
            threat_level=ThreatLevel.HIGH,
            threat_hypothesis=ThreatHypothesis.BACKDOOR,
            status=DetectionStatus.REVIEW,
            recommended_action=Action.REVIEW,
        )


# ---------------------------------------------------------------------------
# Event tests
# ---------------------------------------------------------------------------


def test_security_event_valid() -> None:
    event = SecurityEvent(
        event_id="E001",
        event_type=EventType.ANOMALY_DETECTED,
        timestamp=now(),
        round_id="R001",
        client_id="H3",
        update_id="U001",
        threat_level=ThreatLevel.HIGH,
        message="Anomalous update detected.",
        payload={
            "anomaly_score": 87.4,
        },
    )

    assert event.event_type == EventType.ANOMALY_DETECTED
    assert event.client_id == "H3"
    assert event.payload["anomaly_score"] == 87.4


# ---------------------------------------------------------------------------
# Round tests
# ---------------------------------------------------------------------------


def test_round_valid() -> None:
    round_response = RoundResponse(
        round_id="R001",
        status=RoundStatus.RUNNING,
        target_clients=20,
        created_at=now(),
    )

    assert round_response.round_id == "R001"
    assert round_response.status == RoundStatus.RUNNING
    assert round_response.target_clients == 20


def test_round_rejects_zero_clients() -> None:
    with pytest.raises(ValidationError):
        RoundResponse(
            round_id="R001",
            status=RoundStatus.RUNNING,
            target_clients=0,
            created_at=now(),
        )


# ---------------------------------------------------------------------------
# Incident tests
# ---------------------------------------------------------------------------


def test_incident_valid() -> None:
    incident = IncidentResponse(
        incident_id="INC001",
        title="Potential targeted model poisoning",
        threat_level=ThreatLevel.HIGH,
        threat_hypothesis=ThreatHypothesis.BACKDOOR,
        created_at=now(),
        updated_at=now(),
        risk_score=84,
        confidence=0.71,
        recommended_action=Action.QUARANTINE,
    )

    assert incident.incident_id == "INC001"
    assert incident.risk_score == 84
    assert incident.recommended_action == Action.QUARANTINE


# ---------------------------------------------------------------------------
# Security / schema behavior
# ---------------------------------------------------------------------------


def test_extra_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(
            client_id="H1",
            name="Hospital 1",
            unexpected_field="should_fail",
        )