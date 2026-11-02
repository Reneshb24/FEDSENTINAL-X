import json
import uuid
from datetime import datetime, timezone
from backend.storage.database import SessionLocal
from backend.storage.models import (
    Hospital, User, Federation, FederationMembership,
    Dataset, DatasetVersion, ModelUpdate, UpdateEvidence,
    AggregatedDiseaseUpdate
)
from backend.auth.roles import Role
from backend.auth.security import hash_password

db = SessionLocal()

print("1. Cleaning up obsolete dummy hospitals...")
# Identify obsolete dummy hospitals
dummy_codes = [
    "H01", "H02", "H03", "H04", "H05", "H06", "H07", "H08", "H09", "H10",
    "H11", "H12", "H13", "H14", "H15", "H16", "H17", "H18", "H19", "H20",
    "H30", "H77", "H88", "STANFORD", "MAYO_CLINIC", "H41", "H95", "H51", "H21"
]

# Find hospitals matching these codes or names
hospitals_to_remove = db.query(Hospital).filter(
    (Hospital.code.in_(dummy_codes)) | 
    (Hospital.name.like("%FedSentinel Hospital%")) |
    (Hospital.name.like("%Federated Hospital%")) |
    (Hospital.name.like("%Demo%"))
).all()

hosp_ids_to_remove = [h.id for h in hospitals_to_remove]
print(f"Found {len(hosp_ids_to_remove)} obsolete dummy hospitals to clean.")

if hosp_ids_to_remove:
    # 1. Delete associated ModelUpdates and Evidence
    old_updates = db.query(ModelUpdate).filter(ModelUpdate.hospital_id.in_(hosp_ids_to_remove)).all()
    old_upd_ids = [u.id for u in old_updates]
    if old_upd_ids:
        db.query(UpdateEvidence).filter(UpdateEvidence.update_id.in_(old_upd_ids)).delete(synchronize_session=False)
        db.query(ModelUpdate).filter(ModelUpdate.id.in_(old_upd_ids)).delete(synchronize_session=False)

    # 2. Delete associated Datasets and DatasetVersions
    old_datasets = db.query(Dataset).filter(Dataset.hospital_id.in_(hosp_ids_to_remove)).all()
    old_ds_ids = [d.id for d in old_datasets]
    if old_ds_ids:
        db.query(DatasetVersion).filter(DatasetVersion.dataset_id.in_(old_ds_ids)).delete(synchronize_session=False)
        db.query(Dataset).filter(Dataset.id.in_(old_ds_ids)).delete(synchronize_session=False)

    # 3. Delete Federation Memberships
    db.query(FederationMembership).filter(FederationMembership.hospital_id.in_(hosp_ids_to_remove)).delete(synchronize_session=False)

    # 4. Delete Users attached to those hospitals
    db.query(User).filter(User.hospital_id.in_(hosp_ids_to_remove)).delete(synchronize_session=False)

    # 5. Delete the hospitals
    db.query(Hospital).filter(Hospital.id.in_(hosp_ids_to_remove)).delete(synchronize_session=False)

    db.commit()
    print("Obsolete dummy hospitals successfully removed!")

# Verify Default Federation exists
DEFAULT_FED_ID = "413ef0b3-a947-4a02-a652-d963ef14b8da"
fed = db.query(Federation).filter(Federation.id == DEFAULT_FED_ID).first()
if not fed:
    fed = Federation(
        id=DEFAULT_FED_ID,
        name="FedSentinel Global Healthcare Consortium",
        description="Collaborative Healthcare AI Security & Multi-Disease Federated Learning Network",
        status="ACTIVE",
    )
    db.add(fed)
    db.commit()

# Ensure Super Admin exists
admin = db.query(User).filter(User.role == Role.SUPER_ADMIN.value).first()
if not admin:
    admin = User(
        email="admin@fedsentinel.local",
        password_hash=hash_password("Admin123!"),
        role=Role.SUPER_ADMIN.value,
        hospital_id=None,
        is_active=True,
        full_name="Global Security Administrator",
    )
    db.add(admin)
    db.commit()
    print("Created Super Admin user.")

print("\n2. Creating 5 Brand New Specialized Healthcare Institutions...")

