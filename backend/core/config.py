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

    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
    )

    # -----------------------------------------------------------------------
    # Database
    # -----------------------------------------------------------------------

    database_url: str = "sqlite:///./fedsentinel.db"

    # -----------------------------------------------------------------------
    # Authentication / JWT
    # -----------------------------------------------------------------------

    jwt_secret_key: str = "fedsentinel-secret-key-change-in-production-f831b2e8a1"

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = Field(
        default=15,
        ge=1,
        le=1440,
    )

    refresh_token_expire_days: int = Field(
        default=7,
        ge=1,
        le=90,
    )

    # -----------------------------------------------------------------------
    # Refresh Token Cookie
    # -----------------------------------------------------------------------

    refresh_cookie_name: str = "fedsentinel_refresh"

    refresh_cookie_secure: bool = False

    refresh_cookie_samesite: str = "lax"

    # -----------------------------------------------------------------------
    # Authentication Protection
    # -----------------------------------------------------------------------

    auth_max_failed_attempts: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    auth_lock_minutes: int = Field(
        default=15,
        ge=1,
        le=1440,
    )

    # -----------------------------------------------------------------------
    # CORS
    # -----------------------------------------------------------------------

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as a list."""

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    # -----------------------------------------------------------------------
    # Federation
    # -----------------------------------------------------------------------

    client_count: int = Field(
        default=20,
        ge=1,
    )

    min_clients_for_round: int = Field(
        default=5,
        ge=1,
    )

    local_epochs: int = Field(
        default=1,
        ge=1,
    )

    batch_size: int = Field(
        default=32,
        ge=1,
    )

    learning_rate: float = Field(
        default=0.001,
        gt=0,
    )

    # -----------------------------------------------------------------------
    # Detection Thresholds
    # -----------------------------------------------------------------------

    review_threshold: float = Field(
        default=40.0,
        ge=0.0,
        le=100.0,
    )

    suspicious_threshold: float = Field(
        default=65.0,
        ge=0.0,
        le=100.0,
    )

    quarantine_threshold: float = Field(
        default=80.0,
        ge=0.0,
        le=100.0,
    )

    # -----------------------------------------------------------------------
    # Artifact Security
    # -----------------------------------------------------------------------

    max_artifact_size_mb: int = Field(
        default=100,
        ge=1,
    )

    @property
    def max_artifact_size_bytes(self) -> int:
        """Return the configured artifact limit in bytes."""

        return (
            self.max_artifact_size_mb
            * 1024
            * 1024
        )

    # -----------------------------------------------------------------------
    # WebSocket
    # -----------------------------------------------------------------------

    websocket_heartbeat_seconds: int = Field(
        default=30,
        ge=5,
    )

    # -----------------------------------------------------------------------
    # Demo
    # -----------------------------------------------------------------------

    demo_mode: bool = True

    demo_client_count: int = Field(
        default=20,
        ge=1,
    )

    demo_dataset: str = "MNIST"


@lru_cache
def get_settings() -> Settings:
    """
    Return the cached application settings instance.
    """

    return Settings()


settings = get_settings()
