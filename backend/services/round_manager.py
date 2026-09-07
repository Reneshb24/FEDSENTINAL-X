"""
FedSentinel round orchestration.

The RoundManager owns the lifecycle of a federated security round.

Responsibilities:
    - create a round
    - track round status
    - execute the existing SecurityPipeline
    - expose the completed round result
    - keep orchestration separate from security-layer logic

Important:
    Security detection logic remains inside SecurityPipeline and the
    individual L0-L5 components. RoundManager only coordinates them.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from backend.core.types import RoundStatus
from backend.models.model_utils import StateDict
from backend.models.update import ModelUpdate
from backend.services.security_pipeline import (
    SecurityPipeline,
    SecurityRoundResult,
)


@dataclass
class ManagedRound:
    """
    Runtime state for one federated security round.
    """

    round_id: str
    status: RoundStatus
    target_clients: int

    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    result: SecurityRoundResult | None = None
    error: str | None = None


class RoundManager:
    """
    Manage the lifecycle of FedSentinel security rounds.

    This class does not implement detection algorithms.

    It delegates security analysis to SecurityPipeline.
    """

    def __init__(
        self,
        *,
        pipeline: SecurityPipeline | None = None,
    ) -> None:
        self.pipeline = (
            pipeline
            if pipeline is not None
            else SecurityPipeline()
        )

        self._rounds: dict[str, ManagedRound] = {}

    # ---------------------------------------------------------
    # Round creation
    # ---------------------------------------------------------

    def create_round(
        self,
        *,
        round_id: str,
        target_clients: int,
    ) -> ManagedRound:
        """
        Create a new security round.

        A round starts in CREATED state.
        """

        if not round_id:
            raise ValueError("round_id cannot be empty.")

        if target_clients <= 0:
            raise ValueError(
                "target_clients must be greater than zero."
            )

        if round_id in self._rounds:
            raise ValueError(
                f"Round '{round_id}' already exists."
            )

        now = datetime.now(timezone.utc)

        managed_round = ManagedRound(
            round_id=round_id,
            status=RoundStatus.CREATED,
            target_clients=target_clients,
            created_at=now,
        )

        self._rounds[round_id] = managed_round

        return managed_round

    # ---------------------------------------------------------
    # Round lookup
    # ---------------------------------------------------------

    def get_round(
        self,
        round_id: str,
    ) -> ManagedRound:
        """
        Return an existing round.

        Raises:
            KeyError: if the round does not exist.
        """

        try:
            return self._rounds[round_id]
        except KeyError:
            raise KeyError(
                f"Round '{round_id}' does not exist."
            ) from None

    # ---------------------------------------------------------
    # Round execution
    # ---------------------------------------------------------

    def execute_round(
        self,
        *,
        round_id: str,
        updates: list[ModelUpdate],
        global_state: StateDict,
        model_factory: Any,
        validation_loader: Any,
        device: str = "cpu",
    ) -> SecurityRoundResult:
        """
        Execute the complete security pipeline for a round.

        Lifecycle:

            CREATED
                ↓
            RUNNING
                ↓
            DETECTING
                ↓
            AGGREGATING
                ↓
            COMPLETED

        If execution fails:

            FAILED
        """

        managed_round = self.get_round(round_id)

        if managed_round.status not in (
            RoundStatus.CREATED,
        ):
            raise RuntimeError(
                f"Round '{round_id}' cannot be executed from "
                f"status {managed_round.status.value}."
            )

        if not updates:
            raise ValueError(
                "Cannot execute a round without updates."
            )

        managed_round.status = RoundStatus.RUNNING
        managed_round.started_at = datetime.now(timezone.utc)

        try:
            # -------------------------------------------------
            # Detection / security pipeline
            # -------------------------------------------------

            managed_round.status = RoundStatus.DETECTING

            result = self.pipeline.process_round(
                round_id=round_id,
                updates=updates,
                global_state=global_state,
                model_factory=model_factory,
                validation_loader=validation_loader,
                device=device,
            )

            # -------------------------------------------------
            # Aggregation completed by SecurityPipeline.
            # -------------------------------------------------

            managed_round.status = RoundStatus.AGGREGATING

            managed_round.result = result
            managed_round.completed_at = datetime.now(timezone.utc)

            managed_round.status = RoundStatus.COMPLETED

            return result

        except Exception as exc:
            managed_round.status = RoundStatus.FAILED
            managed_round.error = str(exc)
            managed_round.completed_at = datetime.now(timezone.utc)

            raise

    # ---------------------------------------------------------
    # Convenience state methods
    # ---------------------------------------------------------

    def list_rounds(self) -> list[ManagedRound]:
        """
        Return all rounds ordered by creation time.
        """

        return sorted(
            self._rounds.values(),
            key=lambda item: item.created_at,
        )

    def latest_round(self) -> ManagedRound | None:
        """
        Return the most recently created round.
        """

        rounds = self.list_rounds()

        if not rounds:
            return None

        return rounds[-1]

    def clear(self) -> None:
        """
        Clear in-memory round state.

        Useful for tests and local development.
        """

        self._rounds.clear()