from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.services.round_management_service import RoundManagementService
from backend.storage.database import Base
from backend.storage.models import Federation, FederationRound, User


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(
        email="admin@fedsentinel.io",
        password_hash="test",
        role="SUPER_ADMIN",
    )
    session.add(user)

    federation = Federation(
        id="fed-test-01",
        name="Test Federation",
        description="Testing",
        status="ACTIVE",
    )
    session.add(federation)
    session.commit()

    yield session

    session.close()


def test_cancel_created_round(db_session):
    admin = db_session.query(User).first()
    round_ = FederationRound(
        federation_id="fed-test-01",
        round_number=1,
        status="CREATED",
        participating_clients=2,
        config_json="{}",
    )
    db_session.add(round_)
    db_session.commit()

    cancelled = RoundManagementService.mark_cancelled(
        db_session,
        round_,
        actor_user_id=admin.id,
        reason="Test cancel",
    )
    assert cancelled.status == "CANCELLED"
    assert cancelled.completed_at is not None


def test_cancel_running_round(db_session):
    admin = db_session.query(User).first()
    round_ = FederationRound(
        federation_id="fed-test-01",
        round_number=1,
        status="RUNNING",
        participating_clients=2,
        config_json="{}",
    )
    db_session.add(round_)
    db_session.commit()

    cancelled = RoundManagementService.mark_cancelled(
        db_session,
        round_,
        actor_user_id=admin.id,
        reason="Admin cancelled running round",
    )
    assert cancelled.status == "CANCELLED"
    assert cancelled.completed_at is not None


def test_cannot_cancel_completed_round(db_session):
    admin = db_session.query(User).first()
    round_ = FederationRound(
        federation_id="fed-test-01",
        round_number=1,
        status="COMPLETED",
        participating_clients=2,
        config_json="{}",
    )
    db_session.add(round_)
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        RoundManagementService.mark_cancelled(
            db_session,
            round_,
            actor_user_id=admin.id,
            reason="Test",
        )
    assert exc.value.status_code == 409


def test_mark_failed(db_session):
    admin = db_session.query(User).first()
    round_ = FederationRound(
        federation_id="fed-test-01",
        round_number=1,
        status="RUNNING",
        participating_clients=2,
        config_json="{}",
    )
    db_session.add(round_)
    db_session.commit()

    failed = RoundManagementService.mark_failed(
        db_session,
        round_,
        actor_user_id=admin.id,
        reason="Execution failed due to error",
    )
    assert failed.status == "FAILED"
    assert failed.completed_at is not None
