from enum import Enum


class ClientStatus(str, Enum):
    """Current operational status of a federated client."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEGRADED = "DEGRADED"
    QUARANTINED = "QUARANTINED"


class ThreatLevel(str, Enum):
    """Severity assigned to a detected security concern."""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DetectionStatus(str, Enum):
    """Outcome of the security detection pipeline."""

    CLEAN = "CLEAN"
    REVIEW = "REVIEW"
    SUSPICIOUS = "SUSPICIOUS"
    CONFIRMED = "CONFIRMED"


class TrustStatus(str, Enum):
    """Operational trust state assigned to a client."""

    TRUSTED = "TRUSTED"
    REVIEW = "REVIEW"
    SUSPICIOUS = "SUSPICIOUS"
    QUARANTINED = "QUARANTINED"


class Action(str, Enum):
    """Recommended security action."""

    ALLOW = "ALLOW"
    MONITOR = "MONITOR"
    REVIEW = "REVIEW"
    QUARANTINE = "QUARANTINE"
    BLOCK = "BLOCK"


class RoundStatus(str, Enum):
    """Lifecycle state of a federated learning round."""

    CREATED = "CREATED"
    RUNNING = "RUNNING"
    DETECTING = "DETECTING"
    AGGREGATING = "AGGREGATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EventType(str, Enum):
    """Realtime events emitted by the FedSentinel pipeline."""

    ROUND_STARTED = "ROUND_STARTED"
    CLIENT_UPDATE_RECEIVED = "CLIENT_UPDATE_RECEIVED"
    INTEGRITY_CHECKED = "INTEGRITY_CHECKED"
    FINGERPRINT_GENERATED = "FINGERPRINT_GENERATED"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"
    UPDATE_QUARANTINED = "UPDATE_QUARANTINED"
    INFLUENCE_TEST_STARTED = "INFLUENCE_TEST_STARTED"
    INFLUENCE_TEST_COMPLETED = "INFLUENCE_TEST_COMPLETED"
    COUNTERFACTUAL_TEST_STARTED = "COUNTERFACTUAL_TEST_STARTED"
    COUNTERFACTUAL_TEST_COMPLETED = "COUNTERFACTUAL_TEST_COMPLETED"
    ATTRIBUTION_UPDATED = "ATTRIBUTION_UPDATED"
    TRUST_UPDATED = "TRUST_UPDATED"
    AGGREGATION_STARTED = "AGGREGATION_STARTED"
    AGGREGATION_COMPLETED = "AGGREGATION_COMPLETED"
    INCIDENT_CREATED = "INCIDENT_CREATED"
    GLOBAL_MODEL_SECURED = "GLOBAL_MODEL_SECURED"


class ThreatHypothesis(str, Enum):
    """Security hypothesis explaining why an update may be risky."""

    NONE = "NONE"
    ANOMALOUS_UPDATE = "ANOMALOUS_UPDATE"
    DATA_POISONING = "DATA_POISONING"
    LABEL_POISONING = "LABEL_POISONING"
    BACKDOOR = "BACKDOOR"
    MODEL_POISONING = "MODEL_POISONING"
    COLLUSION = "COLLUSION"
    REPLAY = "REPLAY"
    INTEGRITY_VIOLATION = "INTEGRITY_VIOLATION"
    UNKNOWN = "UNKNOWN"