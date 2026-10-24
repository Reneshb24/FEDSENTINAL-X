from __future__ import annotations

from sqlalchemy.orm import Session

from backend.services.model_artifact_service import ModelArtifactService
from backend.storage.models import Federation, Model, ModelVersion


class GlobalModelService:
    """
    Resolve and securely load the latest validated global model
    associated with a federation.
    """

    def __init__(
        self,
        artifact_service: ModelArtifactService | None = None,
    ) -> None:

        self.artifact_service = (
            artifact_service
            if artifact_service is not None
            else ModelArtifactService()
        )

    @staticmethod
    def get_model(
        db: Session,
        *,
        federation: Federation,
    ) -> Model:

        model = (
            db.query(Model)
            .filter(
                Model.name == federation.model_name,
                Model.is_active.is_(True),
            )
            .first()
        )

        if model is None:
            raise ValueError(
                f"No active model is registered for federation "
                f"'{federation.name}'."
            )

        return model

    @staticmethod
    def get_latest_version(
        db: Session,
        *,
        model: Model,
    ) -> ModelVersion:

        version = (
            db.query(ModelVersion)
            .filter(
                ModelVersion.model_id == model.id,
                ModelVersion.security_status == "VALIDATED",
            )
            .order_by(
                ModelVersion.created_at.desc()
            )
            .first()
        )

        if version is None:
            raise ValueError(
                f"No validated model version exists for "
                f"model '{model.name}'."
            )

        return version

    def load_latest_verified(
        self,
        db: Session,
        *,
        federation: Federation,
    ) -> tuple[ModelVersion, dict]:

        model = self.get_model(
            db,
            federation=federation,
        )

        version = self.get_latest_version(
            db,
            model=model,
        )

        state_dict = self.artifact_service.load_verified(
            model_name=model.name,
            version=version.version,
            expected_hash=version.model_hash,
        )

        return (
            version,
            state_dict,
        )