NEW_HOSPITALS = [
    {
        "code": "H101",
        "name": "Mount Sinai Pulmonary & Respiratory Center",
        "email": "admin@h101-sinai.org",
        "domain": "PULMONARY_IMAGE",
        "focus": "Pulmonary Infiltration, Lobar Pneumonia & Thoracic Radiology",
        "city": "New York, NY",
        "country": "United States",
        "dataset_name": "Chest X-Ray Pneumonia & Pulmonary Infiltration Cohort",
        "modality": "IMAGE_CLASSIFICATION",
        "records_count": 2850,
    },
    {
        "code": "H102",
        "name": "Joslin Diabetes Center & Metabolic Institute",
        "email": "admin@h102-joslin.org",
        "domain": "METABOLIC_DIABETES",
        "focus": "Type-2 Diabetes Mellitus, Glycemic Biomarkers & Insulin Resistance",
        "city": "Boston, MA",
        "country": "United States",
        "dataset_name": "Clinical Diabetes & Glycemic Metabolic Biomarkers",
        "modality": "TABULAR_CLASSIFICATION",
        "records_count": 4200,
    },
    {
        "code": "H103",
        "name": "Cleveland Clinic Cardiovascular AI Enclave",
        "email": "admin@h103-cleveland.org",
        "domain": "CARDIOMETABOLIC",
        "focus": "Cardiomegaly, Left Ventricular Enlargement & Acute Coronary Syndrome",
        "city": "Cleveland, OH",
        "country": "United States",
        "dataset_name": "Cardiothoracic Silhouette & Coronary Syndrome Records",
        "modality": "IMAGE_CLASSIFICATION",
        "records_count": 3150,
    },
    {
        "code": "H104",
        "name": "Memorial Sloan Kettering Dermatopathology Enclave",
        "email": "admin@h104-msk.org",
        "domain": "DERMATOLOGIC",
        "focus": "Dermatologic Dysplasia, Cutaneous Melanoma & Dermoscopy",
        "city": "New York, NY",
        "country": "United States",
        "dataset_name": "Dermoscopy Melanocytic & Dysplastic Lesion Cohort",
        "modality": "IMAGE_CLASSIFICATION",
        "records_count": 2400,
    },
    {
        "code": "H105",
        "name": "Johns Hopkins Clinical AI & Infectious Disease Center",
        "email": "admin@h105-hopkins.org",
        "domain": "CONSENSUS_MULTI",
        "focus": "Infectious Disease, Severe Sepsis & Multi-Modal Clinical Diagnostics",
        "city": "Baltimore, MD",
        "country": "United States",
        "dataset_name": "Multi-System Acute Infectious & Respiratory Cohort",
        "modality": "TEXT_CLASSIFICATION",
        "records_count": 5100,
    },
]

created_hospitals = []

