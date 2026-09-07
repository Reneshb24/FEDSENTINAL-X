"""
FedSentinel application exceptions.

Custom exceptions keep error handling consistent across the security
pipeline, services, API layer, and simulation engine.
"""


class FedSentinelError(Exception):
    """Base exception for all FedSentinel application errors."""

    default_message = "An unexpected FedSentinel error occurred."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class ConfigurationError(FedSentinelError):
    """Raised when application configuration is invalid."""

    default_message = "FedSentinel configuration is invalid."


class ValidationError(FedSentinelError):
    """Raised when an artifact, update, or request fails validation."""

    default_message = "Validation failed."


class ArtifactError(FedSentinelError):
    """Raised when a model-update artifact is invalid or unsafe."""

    default_message = "Model update artifact is invalid or unsafe."


class IntegrityError(ArtifactError):
    """Raised when artifact integrity verification fails."""

    default_message = "Artifact integrity verification failed."


class UnsupportedArtifactError(ArtifactError):
    """Raised when an artifact format is not permitted."""

    default_message = "Artifact format is not supported."


class ArtifactTooLargeError(ArtifactError):
    """Raised when an artifact exceeds the configured size limit."""

    default_message = "Artifact exceeds the permitted size limit."


class DetectionError(FedSentinelError):
    """Raised when a security detection layer cannot complete."""

    default_message = "Security detection failed."


class AggregationError(FedSentinelError):
    """Raised when model aggregation cannot safely complete."""

    default_message = "Model aggregation failed."


class QuarantineError(FedSentinelError):
    """Raised when an update cannot be quarantined safely."""

    default_message = "Unable to quarantine the update."


class RoundError(FedSentinelError):
    """Raised when a federation round cannot proceed."""

    default_message = "Federated learning round failed."


class ClientError(FedSentinelError):
    """Raised for invalid client operations."""

    default_message = "Federated client operation failed."


class StorageError(FedSentinelError):
    """Raised when persistence operations fail."""

    default_message = "Storage operation failed."