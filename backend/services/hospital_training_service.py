"""
Hospital-local federated training service for FedSentinel.

This service connects the hospital dataset-management boundary to the
existing federated training implementation.

Responsibilities:

    1. Locate a registered hospital dataset version.
    2. Safely load the validated NPZ artifact.
    3. Convert the artifact into a PyTorch Dataset.
    4. Create the existing HospitalClient.
    5. Train locally using the existing LocalTrainer.
    6. Produce the existing ModelUpdate representation.

Security decisions are intentionally NOT performed here.

Raw hospital data remains local to this service.
Only the resulting ModelUpdate is intended to cross into the
server-side security pipeline.
"""

from __future__ import annotations

import hashlib
import uuid
from collections import OrderedDict
from pathlib import Path
from typing import Mapping

import numpy as np
import torch
from sqlalchemy.orm import Session
from torch import Tensor
from torch.utils.data import Dataset

from backend.models.cnn import FedSentinelCNN
from backend.models.model_utils import StateDict, clone_state_dict
from backend.models.update import ModelUpdate
from backend.storage.models import Dataset as DatasetModel
from backend.storage.models import DatasetVersion
from backend.services.global_model_service import GlobalModelService
from backend.storage.models import FederationRound
from backend.storage.models import Federation
from clients.client_config import ClientConfig
from clients.hospital_client import HospitalClient


# ============================================================================
# STORAGE CONFIGURATION
# ============================================================================

DATASET_STORAGE_ROOT = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "hospital_datasets"
)


# ============================================================================
# LOCAL NPZ DATASET
# ============================================================================

class HospitalNPZDataset(Dataset):
    """
    PyTorch Dataset backed by a validated hospital-local NPZ artifact.

    The NPZ file is loaded with allow_pickle=False.

    Supported array naming conventions:

        x_train / y_train
        x / y
        images / labels

    The raw arrays remain inside the hospital training process.
    """

    def __init__(
        self,
        path: Path,
        *,
        expected_num_classes: int,
    ) -> None:

        if not path.exists():
            raise FileNotFoundError(
                f"Hospital dataset artifact not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Hospital dataset artifact is not a file: {path}"
            )

        if expected_num_classes < 1:
            raise ValueError(
                "expected_num_classes must be at least 1."
            )

        (
            images,
            labels,
        ) = self._load_npz(
            path,
            expected_num_classes=expected_num_classes,
        )

        self.images = images
        self.labels = labels

    @staticmethod
    def _load_npz(
        path: Path,
        *,
        expected_num_classes: int,
    ) -> tuple[Tensor, Tensor]:
        """
        Load and validate the hospital-local NPZ artifact.

        Pickled Python objects are explicitly disabled.
        """

        with np.load(
            path,
            allow_pickle=False,
        ) as data:

            available = set(data.files)

            pairs = [
                ("x_train", "y_train"),
                ("x", "y"),
                ("images", "labels"),
            ]

            x_key: str | None = None
            y_key: str | None = None

            for candidate_x, candidate_y in pairs:
                if (
                    candidate_x in available
                    and candidate_y in available
                ):
                    x_key = candidate_x
                    y_key = candidate_y
                    break

            if x_key is None or y_key is None:
                raise ValueError(
                    "NPZ must contain one of: "
                    "x_train/y_train, x/y, or images/labels."
                )

            x = np.asarray(data[x_key])
            y = np.asarray(data[y_key])

        # ---------------------------------------------------------
        # Basic structure
        # ---------------------------------------------------------

        if x.ndim < 2:
            raise ValueError(
                "Input samples must have at least 2 dimensions."
            )

        if y.ndim != 1:
            y = y.reshape(-1)

        if x.shape[0] <= 0:
            raise ValueError(
                "Hospital dataset contains no samples."
            )

        if len(y) != x.shape[0]:
            raise ValueError(
                "Number of labels does not match "
                "number of input samples."
            )

        # ---------------------------------------------------------
        # Numeric validation
        # ---------------------------------------------------------

        if not np.issubdtype(
            x.dtype,
            np.number,
        ):
            raise ValueError(
                "Input samples must contain numeric values."
            )

        if not np.all(
            np.isfinite(x)
        ):
            raise ValueError(
                "Input samples contain non-finite values."
            )

        if not np.issubdtype(
            y.dtype,
            np.integer,
        ):
            if not np.all(
                np.isfinite(y)
            ):
                raise ValueError(
                    "Labels contain non-finite values."
                )

            if not np.all(
                np.equal(
                    y,
                    np.floor(y),
                )
            ):
                raise ValueError(
                    "Labels must contain integer class IDs."
                )

        y = y.astype(
            np.int64,
            copy=False,
        )

        # ---------------------------------------------------------
        # Class validation
        # ---------------------------------------------------------

        min_label = int(y.min())
        max_label = int(y.max())

        if min_label < 0:
            raise ValueError(
                "Labels cannot be negative."
            )

        if max_label >= expected_num_classes:
            raise ValueError(
                f"Label {max_label} exceeds the configured "
                f"class range 0-{expected_num_classes - 1}."
            )

        unique_classes = np.unique(y)

        if len(unique_classes) < 2:
            raise ValueError(
                "Hospital dataset must contain at least two classes."
            )

        # ---------------------------------------------------------
        # MNIST-compatible shape
        # ---------------------------------------------------------
        #
        # Supported:
        #
        #   [N, 28, 28]
        #   [N, 1, 28, 28]
        #
        # The CNN expects:
        #
        #   [batch, 1, 28, 28]
        #

        if x.ndim == 3:

            if (
                x.shape[1] != 28
                or x.shape[2] != 28
            ):
                raise ValueError(
                    "MNIST-compatible input must have shape "
                    "[N, 28, 28] or [N, 1, 28, 28]."
                )

            x = x[:, np.newaxis, :, :]

        elif x.ndim == 4:

            if x.shape[1] != 1:
                raise ValueError(
                    "MNIST-compatible 4D input must have "
                    "one channel: [N, 1, 28, 28]."
                )

            if (
                x.shape[2] != 28
                or x.shape[3] != 28
            ):
                raise ValueError(
                    "MNIST-compatible input must have shape "
                    "[N, 1, 28, 28]."
                )

        else:
            raise ValueError(
                "MNIST-compatible input must have shape "
                "[N, 28, 28] or [N, 1, 28, 28]."
            )

        # ---------------------------------------------------------
        # Convert to float32
        # ---------------------------------------------------------

        x = x.astype(
            np.float32,
            copy=False,
        )

        # ---------------------------------------------------------
        # Normalize
        # ---------------------------------------------------------
        #
        # The existing torchvision MNIST pipeline uses:
        #
        #   mean = 0.1307
        #   std  = 0.3081
        #
        # Uploaded hospital datasets may contain either:
        #
        #   [0, 1] floating-point pixels
        #
        # or already normalized values.
        #
        # We intentionally normalize only [0, 1] style data.
        #

        x_min = float(x.min())
        x_max = float(x.max())

        if (
            x_min >= 0.0
            and x_max <= 1.0
        ):
            x = (
                x - 0.1307
            ) / 0.3081

        images = torch.from_numpy(
            np.ascontiguousarray(x)
        )

        labels = torch.from_numpy(
            np.ascontiguousarray(y)
        ).long()

        return images, labels

    def __len__(self) -> int:
        return int(
            self.labels.shape[0]
        )

    def __getitem__(
        self,
        index: int,
    ) -> tuple[Tensor, Tensor]:

        return (
            self.images[index],
            self.labels[index],
        )


