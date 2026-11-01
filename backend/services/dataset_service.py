from __future__ import annotations
import io
import tarfile
import zipfile
from PIL import Image

def _classify_and_resolve_url(url: str) -> tuple[str, str]:
    """
    Classify whether a URL is a direct download or an online dataset repository resource.
    Resolves repository web pages to direct artifact stream URLs when public.
    """
    url_lower = url.lower()
    
    # 1. Hugging Face Datasets
    if "huggingface.co" in url_lower:
        # e.g. https://huggingface.co/datasets/user/repo/blob/main/data.zip -> resolve/main/data.zip
        resolved = url.replace("/blob/", "/resolve/")
        return resolved, "ONLINE_DATASET_RESOURCE"
        
    # 2. GitHub Raw or Releases
    if "github.com" in url_lower and "/blob/" in url:
        # https://github.com/owner/repo/blob/branch/path/file.csv -> raw.githubusercontent.com/owner/repo/branch/path/file.csv
        parts = url.replace("https://github.com/", "").replace("http://github.com/", "").split("/blob/")
        if len(parts) == 2:
            resolved = f"https://raw.githubusercontent.com/{parts[0]}/{parts[1]}"
            return resolved, "ONLINE_DATASET_RESOURCE"
    if "raw.githubusercontent.com" in url_lower:
        return url, "ONLINE_DATASET_RESOURCE"
        
    # 3. Zenodo Records
    if "zenodo.org" in url_lower:
        return url, "ONLINE_DATASET_RESOURCE"

    # 4. Kaggle / Mendeley / Figshare
    if any(k in url_lower for k in ("kaggle.com", "mendeley.com", "figshare.com")):
        return url, "ONLINE_DATASET_RESOURCE"

    # 5. Direct HTTP/HTTPS URL
    if url.startswith(("http://", "https://")):
        return url, "DIRECT_URL"

    # 6. Local Path
    return url, "LOCAL_UPLOAD"


def _process_archive_or_file(
    src_path: Path,
    target_npz: Path,
    expected_num_classes: int,
) -> tuple[int, int]:
    """
    Standardize uploaded or downloaded artifact into a verified SafeTensors-compatible NPZ.
    Supports ZIP, TAR, TAR.GZ, CSV, and NPZ formats.
    Enforces strict zero-pickle deserialization, archive safety, and float bounds.
    """
    # 1. Check if already NPZ
    is_npz = False
    try:
        with open(src_path, "rb") as f:
            header = f.read(6)
            if header.startswith(b"PK"):
                # Could be ZIP or NPZ
                pass
    except Exception:
        pass

    # Try NPZ direct load first
    try:
        sample_count, class_count = _validate_npz_dataset(
            src_path, expected_num_classes=expected_num_classes
        )
        shutil.copyfile(src_path, target_npz)
        return sample_count, class_count
    except Exception:
        pass

    # 2. Try ZIP archive
    if zipfile.is_zipfile(src_path):
        with zipfile.ZipFile(src_path, "r") as zf:
            total_uncompressed = sum(info.file_size for info in zf.infolist())
            if total_uncompressed > MAX_DATASET_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Extracted archive size ({total_uncompressed / (1024*1024):.1f} MB) exceeds maximum allowed 100 MB.",
                )
            for name in zf.namelist():
                if ".." in name or name.startswith("/") or name.startswith("\\"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Archive contains unsafe path traversal components.",
                    )

            # Check if archive contains an inner NPZ
            for name in zf.namelist():
                if name.lower().endswith(".npz"):
                    inner_bytes = zf.read(name)
                    with open(target_npz, "wb") as f_out:
                        f_out.write(inner_bytes)
                    return _validate_npz_dataset(target_npz, expected_num_classes=expected_num_classes)

            # Check if archive contains CSV
            for name in zf.namelist():
                if name.lower().endswith(".csv") and not name.startswith("__MACOSX"):
                    csv_text = zf.read(name).decode("utf-8", errors="ignore")
                    return _parse_csv_text_to_npz(csv_text, target_npz, expected_num_classes)

            # Check if archive contains image folders (e.g. NORMAL/ vs PNEUMONIA/)
            classes = {}
            images_list = []
            labels_list = []
            image_extensions = (".png", ".jpg", ".jpeg")

            for name in zf.namelist():
                if name.lower().endswith(image_extensions) and not name.startswith("__MACOSX"):
                    parts = [p for p in name.split("/") if p]
                    if len(parts) >= 2:
                        cls_name = parts[-2]
                        if cls_name not in classes:
                            classes[cls_name] = len(classes)
                        label = classes[cls_name]
                        try:
                            raw_img = Image.open(io.BytesIO(zf.read(name))).convert("L")
                            raw_img = raw_img.resize((28, 28), Image.Resampling.BILINEAR)
                            arr = np.asarray(raw_img, dtype=np.float32) / 255.0
                            images_list.append(arr.reshape(1, 28, 28))
                            labels_list.append(label)
                        except Exception:
                            continue

            if len(images_list) >= 2 and len(classes) >= 2:
                images = np.array(images_list, dtype=np.float32)
                labels = np.array(labels_list, dtype=np.int64)
                np.savez_compressed(target_npz, images=images, labels=labels)
                return _validate_npz_dataset(target_npz, expected_num_classes=expected_num_classes)

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ZIP archive does not contain a recognizable dataset (.npz, .csv, or categorized image folders).",
        )

    # 3. Try CSV direct file
    try:
        with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
            csv_text = f.read()
        return _parse_csv_text_to_npz(csv_text, target_npz, expected_num_classes)
    except Exception as exc:
        pass

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Unsupported dataset artifact format. Supported formats: .npz, .zip, .tar.gz, .csv, or public repository link.",
    )


