"""
FedSentinel end-to-end security pipeline.

Orchestrates:
    Federation
        -> L0
        -> L1
        -> L2
        -> Quarantine
        -> Robust aggregation
        -> L3
        -> L4
        -> L5
        -> Trust Engine

The pipeline coordinates existing validated components.
It does not replace their detection logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from backend.aggregation.fedavg import fedavg
from backend.aggregation.quarantine import QuarantineManager
from backend.layers.layer1_fingerprint import FingerprintGenerator
from backend.layers.layer2_anomaly import Layer2Detector
from backend.layers.layer3_influence import InfluenceAnalyzer
from backend.layers.layer4_counterfactual import CounterfactualAnalyzer
from backend.layers.layer5_attribution import (
    AttributionEngine,
    AttributionEvidence,
)
from backend.models.model_utils import (
    StateDict,
    apply_model_delta,
)
from backend.models.update import ModelUpdate
from backend.security.artifact_validator import ArtifactValidator
from backend.trust.engine import TrustEngine
from backend.trust.evidence import TrustEvidence


@dataclass
class ClientSecurityResult:
    """Security evidence and decision for one client update."""

    client_id: str
    update_id: str

    layer0_passed: bool = False
    layer0_forensic_eligible: bool = False
    fingerprint: Any | None = None
    layer2: Any | None = None
    layer3: Any | None = None
    layer4: Any | None = None
    layer5: Any | None = None
    trust: Any | None = None

    quarantined: bool = False
    evidence_items: list[str] = field(default_factory=list)


@dataclass
class SecurityRoundResult:
    """Complete result produced by one security pipeline execution."""

    round_id: str
    started_at: datetime
    completed_at: datetime

    total_updates: int
    accepted_updates: list[ModelUpdate]
    quarantined_updates: list[ModelUpdate]

    client_results: dict[str, ClientSecurityResult]

    global_state: StateDict | None = None

    incident_required: bool = False


class SecurityPipeline:
    """
    Coordinate the complete FedSentinel security workflow.

    Important:
        This class is an orchestrator. Individual security layers remain
        independently responsible for their own evidence generation.
    """

    def __init__(
        self,
        *,
        artifact_validator: ArtifactValidator | None = None,
        fingerprint_generator: FingerprintGenerator | None = None,
        layer2_detector: Layer2Detector | None = None,
        quarantine_manager: QuarantineManager | None = None,
        trust_engine: TrustEngine | None = None,
    ) -> None:

        self.artifact_validator = (
            artifact_validator
            if artifact_validator is not None
            else ArtifactValidator()
        )

        self.fingerprint_generator = (
            fingerprint_generator
            if fingerprint_generator is not None
            else FingerprintGenerator()
        )

        self.layer2_detector = (
            layer2_detector
            if layer2_detector is not None
            else Layer2Detector()
        )

        self.quarantine_manager = (
            quarantine_manager
            if quarantine_manager is not None
            else QuarantineManager()
        )

        self.trust_engine = (
            trust_engine
            if trust_engine is not None
            else TrustEngine()
        )

    # ---------------------------------------------------------
    # L0 + L1
    # ---------------------------------------------------------

    def _validate_and_fingerprint(
        self,
        updates: list[ModelUpdate],
    ) -> dict[str, ClientSecurityResult]:

        results: dict[str, ClientSecurityResult] = {}

        for update in updates:
            result = ClientSecurityResult(
                client_id=update.client_id,
                update_id=update.update_id,
            )

            result.layer0_forensic_eligible = False

            # L0 validation.
            try:
                validation = self.artifact_validator.validate(
                    update
                )

                result.layer0_passed = validation.passed

                if validation.passed:
                    result.evidence_items.append(
                        "L0 artifact validation passed."
                    )
                else:
                    result.evidence_items.append(
                        f"L0 validation failed: {validation.reason}"
                    )

            except Exception as exc:
                result.layer0_passed = False
                result.evidence_items.append(
                    f"L0 validation error: {exc}"
                )

                # If validation itself fails, the update cannot safely
                # continue into forensic analysis.
                results[update.client_id] = result
                continue

            # L0 may reject an update because its norm exceeds the
            # configured bound. That is important security evidence,
            # but the update remains structurally analyzable.
            #
            # Truly unsafe artifacts (malformed structure, non-finite
            # values, invalid parameter count, or duplicate replay)
            # must not proceed to behavioral analysis.

            forensic_eligible = (
                validation.parameter_structure_valid
                and validation.finite_values_valid
                and not validation.duplicate_detected
                and validation.integrity_verified
            )

            result.layer0_forensic_eligible = forensic_eligible

            if forensic_eligible:
                result.fingerprint = (
                    self.fingerprint_generator.generate(update)
                )

                result.evidence_items.append(
                    "L1 privacy-safe fingerprint generated."
                )

                if not validation.passed:
                    result.evidence_items.append(
                        "L0 policy warning retained as forensic evidence."
                    )

            results[update.client_id] = result

        return results

    # ---------------------------------------------------------
    # Public pipeline
    # ---------------------------------------------------------

    def process_round(
        self,
        *,
        round_id: str,
        updates: list[ModelUpdate],
        global_state: StateDict,
        model_factory: Any,
        validation_loader: Any,
        device: str = "cpu",
    ) -> SecurityRoundResult:

        started_at = datetime.now(timezone.utc)

        if not updates:
            raise ValueError(
                "Security pipeline requires at least one update."
            )

        # -----------------------------------------------------
        # L0 + L1
        # -----------------------------------------------------

        results = self._validate_and_fingerprint(updates)

        # These updates are safe enough for independent forensic
        # analysis. They are NOT automatically accepted for aggregation.
        forensic_updates = [
            update
            for update in updates
            if results[update.client_id].layer0_forensic_eligible
        ]

        # -----------------------------------------------------
        # L2
        # -----------------------------------------------------

        fingerprints = {
            client_id: result.fingerprint.vector
            for client_id, result in results.items()
            if result.fingerprint is not None
        }

        if fingerprints:
            layer2_result = self.layer2_detector.detect_round(
                fingerprints
            )

            for client_id, detection in layer2_result.detections.items():
                if client_id not in results:
                    continue

                results[client_id].layer2 = detection

                results[client_id].evidence_items.append(
                    f"L2 anomaly score: {detection.anomaly_score:.2f}"
                )

        # -----------------------------------------------------
        # Quarantine L2 outliers
        # -----------------------------------------------------

        quarantined: list[ModelUpdate] = []
        accepted: list[ModelUpdate] = []

        for update in forensic_updates:
            result = results[update.client_id]

            if (
                result.layer2 is not None
                and result.layer2.is_outlier
            ):
                quarantined.append(update)

                result.quarantined = True

                results[update.client_id].evidence_items.append(
                    "L2 outlier quarantined before aggregation."
                )

            else:
                accepted.append(update)

        # -----------------------------------------------------
        # Safe aggregation
        # -----------------------------------------------------

        if not accepted:
            raise RuntimeError(
                "No valid updates remain after security filtering."
            )

        # FedAvg returns an aggregated MODEL DELTA.
        aggregated_delta = fedavg(accepted)

        # Convert the aggregated delta into the actual next
        # global model state.
        new_global_state = apply_model_delta(
            global_state,
            aggregated_delta,
        )

        # -----------------------------------------------------
        # L3
        # -----------------------------------------------------

        influence_analyzer = InfluenceAnalyzer(
            model_factory=model_factory,
            validation_loader=validation_loader,
            device=device,
        )

        influence_result = influence_analyzer.analyze(
            global_state=global_state,
            updates=forensic_updates,
        )

        for influence in influence_result:
            client_id = influence.client_id

            if client_id in results:
                results[client_id].layer3 = influence

                results[client_id].evidence_items.append(
                    f"L3 influence: {influence.influence_score:+.2f}"
                )

        # -----------------------------------------------------
        # L4
        # -----------------------------------------------------

        counterfactual_analyzer = CounterfactualAnalyzer(
            model_factory=model_factory,
            validation_loader=validation_loader,
            device=device,
        )

        counterfactual_results = counterfactual_analyzer.analyze(
            global_state=global_state,
            updates=forensic_updates,
        )

        for client_id, counterfactual in counterfactual_results.items():
            if client_id in results:
                results[client_id].layer4 = counterfactual

                results[client_id].evidence_items.append(
                    "L4 counterfactual analysis completed."
                )

        # -----------------------------------------------------
        # L5 + Trust
        # -----------------------------------------------------

        for update in updates:
            result = results[update.client_id]

            layer2 = result.layer2
            layer3 = result.layer3
            layer4 = result.layer4

            attribution_evidence = AttributionEvidence(
                client_id=update.client_id,

                anomaly_score=(
                    layer2.anomaly_score
                    if layer2 is not None
                    else None
                ),

                anomaly_z_score=(
                    layer2.z_score
                    if layer2 is not None
                    else None
                ),

                peer_similarity=(
                    layer2.peer_similarity
                    if layer2 is not None
                    else None
                ),

                influence_score=(
                    layer3.influence_score
                    if layer3 is not None
                    else None
                ),

                validation_delta=(
                    layer3.validation_delta
                    if layer3 is not None
                    else None
                ),

                harmful_influence=(
                    layer3.harmful_influence
                    if layer3 is not None
                    else None
                ),

                counterfactual_accuracy_delta=(
                    layer4.accuracy_delta
                    if layer4 is not None
                    else None
                ),

                counterfactual_loss_delta=(
                    layer4.loss_delta
                    if layer4 is not None
                    else None
                ),

                harmful_counterfactual=(
                    layer4.harmful_counterfactual
                    if layer4 is not None
                    else None
                ),
            )

            attribution = AttributionEngine().attribute(
                attribution_evidence
            )

            result.layer5 = attribution

            trust_evidence = TrustEvidence(
                client_id=update.client_id,

                anomaly_score=(
                    layer2.anomaly_score
                    if layer2 is not None
                    else 0.0
                ),

                anomaly_z_score=(
                    layer2.z_score
                    if layer2 is not None
                    else 0.0
                ),

                is_anomaly_outlier=(
                    layer2.is_outlier
                    if layer2 is not None
                    else False
                ),

                peer_similarity=(
                    layer2.peer_similarity
                    if layer2 is not None
                    else 0.0
                ),

                influence_score=(
                    layer3.influence_score
                    if layer3 is not None
                    else 0.0
                ),

                harmful_influence=(
                    layer3.harmful_influence
                    if layer3 is not None
                    else False
                ),

                validation_delta=(
                    layer3.validation_delta
                    if layer3 is not None
                    else 0.0
                ),

                counterfactual_accuracy_delta=(
                    layer4.accuracy_delta
                    if layer4 is not None
                    else 0.0
                ),

                counterfactual_loss_delta=(
                    layer4.loss_delta
                    if layer4 is not None
                    else 0.0
                ),

                harmful_counterfactual=(
                    layer4.harmful_counterfactual
                    if layer4 is not None
                    else False
                ),

                attribution_score=attribution.evidence_score,

                hypothesis=attribution.hypothesis,

                attribution_confidence=attribution.confidence,
            )

            result.trust = self.trust_engine.evaluate(
                trust_evidence
            )

            if result.trust.action.value == "QUARANTINE":
                result.quarantined = True

        completed_at = datetime.now(timezone.utc)

        incident_required = any(
            result.quarantined
            for result in results.values()
        )

        return SecurityRoundResult(
            round_id=round_id,
            started_at=started_at,
            completed_at=completed_at,
            total_updates=len(updates),
            accepted_updates=accepted,
            quarantined_updates=quarantined,
            client_results=results,

            # This is now the ACTUAL new global model state,
            # rather than the raw aggregated delta.
            global_state=new_global_state,

            incident_required=incident_required,
        )