# ============================================================================
# TRAINING RESULT
# ============================================================================

class HospitalTrainingResult:
    """
    Result of one hospital-local training session.

    This is deliberately a lightweight runtime object.

    Raw hospital data is not included.
    """

    def __init__(
        self,
        *,
        hospital_id: str,
        dataset_id: str,
        dataset_version_id: str,
        dataset_version: str,
        round_id: str,
        update: ModelUpdate,
        training_loss: float,
        epochs_completed: int,
        num_examples: int,
        artifact_fingerprint: str,
    ) -> None:

        self.hospital_id = hospital_id
        self.dataset_id = dataset_id
        self.dataset_version_id = dataset_version_id
        self.dataset_version = dataset_version
        self.round_id = round_id
        self.update = update
        self.training_loss = training_loss
        self.epochs_completed = epochs_completed
        self.num_examples = num_examples
        self.artifact_fingerprint = artifact_fingerprint


# ============================================================================
# SERVICE
# ============================================================================

class HospitalTrainingService:
    """
    Execute genuine local federated training for one hospital.

    Existing training components are reused:

        FedSentinelCNN
            ↓
        HospitalClient
            ↓
        LocalTrainer
            ↓
        compute_model_delta()
            ↓
        ModelUpdate

    This service does not perform security analysis.
    """

    def __init__(
        self,
        *,
        local_epochs: int = 1,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        device: str = "cpu",
    ) -> None:

        if local_epochs < 1:
            raise ValueError(
                "local_epochs must be at least 1."
            )

        if batch_size < 1:
            raise ValueError(
                "batch_size must be at least 1."
            )

        if learning_rate <= 0:
            raise ValueError(
                "learning_rate must be positive."
            )

        if not device.strip():
            raise ValueError(
                "device must not be empty."
            )

        self.local_epochs = local_epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.device = device

        # Resolves the latest validated federation model and verifies
        # its artifact hash before local training begins.
        self.global_model_service = GlobalModelService()

    # ------------------------------------------------------------------
    # MODEL
    # ------------------------------------------------------------------

    @staticmethod
    def model_factory(
        num_classes: int = 10,
    ) -> FedSentinelCNN:
        """
        Create the same CNN architecture used by the simulator.
        """

        return FedSentinelCNN(
            num_classes=num_classes
        )

    # ------------------------------------------------------------------
    # STORAGE
    # ------------------------------------------------------------------

    @staticmethod
    def _storage_path(
        *,
        hospital_id: str,
        dataset_id: str,
        version: str,
    ) -> Path:
        """
        Build the deterministic hospital-local artifact path.

        This mirrors the existing DatasetService storage layout.
        """

        return (
            DATASET_STORAGE_ROOT
            / hospital_id
            / dataset_id
            / version
            / "dataset.npz"
        )

    # ------------------------------------------------------------------
    # FINGERPRINT
    # ------------------------------------------------------------------

    @staticmethod
    def _sha256(
        path: Path,
    ) -> str:
        """
        Calculate the SHA-256 fingerprint of the local artifact.
        """

        digest = hashlib.sha256()

        with path.open(
            "rb"
        ) as file:

            while True:

                chunk = file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                digest.update(chunk)

        return digest.hexdigest()

    # ------------------------------------------------------------------
    # DATASET LOOKUP
    # ------------------------------------------------------------------

    @classmethod
    def _get_dataset_version(
        cls,
        db: Session,
        *,
        hospital_id: str,
        dataset_id: str,
        version: str,
    ) -> tuple[DatasetModel, DatasetVersion]:

        dataset = (
            db.query(DatasetModel)
            .filter(
                DatasetModel.id == dataset_id,
                DatasetModel.hospital_id == hospital_id,
            )
            .first()
        )

        if dataset is None:
            raise ValueError(
                "Dataset was not found for this hospital."
            )

        if not dataset.is_active:
            raise ValueError(
                "Dataset is inactive."
            )

        dataset_version = (
            db.query(DatasetVersion)
            .filter(
                DatasetVersion.dataset_id == dataset_id,
                DatasetVersion.version == version,
            )
            .first()
        )

        if dataset_version is None:
            raise ValueError(
                "Dataset version was not found."
            )

        return (
            dataset,
            dataset_version,
        )

    # ------------------------------------------------------------------
    # TRAIN
    # ------------------------------------------------------------------

    def train(
        self,
        db: Session,
        *,
        hospital_id: str,
        dataset_id: str,
        version: str,
        round_id: str,
        global_state: Mapping[str, Tensor],
        update_id: str | None = None,
    ) -> HospitalTrainingResult:
        """
        Perform one hospital-local training session.

        The hospital:

            1. Loads its registered local dataset.
            2. Verifies the stored artifact fingerprint.
            3. Builds the existing FedSentinel CNN.
            4. Creates the existing HospitalClient.
            5. Trains locally.
            6. Produces the existing ModelUpdate.

        The raw dataset never leaves this service.
        """

        if not hospital_id.strip():
            raise ValueError(
                "hospital_id must not be empty."
            )

        if not dataset_id.strip():
            raise ValueError(
                "dataset_id must not be empty."
            )

        if not version.strip():
            raise ValueError(
                "version must not be empty."
            )

        if not round_id.strip():
            raise ValueError(
                "round_id must not be empty."
            )

        if not global_state:
            raise ValueError(
                "global_state must not be empty."
            )

        # ---------------------------------------------------------
        # 1. Locate registered dataset
        # ---------------------------------------------------------

        (
            dataset,
            dataset_version,
        ) = self._get_dataset_version(
            db,
            hospital_id=hospital_id,
            dataset_id=dataset_id,
            version=version,
        )

        # ---------------------------------------------------------
        # 2. Locate hospital-local artifact
        # ---------------------------------------------------------

        artifact_path = self._storage_path(
            hospital_id=hospital_id,
            dataset_id=dataset_id,
            version=version,
        )

        if not artifact_path.exists():
            raise FileNotFoundError(
                "Registered dataset artifact is missing from "
                f"hospital-local storage: {artifact_path}"
            )

        # ---------------------------------------------------------
        # 3. Verify artifact fingerprint
        # ---------------------------------------------------------

        actual_fingerprint = self._sha256(
            artifact_path
        )

        if (
            dataset_version.fingerprint
            and actual_fingerprint
            != dataset_version.fingerprint
        ):
            raise ValueError(
                "Hospital dataset artifact fingerprint mismatch."
            )

        # ---------------------------------------------------------
        # 4. Load dataset locally
        # ---------------------------------------------------------

        local_dataset = HospitalNPZDataset(
            artifact_path,
            expected_num_classes=dataset.num_classes,
        )

        if len(local_dataset) != dataset_version.sample_count:
            raise ValueError(
                "Stored dataset sample count does not match "
                "the registered dataset version metadata."
            )

        # ---------------------------------------------------------
        # 5. Create model
        # ---------------------------------------------------------

        model = self.model_factory(
            num_classes=dataset.num_classes
        )

        # ---------------------------------------------------------
        # 6. Create hospital client
        # ---------------------------------------------------------

        config = ClientConfig(
            client_id=hospital_id,
            local_epochs=self.local_epochs,
            batch_size=self.batch_size,
            learning_rate=self.learning_rate,
            device=self.device,
        )

        hospital_client = HospitalClient(
            config=config,
            dataset=local_dataset,
            model=model,
        )

        # ---------------------------------------------------------
        # 7. Generate update ID
        # ---------------------------------------------------------

        if update_id is None:
            update_id = (
                f"{round_id}-{hospital_id}-"
                f"{uuid.uuid4().hex[:12]}"
            )

        # ---------------------------------------------------------
        # 8. Train locally
        # ---------------------------------------------------------

        training_result = hospital_client.trainer.train(
            global_state_dict=clone_state_dict(
                global_state
            ),
            dataloader=hospital_client.create_dataloader(
                shuffle=True
            ),
        )

        # ---------------------------------------------------------
        # 9. Create the standard FedSentinel ModelUpdate
        # ---------------------------------------------------------

        from backend.models.update import create_model_update

        update = create_model_update(
            update_id=update_id,
            client_id=hospital_id,
            round_id=round_id,
            delta=training_result.model_delta,
            num_examples=training_result.num_examples,
        )

        return HospitalTrainingResult(
            hospital_id=hospital_id,
            dataset_id=dataset.id,
            dataset_version_id=dataset_version.id,
            dataset_version=dataset_version.version,
            round_id=round_id,
            update=update,
            training_loss=training_result.average_loss,
            epochs_completed=training_result.epochs_completed,
            num_examples=training_result.num_examples,
            artifact_fingerprint=actual_fingerprint,
        )


    # ------------------------------------------------------------------
    # SECURE FEDERATION TRAINING
    # ------------------------------------------------------------------

    def train_from_federation(
        self,
        db: Session,
        *,
        hospital_id: str,
        federation_id: str,
        dataset_id: str,
        version: str,
        round_id: str,
        update_id: str | None = None,
    ) -> HospitalTrainingResult:
        """
        Perform genuine local training using the federation's
        server-verified global model.

        The caller cannot provide an arbitrary global model state.

        Raw hospital data remains local.
        Security analysis is performed after submission.
        """

        if not hospital_id.strip():
            raise ValueError("hospital_id must not be empty.")

        if not federation_id.strip():
            raise ValueError("federation_id must not be empty.")

        if not round_id.strip():
            raise ValueError("round_id must not be empty.")

        # ---------------------------------------------------------
        # 1. Verify federation
        # ---------------------------------------------------------

        federation = (
            db.query(Federation)
            .filter(
                Federation.id == federation_id,
                Federation.status == "ACTIVE",
            )
            .first()
        )

        if federation is None:
            raise ValueError("Active federation was not found.")

        # ---------------------------------------------------------
        # 2. Verify round belongs to federation
        # ---------------------------------------------------------

        federation_round = (
            db.query(FederationRound)
            .filter(
                FederationRound.id == round_id,
                FederationRound.federation_id == federation_id,
            )
            .first()
        )

        if federation_round is None:
            raise ValueError(
                "Round was not found for this federation."
            )

        # ---------------------------------------------------------
        # 3. Verify round is accepting hospital training
        # ---------------------------------------------------------

        if federation_round.status != "RUNNING":
            raise ValueError(
                f"Round is not accepting hospital training. "
                f"Current status: {federation_round.status}."
            )

        # ---------------------------------------------------------
        # 4. Load the latest validated global model
        # ---------------------------------------------------------

        (
            model_version,
            global_state,
        ) = self.global_model_service.load_latest_verified(
            db,
            federation=federation,
        )

        # ---------------------------------------------------------
        # 5. Train using the existing trusted local flow
        # ---------------------------------------------------------

        result = self.train(
            db,
            hospital_id=hospital_id,
            dataset_id=dataset_id,
            version=version,
            round_id=round_id,
            global_state=global_state,
            update_id=update_id,
        )

        # ---------------------------------------------------------
        # 6. Attach model provenance
        # ---------------------------------------------------------

        result.update.metadata.update(
            {
                "federation_id": federation.id,
                "global_model_version": model_version.version,
                "global_model_hash": model_version.model_hash,
                "training_source": "verified_global_model",
            }
        )

        return result