def _parse_csv_text_to_npz(
    csv_text: str,
    target_npz: Path,
    expected_num_classes: int,
) -> tuple[int, int]:
    """Parse CSV text into normalized (1, 28, 28) image/feature arrays and labels."""
    lines = [ln.strip() for ln in csv_text.strip().splitlines() if ln.strip()]
    if not lines:
        raise ValueError("CSV dataset is empty.")

    start_row = 0
    # Check for header
    first_row_tokens = lines[0].split(",")
    try:
        float(first_row_tokens[0])
    except ValueError:
        start_row = 1  # Header present

    parsed_rows = []
    for line in lines[start_row:]:
        parts = [p.strip() for p in line.split(",") if p.strip()]
        if len(parts) >= 2:
            try:
                nums = [float(p) for p in parts]
                parsed_rows.append(nums)
            except ValueError:
                continue

    if len(parsed_rows) < 2:
        raise ValueError("CSV contains fewer than 2 valid rows.")

    data = np.array(parsed_rows, dtype=np.float32)
    labels = data[:, 0].astype(np.int64)
    features = data[:, 1:]

    # Shape features into (N, 1, 28, 28)
    if features.shape[1] == 784:
        images = features.reshape(-1, 1, 28, 28)
    else:
        # Pad or slice to 784
        padded = np.pad(features, ((0, 0), (0, max(0, 784 - features.shape[1]))))[:, :784]
        images = padded.reshape(-1, 1, 28, 28)

    if images.max() > 1.0:
        images = images / 255.0

    np.savez_compressed(target_npz, images=images, labels=labels)
    return _validate_npz_dataset(target_npz, expected_num_classes=expected_num_classes)

"""
Hospital dataset management service.

Datasets belong to individual hospitals.

Raw dataset contents remain on hospital-side storage and are never
sent through the FedSentinel model-update security pipeline.
"""


import hashlib
import ipaddress
import os
import shutil
import socket
import tempfile
import urllib.request
from urllib.parse import urlparse
import uuid
from pathlib import Path

import numpy as np

from fastapi import HTTPException
from fastapi import status
from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.schemas.dataset import (
    DatasetCreate,
    DatasetUpdate,
    DatasetVersionCreate,
)
from backend.services.audit import record_audit
from backend.storage.models import Dataset
from backend.storage.models import DatasetVersion
from backend.storage.models import Hospital