for h_data in NEW_HOSPITALS:
    hosp = db.query(Hospital).filter(Hospital.code == h_data["code"]).first()
    if not hosp:
        hosp = Hospital(
            code=h_data["code"],
            name=h_data["name"],
            status="ACTIVE",
            application_status="APPROVED",
            is_eligible=True,
            security_status="TRUSTED",
            country=h_data["country"],
            location=h_data["city"],
            contact_email=h_data["email"],
            description=h_data["focus"],
        )
        db.add(hosp)
        db.flush()

    # Create Hospital Admin User
    user = db.query(User).filter(User.email == h_data["email"]).first()
    if not user:
        user = User(
            email=h_data["email"],
            password_hash=hash_password("Hospital123!"),
            role=Role.HOSPITAL_ADMIN.value,
            hospital_id=hosp.id,
            is_active=True,
            full_name=f"{h_data['code']} Enclave Medical Director",
        )
        db.add(user)

    # Create Federation Membership
    membership = db.query(FederationMembership).filter(
        FederationMembership.hospital_id == hosp.id,
        FederationMembership.federation_id == DEFAULT_FED_ID
    ).first()
    if not membership:
        membership = FederationMembership(
            hospital_id=hosp.id,
            federation_id=DEFAULT_FED_ID,
            status="ACTIVE",
        )
        db.add(membership)

    # Ingest Valid Dataset for Hospital
    ds = db.query(Dataset).filter(Dataset.hospital_id == hosp.id).first()
    if not ds:
        num_samples = 120
        ds = Dataset(
            hospital_id=hosp.id,
            name=h_data["dataset_name"],
            dataset_type=h_data["modality"],
            sample_count=num_samples,
            num_classes=10,
            is_active=True,
        )
        db.add(ds)
        db.flush()

        # Create physical .npz file on disk for hospital-local training
        from pathlib import Path
        import hashlib
        import numpy as np

        ds_dir = Path("data/hospital_datasets") / hosp.id / ds.id / "1.0.0"
        ds_dir.mkdir(parents=True, exist_ok=True)
        npz_file = ds_dir / "dataset.npz"

        # Deterministic synthetic medical feature arrays
        np.random.seed(42 + len(created_hospitals))
        x_data = np.random.randn(num_samples, 1, 28, 28).astype(np.float32)
        y_data = np.random.randint(0, 10, size=(num_samples,)).astype(np.int64)
        np.savez(npz_file, x=x_data, y=y_data)

        # Compute SHA-256 fingerprint
        hasher = hashlib.sha256()
        with open(npz_file, "rb") as f:
            while chunk := f.read(1024 * 1024):
                hasher.update(chunk)
        real_fp = hasher.hexdigest()

        dsv = DatasetVersion(
            dataset_id=ds.id,
            version="1.0.0",
            sample_count=num_samples,
            fingerprint=real_fp,
            source_type="LOCAL_UPLOAD",
        )
        db.add(dsv)
    else:
        # Ensure existing dataset has corresponding physical file & valid fingerprint
        from pathlib import Path
        import hashlib
        import numpy as np
        dsv = db.query(DatasetVersion).filter(DatasetVersion.dataset_id == ds.id).first()
        if dsv:
            num_samples = 120
            ds.sample_count = num_samples
            ds.num_classes = 10
            dsv.sample_count = num_samples
            ds_dir = Path("data/hospital_datasets") / hosp.id / ds.id / dsv.version
            ds_dir.mkdir(parents=True, exist_ok=True)
            npz_file = ds_dir / "dataset.npz"
            np.random.seed(42 + len(created_hospitals))
            x_data = np.random.randn(num_samples, 1, 28, 28).astype(np.float32)
            y_data = np.random.randint(0, 10, size=(num_samples,)).astype(np.int64)
            np.savez(npz_file, x=x_data, y=y_data)

            hasher = hashlib.sha256()
            with open(npz_file, "rb") as f:
                while chunk := f.read(1024 * 1024):
                    hasher.update(chunk)
            dsv.fingerprint = hasher.hexdigest()

    created_hospitals.append(hosp)

db.commit()

print(f"\nSuccessfully initialized {len(created_hospitals)} hospitals with credentials & datasets:")
for h in created_hospitals:
    print(f"  [{h.code}] {h.name} | Focus: {h.description}")

# 3. Update Consortium Aggregated Disease Updates Table
print("\n3. Updating Consortium Aggregated Global Updates for All 5 Diseases...")
db.query(AggregatedDiseaseUpdate).delete(synchronize_session=False)

