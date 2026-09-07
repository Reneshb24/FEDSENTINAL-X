"""
FedSentinel application configuration.

Configuration is loaded from environment variables when provided, with
safe development defaults for the local prototype.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide runtime configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -----------------------------------------------------------------------
    # Application
    # -----------------------------------------------------------------------

    app_name: str = "FedSentinel"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    # -----------------------------------------------------------------------
    # API
    # -----------------------------------------------------------------------

    api_prefix: str = "/api"
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)

    # -----------------------------------------------------------------------
    # Database
    # -----------------------------------------------------------------------

    database_url: str = "sqlite:///./fedsentinel.db"

    # -----------------------------------------------------------------------
    # Federation
    # -----------------------------------------------------------------------

    client_count: int = Field(default=20, ge=1)
    min_clients_for_round: int = Field(default=5, ge=1)

    local_epochs: int = Field(default=1, ge=1)
    batch_size: int = Field(default=32, ge=1)
    learning_rate: float = Field(default=0.001, gt=0)

    # -----------------------------------------------------------------------
    # Detection thresholds
    # -----------------------------------------------------------------------

    review_threshold: float = Field(default=40.0, ge=0.0, le=100.0)
    suspicious_threshold: float = Field(default=65.0, ge=0.0, le=100.0)
    quarantine_threshold: float = Field(default=80.0, ge=0.0, le=100.0)

    # -----------------------------------------------------------------------
    # Artifact security
    # -----------------------------------------------------------------------

    max_artifact_size_mb: int = Field(default=100, ge=1)

    # -----------------------------------------------------------------------
    # WebSocket
    # -----------------------------------------------------------------------

    websocket_heartbeat_seconds: int = Field(default=30, ge=5)

    # -----------------------------------------------------------------------
    # Demo
    # -----------------------------------------------------------------------

    demo_mode: bool = True
    demo_client_count: int = Field(default=20, ge=1)
    demo_dataset: str = "MNIST"

    @property
    def max_artifact_size_bytes(self) -> int:
        """Return the configured artifact limit in bytes."""

        return self.max_artifact_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """
    Return the cached application settings instance.

    Caching ensures the application uses one consistent configuration
    object during its lifetime.
    """

    return Settings()