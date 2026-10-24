from __future__ import annotations

from datetime import datetime, timezone

from backend.services.federation_service import FederationService
from backend.services.round_orchestrator import RoundOrchestrator


class FakeResult:
    def __init__(self, global_state):
        self.global_state = global_state


class FakeManagedRound:
    def __init__(self, global_state):
        self.result = FakeResult(global_state)


class FakeOrchestrator:
    def __init__(self, secured_state):
        self.secured_state = secured_state
        self.execute_called = False

    def execute_round(
        self,
        *,
        round_id,
        updates,
        global_state,
        model_factory,
        validation_loader,
        device,
    ):
        self.execute_called = True

    def get_round(self, round_id):
        return FakeManagedRound(
            self.secured_state
        )


def test_execute_returns_secured_global_state(monkeypatch) -> None:
    """
    FederationService must return the post-security global model.

    The raw FederationEngine state represents the pre-security model.
    The orchestrator result represents the secured model after the
    security pipeline and safe aggregation.
    """

    pre_security_state = {
        "weight": "pre-security"
    }

    secured_state = {
        "weight": "secured"
    }

    orchestrator = FakeOrchestrator(
        secured_state=secured_state
    )

    service = FederationService(
        orchestrator=orchestrator
    )

    class FakeFederationResult:
        global_state = pre_security_state
        updates = []

    class FakeFederationEngine:
        def __init__(self, **kwargs):
            pass

        def run_round(self, round_id):
            return FakeFederationResult()

    monkeypatch.setattr(
        "backend.services.federation_service.load_mnist_train",
        lambda: object(),
    )

    monkeypatch.setattr(
        "backend.services.federation_service.load_mnist_test",
        lambda: object(),
    )

    monkeypatch.setattr(
        "backend.services.federation_service.FederationEngine",
        FakeFederationEngine,
    )

    monkeypatch.setattr(
        "backend.services.federation_service.create_validation_loader",
        lambda **kwargs: object(),
    )

    result = service.execute(
        round_id="round-secured-state",
        inject_attack=False,
    )

    assert orchestrator.execute_called is True
    assert result.global_state is secured_state
    assert result.global_state is not pre_security_state