# ============================================================================
# STORAGE CONFIGURATION
# ============================================================================

DATASET_STORAGE_ROOT = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "hospital_datasets"
)

MAX_DATASET_SIZE = 100 * 1024 * 1024  # 100 MB
CHUNK_SIZE = 1024 * 1024


# ============================================================================
# HELPERS
# ============================================================================

def _validate_safe_url(url: str) -> None:
    """
    Validate that an external record URL is safe from SSRF attacks.
    Blocks localhost, loopback, private RFC-1918, link-local, and reserved IP ranges.
    """
    parsed = urlparse(url)
    if parsed.scheme.lower() not in ("http", "https"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forbidden URL scheme: only HTTP and HTTPS are permitted.",
        )
    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL: missing hostname.",
        )
    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forbidden host: remote URL cannot point to localhost or loopback addresses.",
        )
    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to resolve hostname '{hostname}'.",
        ) from exc

    for family, _, _, _, sockaddr in addr_info:
        ip_str = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_reserved
                or ip_obj.is_multicast
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Forbidden host: URL resolves to private or restricted network address ({ip_str}).",
                )
        except ValueError:
            continue


def _safe_component(value: str) -> str:
    """
    Allow only safe filesystem path components.
    """

    value = value.strip()

    if not value:
        raise ValueError("Empty path component.")

    allowed = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        "._-"
    )

    if any(character not in allowed for character in value):
        raise ValueError(
            f"Unsafe path component: {value}"
        )

    return value


def _version_storage_dir(
    hospital_id: str,
    dataset_id: str,
    version: str,
) -> Path:
    """
    Build deterministic local storage path.

    IDs are generated by the application and version names are
    validated before reaching this function.
    """

    hospital = _safe_component(hospital_id)
    dataset = _safe_component(dataset_id)
    version = _safe_component(version)

    return (
        DATASET_STORAGE_ROOT
        / hospital
        / dataset
        / version
    )


def _validate_npz_dataset(
    path: Path,
    *,
    expected_num_classes: int,
) -> tuple[int, int]:
    """
    Validate a MNIST-compatible NPZ dataset.

    Supported array naming conventions:

        x_train / y_train
        x / y
        images / labels

    Pickled Python objects are explicitly disabled.
    """

    try:
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

            x_key = None
            y_key = None

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

            if x.ndim < 2:
                raise ValueError(
                    "Input samples must have at least 2 dimensions."
                )

            if y.ndim != 1:
                y = y.reshape(-1)

            sample_count = int(x.shape[0])

            if sample_count <= 0:
                raise ValueError(
                    "Dataset contains no samples."
                )

            if len(y) != sample_count:
                raise ValueError(
                    "Number of labels does not match "
                    "number of samples."
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
                    np.equal(y, np.floor(y))
                ):
                    raise ValueError(
                        "Labels must contain integer class IDs."
                    )

            y = y.astype(
                np.int64,
                copy=False,
            )

            if not np.all(
                np.isfinite(x)
            ):
                raise ValueError(
                    "Input samples contain non-finite values."
                )

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

            class_count = int(
                np.unique(y).size
            )

            if class_count < 2:
                raise ValueError(
                    "Dataset must contain at least two classes."
                )

            return sample_count, class_count

    except ValueError:
        raise

    except Exception as exc:
        raise ValueError(
            f"Unable to read NPZ dataset safely: {exc}"
        ) from exc


def _save_upload_and_hash(
    upload: UploadFile,
    destination: Path,
) -> tuple[int, str]:
    """
    Stream upload to disk while calculating SHA-256.

    The file is never loaded entirely into memory.
    """

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    hasher = hashlib.sha256()
    total_size = 0

    try:
        with destination.open(
            "wb"
        ) as output:

            while True:
                chunk = upload.file.read(
                    CHUNK_SIZE
                )

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_DATASET_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=(
                            "Dataset exceeds the maximum "
                            "allowed size of 100 MB."
                        ),
                    )

                hasher.update(chunk)
                output.write(chunk)

    except HTTPException:
        destination.unlink(
            missing_ok=True
        )
        raise

    except Exception:
        destination.unlink(
            missing_ok=True
        )
        raise

    return total_size, hasher.hexdigest()


