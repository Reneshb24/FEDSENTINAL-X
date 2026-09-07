from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.core.types import (
    Action,
    EventType,
    RoundStatus,
    ThreatHypothesis,
    TrustStatus,
)
from backend.models.update import create_model_update
from backend.services.event_manager import EventManager
from backend.services.incident_manager import IncidentManager
from backend.services.round_manager import RoundManager
from backend.services.round_orchestrator import RoundOrchestrator
from backend.services.security_pipeline import (
    ClientSecurityResult,
    SecurityRoundResult,
)


class FakePipeline:
    """
    Lightweight pipeline used to test orchestration.

    This test double verifies that RoundOrchestrator coordinates
    services correctly without rerunning the expensive ML pipeline.
    """

    def process_round(
        self,
        *,
        round_id,
        updates,
        global_state,
        model_factory,
        validation_loader,
        device,
    ):
        result = ClientSecurityResult(
            client_id="H1",
            update_id="update-H1",
            layer0_passed=True,
            layer0_forensic_eligible=True,
            evidence_items=[
                "L0 artifact validation passed.",
                "L1 privacy-safe fingerprint generated.",
            ],
        )

        class Layer2:
            anomaly_score = 90.0
            z_score = 8.0
            peer_similarity = 0.2
            is_outlier = True
            reason = "Strong anomaly."

        class Layer3:
            influence_score = -10.0
            validation_delta = -0.10
            harmful_influence = True

        class Layer4:
            accuracy_delta = 0.10
            loss_delta = -1.0
            harmful_counterfactual = True

        class Layer5:
            hypothesis = ThreatHypothesis.MODEL_POISONING
            confidence = 0.80
            evidence_score = 70.0

        class Trust:
            risk_score = 80.0
            confidence = 0.90
            status = TrustStatus.QUARANTINED
            action = Action.QUARANTINE
            hypothesis = ThreatHypothesis.MODEL_POISONING

        result.layer2 = Layer2()
        result.layer3 = Layer3()
        result.layer4 = Layer4()
        result.layer5 = Layer5()
        result.trust = Trust()
        result.quarantined = True

        now = datetime.now(timezone.utc)

        return SecurityRoundResult(
            round_id=round_id,
            started_at=now,
            completed_at=now,
            total_updates=len(updates),
            accepted_updates=[],
            quarantined_updates=updates,
            client_results={
                "H1": result,
            },
            global_state=global_state,
            incident_required=True,
        )


def make_update() -> object:
    """
    Create a minimal update for orchestration tests.
    """

    import torch
    from collections import OrderedDict

    delta = OrderedDict(
        {
            "weight": torch.tensor(
                [[1.0]],
                dtype=torch.float32,
            ),
        }
    )

    return create_model_update(
        update_id="update-H1",
        client_id="H1",
        round_id="round-001",
        delta=delta,
        num_examples=10,
    )


def test_create_round_emits_event() -> None:
    event_manager = EventManager()

    orchestrator = RoundOrchestrator(
        round_manager=RoundManager(
            pipeline=FakePipeline()
        ),
        incident_manager=IncidentManager(),
        event_manager=event_manager,
    )

    round_state = orchestrator.create_round(
        round_id="round-001",
        target_clients=1,
    )

    assert round_state.status == RoundStatus.CREATED

    events = event_manager.events_for_round(
        "round-001"
    )

    assert len(events) == 1
    assert events[0].event_type == EventType.ROUND_STARTED


def test_execute_round_creates_events_and_incident() -> None:
    event_manager = EventManager()
    incident_manager = IncidentManager()

    orchestrator = RoundOrchestrator(
        round_manager=RoundManager(
            pipeline=FakePipeline()
        ),
        incident_manager=incident_manager,
        event_manager=event_manager,
    )

    orchestrator.create_round(
        round_id="round-001",
        target_clients=1,
    )

    update = make_update()

    result = orchestrator.execute_round(
        round_id="round-001",
        updates=[update],
        global_state={},
        model_factory=lambda: None,
        validation_loader=None,
    )

    assert result.round_id == "round-001"
    assert result.incident_required is True

    round_state = orchestrator.get_round(
        "round-001"
    )

    assert round_state.status == RoundStatus.COMPLETED

    incidents = orchestrator.get_incidents()

    assert len(incidents) == 1
    assert incidents[0].primary_client_id == "H1"

    events = orchestrator.get_events(
        round_id="round-001"
    )

    event_types = [
        event.event_type
        for event in events
    ]

    assert EventType.CLIENT_UPDATE_RECEIVED in event_types
    assert EventType.INTEGRITY_CHECKED in event_types
    assert EventType.ANOMALY_DETECTED in event_types
    assert EventType.UPDATE_QUARANTINED in event_types
    assert EventType.INFLUENCE_TEST_COMPLETED in event_types
    assert (
        EventType.COUNTERFACTUAL_TEST_COMPLETED
        in event_types
    )
    assert EventType.ATTRIBUTION_UPDATED in event_types
    assert EventType.TRUST_UPDATED in event_types
    assert EventType.AGGREGATION_COMPLETED in event_types
    assert EventType.INCIDENT_CREATED in event_types
    assert EventType.GLOBAL_MODEL_SECURED in event_types


def test_events_can_be_filtered_by_client() -> None:
    event_manager = EventManager()

    orchestrator = RoundOrchestrator(
        round_manager=RoundManager(
            pipeline=FakePipeline()
        ),
        incident_manager=IncidentManager(),
        event_manager=event_manager,
    )

    orchestrator.create_round(
        round_id="round-001",
        target_clients=1,
    )

    update = make_update()

    orchestrator.execute_round(
        round_id="round-001",
        updates=[update],
        global_state={},
        model_factory=lambda: None,
        validation_loader=None,
    )

    events = orchestrator.get_events(
        client_id="H1"
    )

    assert len(events) > 0
    assert all(
        event.client_id == "H1"
        for event in events
    )


def test_duplicate_round_execution_rejected() -> None:
    orchestrator = RoundOrchestrator(
        round_manager=RoundManager(
            pipeline=FakePipeline()
        ),
        incident_manager=IncidentManager(),
        event_manager=EventManager(),
    )

    orchestrator.create_round(
        round_id="round-001",
        target_clients=1,
    )

    update = make_update()

    orchestrator.execute_round(
        round_id="round-001",
        updates=[update],
        global_state={},
        model_factory=lambda: None,
        validation_loader=None,
    )

    with pytest.raises(RuntimeError):
        orchestrator.execute_round(
            round_id="round-001",
            updates=[update],
            global_state={},
            model_factory=lambda: None,
            validation_loader=None,
        )


def test_clear() -> None:
    event_manager = EventManager()
    incident_manager = IncidentManager()

    orchestrator = RoundOrchestrator(
        round_manager=RoundManager(
            pipeline=FakePipeline()
        ),
        incident_manager=incident_manager,
        event_manager=event_manager,
    )

    orchestrator.create_round(
        round_id="round-001",
        target_clients=1,
    )

    assert len(orchestrator.get_events()) == 1

    orchestrator.clear()

    assert orchestrator.get_events() == []
    assert orchestrator.get_incidents() == []
    assert orchestrator.round_manager.latest_round() is None