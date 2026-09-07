from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from torch import Tensor, nn
from torch.utils.data import DataLoader

from backend.aggregation.fedavg import fedavg
from backend.models.model_utils import apply_model_delta
from backend.models.update import ModelUpdate

from .evaluator import EvaluationResult, evaluate_model


@dataclass(frozen=True)
class CounterfactualResult:
    """Comparison between models with and without one client update."""

    client_id: str
    with_client: EvaluationResult
    without_client: EvaluationResult

    accuracy_delta: float
    loss_delta: float

    improvement_without_client: bool
    harmful_counterfactual: bool

    reason: str


def _build_model(
    model_factory,
    global_state: Mapping[str, Tensor],
    delta: Mapping[str, Tensor],
    device: str,
) -> nn.Module:
    """Create a model after applying an aggregated update."""
    updated_state = apply_model_delta(
        global_state,
        delta,
    )

    model = model_factory()
    model.load_state_dict(
        updated_state,
        strict=True,
    )

    return model.to(device)


class CounterfactualAnalyzer:
    """
    Analyze the effect of allowing versus suppressing each client update.

    This layer produces security evidence only.
    It does not declare a client malicious.
    """

    def __init__(
        self,
        model_factory,
        validation_loader: DataLoader,
        device: str = "cpu",
    ) -> None:
        self.model_factory = model_factory
        self.validation_loader = validation_loader
        self.device = device

    def analyze_client(
        self,
        global_state: Mapping[str, Tensor],
        updates: list[ModelUpdate],
        client_id: str,
    ) -> CounterfactualResult:
        """
        Compare the aggregated model with and without one client.
        """
        if not updates:
            raise ValueError("Updates cannot be empty.")

        target_updates = [
            update
            for update in updates
            if update.client_id == client_id
        ]

        if len(target_updates) != 1:
            raise ValueError(
                f"Expected exactly one update for client {client_id}, "
                f"found {len(target_updates)}."
            )

        # ---------------------------------------------------------
        # MODEL WITH CLIENT
        # ---------------------------------------------------------
        full_delta = fedavg(updates)

        model_with = _build_model(
            self.model_factory,
            global_state,
            full_delta,
            self.device,
        )

        metrics_with = evaluate_model(
            model_with,
            self.validation_loader,
            self.device,
        )

        # ---------------------------------------------------------
        # MODEL WITHOUT CLIENT
        # ---------------------------------------------------------
        remaining_updates = [
            update
            for update in updates
            if update.client_id != client_id
        ]

        if remaining_updates:
            reduced_delta = fedavg(remaining_updates)

            model_without = _build_model(
                self.model_factory,
                global_state,
                reduced_delta,
                self.device,
            )

            metrics_without = evaluate_model(
                model_without,
                self.validation_loader,
                self.device,
            )

        else:
            # With only one client, removing it means evaluating
            # the original global model.
            model_without = self.model_factory()
            model_without.load_state_dict(
                global_state,
                strict=True,
            )
            model_without = model_without.to(self.device)

            metrics_without = evaluate_model(
                model_without,
                self.validation_loader,
                self.device,
            )

        # ---------------------------------------------------------
        # COUNTERFACTUAL EVIDENCE
        # ---------------------------------------------------------

        # Positive means removing the client improved accuracy.
        accuracy_delta = (
            metrics_without.accuracy
            - metrics_with.accuracy
        )

        # Negative means removing the client reduced loss.
        loss_delta = (
            metrics_without.average_loss
            - metrics_with.average_loss
        )

        improvement_without_client = accuracy_delta > 0

        # Stronger evidence when both metrics improve after removal.
        harmful_counterfactual = (
            accuracy_delta > 0
            and loss_delta < 0
        )

        if harmful_counterfactual:
            reason = (
                "Removing this client improves validation accuracy "
                "and reduces validation loss."
            )

        elif improvement_without_client:
            reason = (
                "Removing this client improves validation accuracy, "
                "but loss evidence is mixed."
            )

        elif accuracy_delta < 0:
            reason = (
                "Removing this client reduces validation accuracy; "
                "the contribution appears beneficial under this test."
            )

        else:
            reason = (
                "Removing this client produces no measurable "
                "accuracy change."
            )

        return CounterfactualResult(
            client_id=client_id,
            with_client=metrics_with,
            without_client=metrics_without,
            accuracy_delta=accuracy_delta,
            loss_delta=loss_delta,
            improvement_without_client=improvement_without_client,
            harmful_counterfactual=harmful_counterfactual,
            reason=reason,
        )

    def analyze(
        self,
        global_state: Mapping[str, Tensor],
        updates: list[ModelUpdate],
    ) -> dict[str, CounterfactualResult]:
        """Run counterfactual analysis for every client."""
        if not updates:
            raise ValueError("Updates cannot be empty.")

        client_ids = [
            update.client_id
            for update in updates
        ]

        if len(client_ids) != len(set(client_ids)):
            raise ValueError(
                "Each client must have exactly one update."
            )

        return {
            client_id: self.analyze_client(
                global_state,
                updates,
                client_id,
            )
            for client_id in client_ids
        }