DISEASE_UPDATES_SEED = [
    {
        "disease_domain": "PULMONARY_IMAGE",
        "display_name": "Pulmonary Pneumonia & Respiratory Infiltration",
        "model_version": "v2.5-pulmonary",
        "round_number": 21,
        "aggregation_algorithm": "Coordinate-Median",
        "contributing_hospitals_json": json.dumps([
            {"code": "H101", "name": "Mount Sinai Pulmonary & Respiratory Center", "accepted_updates": 5},
            {"code": "H105", "name": "Johns Hopkins Clinical AI & Infectious Disease Center", "accepted_updates": 3},
        ]),
        "total_updates_reviewed": 8,
        "accepted_updates_count": 8,
        "quarantined_prevented_count": 0,
        "security_verdict": "REVIEWED_AND_AGGREGATED",
        "prevention_summary": "All 8 incoming updates passed L0-L5 security verification. Coordinate-Median robust aggregation committed without anomalies.",
        "accuracy_score": 95.2,
        "loss_score": 0.128,
        "model_weights_hash": "sha256-pulm-h101-sinai-9f8a",
    },
    {
        "disease_domain": "METABOLIC_DIABETES",
        "display_name": "Type-2 Diabetes & Endocrine Biomarkers",
        "model_version": "v3.2-metabolic",
        "round_number": 21,
        "aggregation_algorithm": "Robust Trimmed-Mean",
        "contributing_hospitals_json": json.dumps([
            {"code": "H102", "name": "Joslin Diabetes Center & Metabolic Institute", "accepted_updates": 6},
            {"code": "H105", "name": "Johns Hopkins Clinical AI & Infectious Disease Center", "accepted_updates": 2},
        ]),
        "total_updates_reviewed": 9,
        "accepted_updates_count": 8,
        "quarantined_prevented_count": 1,
        "security_verdict": "POISONING_ATTEMPT_PREVENTED",
        "prevention_summary": "FedSentinel L2/L4 defense intercepted and quarantined 1 malicious scaling backdoor update (+25.0 scale gradient drift). Safely isolated update to PREVENT corrupting global diabetes predictions across all other member hospitals.",
        "accuracy_score": 94.4,
        "loss_score": 0.149,
        "model_weights_hash": "sha256-meta-h102-joslin-3d8a",
    },
    {
        "disease_domain": "CARDIOMETABOLIC",
        "display_name": "Cardiometabolic & Acute Coronary Syndrome",
        "model_version": "v2.0-cardiac",
        "round_number": 20,
        "aggregation_algorithm": "Coordinate-Median",
        "contributing_hospitals_json": json.dumps([
            {"code": "H103", "name": "Cleveland Clinic Cardiovascular AI Enclave", "accepted_updates": 5},
            {"code": "H101", "name": "Mount Sinai Pulmonary & Respiratory Center", "accepted_updates": 2},
        ]),
        "total_updates_reviewed": 7,
        "accepted_updates_count": 7,
        "quarantined_prevented_count": 0,
        "security_verdict": "REVIEWED_AND_AGGREGATED",
        "prevention_summary": "Holdout loss trajectory verified across cardiac validation manifold. Zero data leakage detected.",
        "accuracy_score": 92.8,
        "loss_score": 0.182,
        "model_weights_hash": "sha256-card-h103-cleveland-7c1e",
    },
    {
        "disease_domain": "DERMATOLOGIC",
        "display_name": "Dermatologic Dysplastic & Melanoma Lesions",
        "model_version": "v1.7-derm",
        "round_number": 19,
        "aggregation_algorithm": "Coordinate-Median",
        "contributing_hospitals_json": json.dumps([
            {"code": "H104", "name": "Memorial Sloan Kettering Dermatopathology Enclave", "accepted_updates": 4},
            {"code": "H105", "name": "Johns Hopkins Clinical AI & Infectious Disease Center", "accepted_updates": 2},
        ]),
        "total_updates_reviewed": 6,
        "accepted_updates_count": 6,
        "quarantined_prevented_count": 0,
        "security_verdict": "REVIEWED_AND_AGGREGATED",
        "prevention_summary": "Counterfactual shadow validation confirmed non-negative delta-accuracy (Delta-Acc >= 0). Safely aggregated.",
        "accuracy_score": 93.1,
        "loss_score": 0.168,
        "model_weights_hash": "sha256-derm-h104-msk-1a4f",
    },
    {
        "disease_domain": "CONSENSUS_MULTI",
        "display_name": "Unified Multi-Disease Federated Consensus",
        "model_version": "v4.5-unified",
        "round_number": 21,
        "aggregation_algorithm": "Coordinate-Median",
        "contributing_hospitals_json": json.dumps([
            {"code": "H101", "name": "Mount Sinai Pulmonary & Respiratory Center", "accepted_updates": 5},
            {"code": "H102", "name": "Joslin Diabetes Center & Metabolic Institute", "accepted_updates": 6},
            {"code": "H103", "name": "Cleveland Clinic Cardiovascular AI Enclave", "accepted_updates": 5},
            {"code": "H104", "name": "Memorial Sloan Kettering Dermatopathology Enclave", "accepted_updates": 4},
            {"code": "H105", "name": "Johns Hopkins Clinical AI & Infectious Disease Center", "accepted_updates": 5},
        ]),
        "total_updates_reviewed": 26,
        "accepted_updates_count": 25,
        "quarantined_prevented_count": 1,
        "security_verdict": "POISONING_ATTEMPT_PREVENTED",
        "prevention_summary": "Consortium model aggregated across 25 verified hospital updates from all 5 specialized enclaves. 1 compromised update neutralized by FedSentinel quarantine to preserve cross-institutional diagnostic integrity.",
        "accuracy_score": 95.8,
        "loss_score": 0.119,
        "model_weights_hash": "sha256-unified-consortium-8b2c",
    },
]

for upd in DISEASE_UPDATES_SEED:
    db.add(AggregatedDiseaseUpdate(**upd))

db.commit()
print("Consortium Aggregated Global Disease Updates successfully updated for all 5 new hospitals!")
db.close()
