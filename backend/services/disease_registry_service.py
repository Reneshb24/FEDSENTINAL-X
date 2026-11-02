"""
Disease Model Registry Service for FedSentinel-X.

Manages persistent, versioned disease-specific model checkpoints, SafeTensors weights,
cryptographic SHA-256 hashes, label mappings, and preprocessing specifications.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Mapping
from torch import Tensor
from safetensors.torch import save_file, load_file

from backend.storage.database import SessionLocal
from backend.storage.models import AggregatedDiseaseUpdate, Hospital


DISEASE_MODELS_ROOT = Path("data/models/disease_models")


DEFAULT_DISEASE_METADATA: dict[str, dict[str, Any]] = {
    "PULMONARY_IMAGE": {
        "display_name": "Pulmonary Pneumonia & Respiratory Infiltration",
        "modality": "IMAGE",
        "model_architecture": "FedSentinelCNN",
        "label_mapping": {
            "0": "Normal Cardiopulmonary Examination",
            "1": "Mild Interstitial Markings",
            "2": "Atelectasis / Dependent Opacity",
            "3": "Community-Acquired Lobar Pneumonia",
            "8": "Cardiomegaly / Left Ventricular Enlargement",
        },
        "preprocessing_config": {
            "image_size": [28, 28],
            "channels": 1,
            "normalization": "min_max_0_1",
            "anatomical_region": "THORACIC_CHEST",
            "contrast_ratio_min": 1.08,
        },
        "supported_conditions": ["Pneumonia", "Pulmonary Infiltration", "Lobar Opacity"],
        "unsupported_conditions": ["Neurology", "Craniomaxillofacial", "Orthopedics", "Extremities"],
    },
    "METABOLIC_DIABETES": {
        "display_name": "Type-2 Diabetes & Endocrine Biomarkers",
        "modality": "STRUCTURED_VITALS",
        "model_architecture": "ClinicalBiomarkerNet",
        "label_mapping": {
            "0": "Normal Glycemic Regulation",
            "1": "Type-2 Diabetes Mellitus with Hyperglycemia",
            "2": "Impaired Fasting Glucose / Pre-Diabetes",
            "3": "Metabolic Syndrome with Insulin Resistance",
        },
        "preprocessing_config": {
            "features": ["glucose", "bmi", "age", "blood_pressure", "insulin", "diabetes_pedigree"],
            "scaling": "z_score_standardization",
        },
        "supported_conditions": ["Type-2 Diabetes", "Hyperglycemia", "Metabolic Syndrome"],
        "unsupported_conditions": ["Type-1 Autoimmune DKA", "Gestational Diabetes"],
    },
    "CARDIOMETABOLIC": {
        "display_name": "Cardiometabolic & Acute Coronary Syndrome",
        "modality": "IMAGE_TEXT",
        "model_architecture": "FedSentinelCNN",
        "label_mapping": {
            "0": "Normal Transverse Cardiac Silhouette",
            "1": "Pericardial Effusion",
            "2": "Congestive Heart Failure (Early Decompensation)",
            "8": "Cardiomegaly with Early Pulmonary Vascular Congestion",
        },
        "preprocessing_config": {
            "image_size": [28, 28],
            "channels": 1,
            "normalization": "min_max_0_1",
            "cardiothoracic_ratio_threshold": 0.53,
        },
        "supported_conditions": ["Cardiomegaly", "Acute Coronary Syndrome", "Heart Failure"],
        "unsupported_conditions": ["Congenital Heart Defects", "Valvular Stenosis"],
    },
    "DERMATOLOGIC": {
        "display_name": "Dermatologic Dysplastic & Melanoma Lesions",
        "modality": "IMAGE",
        "model_architecture": "FedSentinelCNN",
        "label_mapping": {
            "0": "Benign Melanocytic Nevus",
            "1": "Seborrheic Keratosis",
            "2": "Atypical Dysplastic Nevus",
            "5": "Cutaneous Malignant Melanoma",
            "6": "Pigmented Basal Cell Carcinoma",
        },
        "preprocessing_config": {
            "image_size": [28, 28],
            "channels": 3,
            "normalization": "min_max_0_1",
            "chromatic_difference_min": 12.0,
        },
        "supported_conditions": ["Malignant Melanoma", "Dysplastic Nevus", "Atypical Lesion"],
        "unsupported_conditions": ["Psoriasis", "Alopecia", "Eczema / Atopic Dermatitis"],
    },
    "CONSENSUS_MULTI": {
        "display_name": "Unified Multi-Disease Federated Consensus",
        "modality": "TEXT",
        "model_architecture": "ClinicalTextClassifier",
        "label_mapping": {
            "0": "Community-Acquired Pneumonia / Acute Pulmonary Infection",
            "1": "Type-2 Diabetes Mellitus with Hyperglycemia",
            "2": "Acute Coronary Syndrome (Myocardial Ischemia)",
            "3": "Systemic Inflammatory Response / Severe Sepsis",
            "4": "Cutaneous Melanoma / Atypical Dysplastic Lesion",
            "5": "Acute Asthma Exacerbation / Bronchospasm",
            "6": "Chronic Kidney Disease / Renal Impairment",
            "7": "Acute Cerebrovascular Event / Transient Ischemic Attack",
        },
        "preprocessing_config": {
            "vectorizer": "clinical_keyword_tfidf",
            "vocab_size": 128,
            "lowercase": True,
        },
        "supported_conditions": [
            "Pneumonia", "Diabetes", "Coronary Syndrome", "Sepsis", "Melanoma", "Asthma"
        ],
        "unsupported_conditions": [
            "Rare Genetic Syndromes", "Tropical Parasitology", "Psychiatric Disorders"
        ],
    },
}


class DiseaseRegistryService:
    """
    Central service for managing disease checkpoints, weights, metadata, and label mappings.
    """

    @classmethod
    def get_checkpoint_dir(cls, disease_domain: str) -> Path:
        domain_dir = DISEASE_MODELS_ROOT / disease_domain.lower()
        domain_dir.mkdir(parents=True, exist_ok=True)
        return domain_dir

    @classmethod
    def save_checkpoint(
        cls,
        disease_domain: str,
        weights: Mapping[str, Tensor],
        metadata: dict[str, Any],
    ) -> tuple[Path, str]:
        """
        Save a model checkpoint as SafeTensors and write its config.json.
        """
        domain_dir = cls.get_checkpoint_dir(disease_domain)
        ckpt_path = domain_dir / "model.safetensors"
        config_path = domain_dir / "config.json"

        # Save SafeTensors weights
        save_file(weights, str(ckpt_path))

        # Compute SHA-256
        hasher = hashlib.sha256()
        with open(ckpt_path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                hasher.update(chunk)
        weights_hash = f"sha256-{hasher.hexdigest()}"

        # Merge with default metadata
        base_meta = DEFAULT_DISEASE_METADATA.get(disease_domain, {}).copy()
        base_meta.update(metadata)
        base_meta["model_weights_hash"] = weights_hash
        base_meta["updated_at"] = datetime.now(timezone.utc).isoformat()

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(base_meta, f, indent=2)

        return ckpt_path, weights_hash

    @classmethod
    def load_checkpoint(cls, disease_domain: str) -> tuple[dict[str, Tensor] | None, dict[str, Any] | None]:
        """
        Load model weights and metadata for a disease domain.
        """
        domain_dir = cls.get_checkpoint_dir(disease_domain)
        ckpt_path = domain_dir / "model.safetensors"
        config_path = domain_dir / "config.json"

        weights = None
        if ckpt_path.exists():
            try:
                weights = load_file(str(ckpt_path))
            except Exception:
                weights = None

        config = None
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception:
                config = DEFAULT_DISEASE_METADATA.get(disease_domain)
        else:
            config = DEFAULT_DISEASE_METADATA.get(disease_domain)

        return weights, config

    @classmethod
    def get_metadata(cls, disease_domain: str) -> dict[str, Any]:
        """
        Get metadata, label mappings, and preprocessing config for a disease domain.
        """
        domain_dir = cls.get_checkpoint_dir(disease_domain)
        config_path = domain_dir / "config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return DEFAULT_DISEASE_METADATA.get(disease_domain, {})