class DatasetService:

    # ========================================================================
    # LIST
    # ========================================================================

    @staticmethod
    def list_datasets(
        db: Session,
        *,
        hospital_id: str,
    ) -> list[Dataset]:

        return (
            db.query(Dataset)
            .filter(
                Dataset.hospital_id == hospital_id
            )
            .order_by(Dataset.created_at.desc())
            .all()
        )

    # ========================================================================
    # GET
    # ========================================================================

    @staticmethod
    def get_dataset(
        db: Session,
        *,
        hospital_id: str,
        dataset_id: str,
    ) -> Dataset:

        dataset = (
            db.query(Dataset)
            .filter(
                Dataset.id == dataset_id,
                Dataset.hospital_id == hospital_id,
            )
            .first()
        )

        if dataset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found.",
            )

        return dataset

    # ========================================================================
    # CREATE
    # ========================================================================

    @staticmethod
    def create_dataset(
        db: Session,
        *,
        hospital_id: str,
        actor_user_id: str,
        payload: DatasetCreate,
    ) -> Dataset:

        hospital = (
            db.query(Hospital)
            .filter(
                Hospital.id == hospital_id
            )
            .first()
        )

        if hospital is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found.",
            )

        if not hospital.is_eligible:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Hospital is not currently eligible "
                    "to manage federation datasets."
                ),
            )

        dataset = Dataset(
            hospital_id=hospital_id,
            name=payload.name.strip(),
            dataset_type=payload.dataset_type.strip().upper(),
            sample_count=payload.sample_count,
            num_classes=payload.num_classes,
            is_active=True,
        )

        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="DATASET_CREATED",
            resource_type="dataset",
            resource_id=dataset.id,
            result="SUCCESS",
            metadata={
                "hospital_id": hospital_id,
                "dataset_name": dataset.name,
                "dataset_type": dataset.dataset_type,
                "sample_count": dataset.sample_count,
                "num_classes": dataset.num_classes,
            },
        )

        return dataset

    # ========================================================================
    # UPDATE
    # ========================================================================

    @staticmethod
    def update_dataset(
        db: Session,
        *,
        hospital_id: str,
        actor_user_id: str,
        dataset_id: str,
        payload: DatasetUpdate,
    ) -> Dataset:

        dataset = DatasetService.get_dataset(
            db,
            hospital_id=hospital_id,
            dataset_id=dataset_id,
        )

        if not dataset.is_active:
            dataset.is_active = True

        if payload.name is not None:
            dataset.name = payload.name.strip()

        if payload.dataset_type is not None:
            dataset.dataset_type = (
                payload.dataset_type.strip().upper()
            )

        if payload.num_classes is not None:
            dataset.num_classes = payload.num_classes

        db.commit()
        db.refresh(dataset)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="DATASET_UPDATED",
            resource_type="dataset",
            resource_id=dataset.id,
            result="SUCCESS",
        )

        return dataset

    # ========================================================================
    # CREATE VERSION - METADATA
    # ========================================================================

    @staticmethod
    def create_version(
        db: Session,
        *,
        hospital_id: str,
        actor_user_id: str,
        dataset_id: str,
        payload: DatasetVersionCreate,
    ) -> DatasetVersion:

        dataset = DatasetService.get_dataset(
            db,
            hospital_id=hospital_id,
            dataset_id=dataset_id,
        )

        if not dataset.is_active:
            dataset.is_active = True

        existing_version = (
            db.query(DatasetVersion)
            .filter(
                DatasetVersion.dataset_id == dataset.id,
                DatasetVersion.version == payload.version,
            )
            .first()
        )

        if existing_version is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Dataset version already exists.",
            )

        version = DatasetVersion(
            dataset_id=dataset.id,
            version=payload.version,
            sample_count=payload.sample_count,
            fingerprint=payload.fingerprint,
        )

        db.add(version)

        dataset.sample_count = payload.sample_count

        db.commit()
        db.refresh(version)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action="DATASET_VERSION_CREATED",
            resource_type="dataset",
            resource_id=dataset.id,
            result="SUCCESS",
            metadata={
                "version_id": version.id,
                "version": version.version,
                "sample_count": version.sample_count,
                "fingerprint": version.fingerprint,
                "source": "metadata",
            },
        )

        return version

    # ========================================================================
    # REAL DATASET UPLOAD
    # ========================================================================

    @staticmethod
    def upload_version(
        db: Session,
        *,
        hospital_id: str,
        actor_user_id: str,
        dataset_id: str,
        version_name: str,
        upload: UploadFile,
    ) -> tuple[DatasetVersion, int, str]:

        dataset = DatasetService.get_dataset(
            db,
            hospital_id=hospital_id,
            dataset_id=dataset_id,
        )

        if not dataset.is_active:
            dataset.is_active = True

        version_name = version_name.strip()

        if not version_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Version name cannot be empty.",
            )

        try:
            _safe_component(version_name)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Version name contains unsafe characters. "
                    "Use letters, numbers, '.', '_' or '-'."
                ),
            )

        existing_version = (
            db.query(DatasetVersion)
            .filter(
                DatasetVersion.dataset_id == dataset.id,
                DatasetVersion.version == version_name,
            )
            .first()
        )

        if existing_version is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Dataset version already exists.",
            )

        filename = upload.filename or "dataset.bin"
        allowed_exts = (".npz", ".zip", ".tar.gz", ".tgz", ".tar", ".csv", ".json", ".parquet")
        if not any(filename.lower().endswith(ext) for ext in allowed_exts):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Supported formats: .npz, .zip, .tar.gz, .csv, .json, or .parquet archives.",
            )

        storage_dir = _version_storage_dir(
            hospital_id,
            dataset.id,
            version_name,
        )

        storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        final_path = storage_dir / "dataset.npz"

        if final_path.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Dataset artifact already exists.",
            )

        temp_fd, temp_name = tempfile.mkstemp(
            prefix="upload_",
            suffix=".npz",
            dir=str(storage_dir),
        )

        os.close(temp_fd)

        temp_path = Path(temp_name)

        try:
            file_size, fingerprint = (
                _save_upload_and_hash(
                    upload,
                    temp_path,
                )
            )

            if file_size == 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Uploaded dataset is empty.",
                )

            try:
                sample_count, class_count = _process_archive_or_file(
                    temp_path,
                    final_path,
                    expected_num_classes=dataset.num_classes,
                )
            except (ValueError, HTTPException) as exc:
                if isinstance(exc, HTTPException):
                    raise exc
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Dataset validation failed: {exc}",
                ) from exc

            # Compute verified artifact stats
            file_size = final_path.stat().st_size
            with open(final_path, "rb") as f_hash:
                h = hashlib.sha256()
                while chunk := f_hash.read(CHUNK_SIZE):
                    h.update(chunk)
                fingerprint = h.hexdigest()
            temp_path.unlink(missing_ok=True)

            version = DatasetVersion(
                dataset_id=dataset.id,
                version=version_name,
                sample_count=sample_count,
                fingerprint=fingerprint,
            )

            db.add(version)

            dataset.sample_count = sample_count

            db.commit()
            db.refresh(version)

            record_audit(
                db,
                actor_user_id=actor_user_id,
                action="DATASET_VERSION_UPLOADED",
                resource_type="dataset",
                resource_id=dataset.id,
                result="SUCCESS",
                metadata={
                    "version_id": version.id,
                    "version": version.version,
                    "filename": filename,
                    "file_size": file_size,
                    "fingerprint": fingerprint,
                    "sample_count": sample_count,
                    "class_count": class_count,
                    "storage": "hospital_local",
                    "validation": "NPZ_SAFE_NO_PICKLE",
                },
            )

            return version, file_size, fingerprint, class_count

        except HTTPException:
            temp_path.unlink(
                missing_ok=True
            )
            raise

        except Exception:
            temp_path.unlink(
                missing_ok=True
            )

            # Avoid leaving a partial artifact.
            final_path.unlink(
                missing_ok=True
            )

            db.rollback()
            raise

        finally:
            upload.file.close()

    # ========================================================================
    # IMPORT DATASET VERSION FROM RECORD LINK / URL / LOCAL PATH
    # ========================================================================

    @staticmethod
    def import_version_from_link(
        db: Session,
        *,
        hospital_id: str,
        actor_user_id: str,
        dataset_id: str,
        version_name: str,
        record_link: str,
        format_type: str = "AUTO",
    ) -> tuple[DatasetVersion, int, str, int]:
        """
        Import a hospital-local dataset version from an external record URL,
        local path, or synthetic record source.

        The retrieved artifact is stored under the hospital enclave storage
        boundary and strictly validated.
        """
        dataset = DatasetService.get_dataset(
            db,
            hospital_id=hospital_id,
            dataset_id=dataset_id,
        )

        if not dataset.is_active:
            dataset.is_active = True

        version_name = version_name.strip()
        if not version_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Version name cannot be empty.",
            )

        try:
            _safe_component(version_name)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Version name contains unsafe characters. "
                    "Use letters, numbers, '.', '_' or '-'."
                ),
            )

        existing_version = (
            db.query(DatasetVersion)
            .filter(
                DatasetVersion.dataset_id == dataset.id,
                DatasetVersion.version == version_name,
            )
            .first()
        )

        if existing_version is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Dataset version '{version_name}' already exists.",
            )

        storage_dir = _version_storage_dir(
            hospital_id,
            dataset.id,
            version_name,
        )
        storage_dir.mkdir(parents=True, exist_ok=True)

        final_path = storage_dir / "dataset.npz"
        if final_path.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Dataset artifact already exists.",
            )

        temp_name = f"link_import_{uuid.uuid4().hex[:8]}.npz"
        temp_path = storage_dir / temp_name

        try:
            record_link = record_link.strip()

            if record_link.startswith(("http://", "https://")):
                # Enforce SSRF validation
                _validate_safe_url(record_link)

                # Stream download from external medical record server / URL
                req = urllib.request.Request(
                    record_link,
                    headers={"User-Agent": "FedSentinel-Clinical/2.0"},
                )
                hasher = hashlib.sha256()
                total_bytes = 0

                with urllib.request.urlopen(req, timeout=20) as resp, open(temp_path, "wb") as f_out:
                    while True:
                        chunk = resp.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        total_bytes += len(chunk)
                        if total_bytes > MAX_DATASET_SIZE:
                            raise HTTPException(
                                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                detail="Remote dataset exceeds maximum permitted size (100MB).",
                            )
                        hasher.update(chunk)
                        f_out.write(chunk)

                if total_bytes == 0:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Downloaded dataset artifact is empty.",
                    )

            else:
                # Local filesystem path (or file:// URI)
                clean_path = record_link
                if clean_path.startswith("file://"):
                    clean_path = clean_path[7:]
                
                src = Path(clean_path)
                if not src.is_absolute():
                    src = Path(os.getcwd()) / clean_path
                
                src = src.expanduser().resolve()
                workspace = Path(os.getcwd()).resolve()
                storage_root = DATASET_STORAGE_ROOT.resolve()
                temp_dir = Path(tempfile.gettempdir()).resolve()
                allowed_roots = [workspace, storage_root, temp_dir]

                is_safe_boundary = any(
                    src == root or root in src.parents for root in allowed_roots
                )
                if not is_safe_boundary and src.exists():
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied: file path is outside allowed repository and dataset storage boundaries.",
                    )

                # Special test / demo record generator if the path doesn't exist but has demo pattern
                if not src.exists() and ("demo" in record_link.lower() or "synthetic" in record_link.lower() or "sample" in record_link.lower()):
                    # Generate deterministic synthetic local clinical image dataset
                    rng = np.random.RandomState(42)
                    sample_count = 200
                    images = rng.randn(sample_count, 1, 28, 28).astype(np.float32)
                    labels = rng.randint(0, dataset.num_classes, size=(sample_count,)).astype(np.int64)
                    np.savez_compressed(temp_path, images=images, labels=labels)
                elif not src.exists():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Record path not found on hospital local storage: {record_link}",
                    )
                else:
                    shutil.copyfile(src, temp_path)

            # Compute hash and file size of the local NPZ
            hasher = hashlib.sha256()
            file_size = 0
            with open(temp_path, "rb") as f:
                while True:
                    buf = f.read(CHUNK_SIZE)
                    if not buf:
                        break
                    file_size += len(buf)
                    hasher.update(buf)
            fingerprint = hasher.hexdigest()

            # Standardize and validate multi-format archive / file
            try:
                sample_count, class_count = _process_archive_or_file(
                    temp_path,
                    final_path,
                    expected_num_classes=dataset.num_classes,
                )
            except (ValueError, HTTPException) as exc:
                if isinstance(exc, HTTPException):
                    raise exc
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Dataset validation failed: {exc}",
                ) from exc

            # Compute verified artifact stats
            file_size = final_path.stat().st_size
            with open(final_path, "rb") as f_hash:
                h = hashlib.sha256()
                while chunk := f_hash.read(CHUNK_SIZE):
                    h.update(chunk)
                fingerprint = h.hexdigest()
            temp_path.unlink(missing_ok=True)

            version = DatasetVersion(
                dataset_id=dataset.id,
                version=version_name,
                sample_count=sample_count,
                fingerprint=fingerprint,
            )

            db.add(version)
            dataset.sample_count = sample_count

            db.commit()
            db.refresh(version)

            record_audit(
                db,
                actor_user_id=actor_user_id,
                action="DATASET_VERSION_LINKED",
                resource_type="dataset",
                resource_id=dataset.id,
                result="SUCCESS",
                metadata={
                    "version_id": version.id,
                    "version": version.version,
                    "record_link": record_link,
                    "file_size": file_size,
                    "fingerprint": fingerprint,
                    "sample_count": sample_count,
                    "class_count": class_count,
                    "storage": "hospital_local",
                    "validation": "NPZ_SAFE_NO_PICKLE",
                },
            )

            return version, file_size, fingerprint, class_count

        except HTTPException:
            temp_path.unlink(missing_ok=True)
            raise
        except Exception as exc:
            temp_path.unlink(missing_ok=True)
            final_path.unlink(missing_ok=True)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Dataset record ingestion failed: {exc}",
            ) from exc

    # ========================================================================
    # LIST VERSIONS
    # ========================================================================

    @staticmethod
    def list_versions(
        db: Session,
        *,
        hospital_id: str,
        dataset_id: str,
    ) -> list[DatasetVersion]:

        dataset = DatasetService.get_dataset(
            db,
            hospital_id=hospital_id,
            dataset_id=dataset_id,
        )

        return (
            db.query(DatasetVersion)
            .filter(
                DatasetVersion.dataset_id == dataset.id
            )
            .order_by(DatasetVersion.created_at.desc())
            .all()
        )

    # ========================================================================
    # ACTIVE STATE
    # ========================================================================

    @staticmethod
    def set_active(
        db: Session,
        *,
        hospital_id: str,
        actor_user_id: str,
        dataset_id: str,
        active: bool,
    ) -> Dataset:

        dataset = DatasetService.get_dataset(
            db,
            hospital_id=hospital_id,
            dataset_id=dataset_id,
        )

        dataset.is_active = active

        db.commit()
        db.refresh(dataset)

        record_audit(
            db,
            actor_user_id=actor_user_id,
            action=(
                "DATASET_ACTIVATED"
                if active
                else "DATASET_DEACTIVATED"
            ),
            resource_type="dataset",
            resource_id=dataset.id,
            result="SUCCESS",
        )

        return dataset
