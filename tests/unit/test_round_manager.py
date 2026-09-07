from __future__ import annotations

import pytest

from backend.core.types import RoundStatus
from backend.services.round_manager import RoundManager


def test_create_round() -> None:
    manager = RoundManager()

    round_state = manager.create_round(
        round_id="round-001",
        target_clients=20,
    )

    assert round_state.round_id == "round-001"
    assert round_state.target_clients == 20
    assert round_state.status == RoundStatus.CREATED
    assert round_state.started_at is None
    assert round_state.completed_at is None


def test_get_round() -> None:
    manager = RoundManager()

    manager.create_round(
        round_id="round-001",
        target_clients=20,
    )

    round_state = manager.get_round("round-001")

    assert round_state.round_id == "round-001"


def test_duplicate_round_rejected() -> None:
    manager = RoundManager()

    manager.create_round(
        round_id="round-001",
        target_clients=20,
    )

    with pytest.raises(ValueError):
        manager.create_round(
            round_id="round-001",
            target_clients=20,
        )


def test_invalid_target_clients_rejected() -> None:
    manager = RoundManager()

    with pytest.raises(ValueError):
        manager.create_round(
            round_id="round-001",
            target_clients=0,
        )


def test_missing_round_rejected() -> None:
    manager = RoundManager()

    with pytest.raises(KeyError):
        manager.get_round("does-not-exist")


def test_list_rounds() -> None:
    manager = RoundManager()

    manager.create_round(
        round_id="round-001",
        target_clients=20,
    )

    manager.create_round(
        round_id="round-002",
        target_clients=20,
    )

    rounds = manager.list_rounds()

    assert len(rounds) == 2
    assert rounds[0].round_id == "round-001"
    assert rounds[1].round_id == "round-002"


def test_latest_round() -> None:
    manager = RoundManager()

    assert manager.latest_round() is None

    manager.create_round(
        round_id="round-001",
        target_clients=20,
    )

    manager.create_round(
        round_id="round-002",
        target_clients=20,
    )

    latest = manager.latest_round()

    assert latest is not None
    assert latest.round_id == "round-002"


def test_clear() -> None:
    manager = RoundManager()

    manager.create_round(
        round_id="round-001",
        target_clients=20,
    )

    assert len(manager.list_rounds()) == 1

    manager.clear()

    assert len(manager.list_rounds()) == 0