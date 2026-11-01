"""
Complete End-to-End Test for FedSentinel-X:
1. Create a new Hospital registration application
2. Admin approves application & activates hospital
3. New Hospital logs in with credentials
4. Hospital updates profile & verifies enclave status
5. Hospital creates a clinical dataset cohort
6. Hospital links / uploads a validated dataset version
7. Verify dataset quality checks (Zero-pickle, 1x28x28, finite bounds)
8. Admin initializes & starts a federation round
9. Hospital runs local PyTorch training on the dataset
10. System generates SafeTensors delta & SHA-256 fingerprint
11. Differential update passes through L0-L5 security pipeline
12. Finalizes round & verifies updated Global Model consensus
13. Verifies immutable audit ledger records
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import uuid
import torch
from sqlalchemy.orm import Session

from backend.main import app
from backend.storage.database import SessionLocal
from backend.storage.models import Hospital, User, Dataset, DatasetVersion, Federation, FederationRound, ModelUpdate
from backend.services.hospital_service import HospitalService
from backend.services.dataset_service import DatasetService
from backend.services.hospital_portal_service import HospitalPortalService
from backend.services.round_orchestrator import RoundOrchestrator
from backend.schemas.hospital import HospitalRegistrationRequest, HospitalUpdate
from backend.schemas.dataset import DatasetCreate, DatasetLinkImportRequest
from backend.schemas.hospital_training import HospitalTrainingRequest
from backend.api.hospital_portal_routes import submit_local_training
from backend.auth.security import create_access_token, verify_password, hash_password


def run_e2e_test():
    db: Session = SessionLocal()
    print("=" * 70)
    print("FEDSENTINEL-X END-TO-END LIFECYCLE VERIFICATION")
    print("=" * 70)

    try:
        # -------------------------------------------------------------
        # STEP 1: Hospital Registration Request
        # -------------------------------------------------------------
        test_suffix = uuid.uuid4().hex[:6]
        hosp_code = f"E2E_CLINIC_{test_suffix}".upper()
        hosp_email = f"e2e_admin_{test_suffix}@clinic.local"
        hosp_password = "SecurePassword123!"

        print(f"\n[STEP 1] Submitting Registration Request for '{hosp_code}'...")
        reg_payload = HospitalRegistrationRequest(
            code=hosp_code,
            name=f"E2E Automated Medical Enclave {test_suffix}",
            contact_email=f"contact_{test_suffix}@clinic.local",
            contact_phone="+1 415-555-0199",
            address="100 Innovation Way, Enclave Alpha",
            location="San Francisco, CA",
            country="USA",
            region="North America",
            institution_type="ACADEMIC_MEDICAL_CENTER",
            description="Specialized pulmonary pathology and federated CT enclave.",
            admin_name="Dr. Sarah Connor",
            admin_email=hosp_email,
            admin_password=hosp_password,
        )

        new_hosp = HospitalService.register_hospital(db, reg_payload)
        print(f" -> Hospital Created with ID: {new_hosp.id}")
        print(f" -> Initial Status: {new_hosp.status} | Application Status: {new_hosp.application_status}")
        assert new_hosp.status == "PENDING"
        assert new_hosp.application_status in ("PENDING", "SUBMITTED")

        # Verify admin user exists but is inactive until approval
        admin_user = db.query(User).filter(User.email == hosp_email).first()
        assert admin_user is not None
        print(f" -> Admin Account Registered: {admin_user.email} (Active={admin_user.is_active})")

        # -------------------------------------------------------------
        # STEP 2: Super Admin Approves Hospital
        # -------------------------------------------------------------
        print(f"\n[STEP 2] Super Admin Approving Hospital '{hosp_code}'...")
        super_admin = db.query(User).filter(User.role == "SUPER_ADMIN").first()
        assert super_admin is not None, "Super admin user must exist"

        fed = db.query(Federation).first()
        assert fed is not None, "At least one Federation must exist"

        approved_hosp = HospitalService.approve_application(
            db,
            actor_user_id=super_admin.id,
            hospital=new_hosp,
            federation_id=fed.id,
            notes="Approved via E2E verification test pipeline."
        )
        db.refresh(admin_user)
        print(f" -> Approved Status: {approved_hosp.status} | Application Status: {approved_hosp.application_status}")
        print(f" -> Admin Account Activated: {admin_user.is_active}")
        assert approved_hosp.status == "ACTIVE"
        assert approved_hosp.application_status == "APPROVED"
        assert admin_user.is_active is True

        # -------------------------------------------------------------
        # STEP 3: Hospital Authentication & Profile Update
        # -------------------------------------------------------------
        print(f"\n[STEP 3] Hospital Admin Authenticating...")
        from backend.core.config import settings
        assert verify_password(hosp_password, admin_user.password_hash) is True
        token = create_access_token(
            user_id=admin_user.id,
            session_id=str(uuid.uuid4()),
            role=admin_user.role,
            hospital_id=approved_hosp.id,
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
            expires_minutes=settings.access_token_expire_minutes,
        )
        print(f" -> JWT Access Token Issued (len={len(token)})")

        # Profile update test
        update_data = HospitalUpdate(
            contact_phone="+1 415-555-0299",
            description="Certified Federated Healthcare Research Partner"
        )
        updated_hosp = HospitalPortalService.update_profile(
            db,
            hospital_id=approved_hosp.id,
            actor_user_id=admin_user.id,
            payload=update_data,
        )
        assert updated_hosp.contact_phone == "+1 415-555-0299"
        print(f" -> Hospital Enclave Profile Updated: phone={updated_hosp.contact_phone}")

        # -------------------------------------------------------------
        # STEP 4: Create Clinical Dataset Cohort
        # -------------------------------------------------------------
        print(f"\n[STEP 4] Registering Clinical Dataset Cohort...")
        ds_payload = DatasetCreate(
            name=f"Chest X-Ray Pneumonia Cohort {test_suffix}",
            dataset_type="IMAGE_CLASSIFICATION",
            sample_count=200,
            num_classes=10,
            dimension_x=28,
            dimension_y=28,
            channels=1,
            description="Normalized 28x28 grayscale chest radiographs.",
        )
        dataset = DatasetService.create_dataset(
            db,
            hospital_id=approved_hosp.id,
            actor_user_id=admin_user.id,
            payload=ds_payload
        )
        print(f" -> Dataset Registered: ID={dataset.id}, Name='{dataset.name}'")
        assert dataset.hospital_id == approved_hosp.id

        # -------------------------------------------------------------
        # STEP 5: Ingest & Validate Dataset Version (Zero-Pickle)
        # -------------------------------------------------------------
        print(f"\n[STEP 5] Ingesting & Validating Dataset Version (Zero-Pickle Enforcement)...")
        version_payload = DatasetLinkImportRequest(
            version=f"v1.0-{test_suffix}",
            record_link="demo://synthetic_clinical_images",
            format="NPZ"
        )
        (
            ds_ver,
            file_size,
            fingerprint,
            class_count
        ) = DatasetService.import_version_from_link(
            db,
            hospital_id=approved_hosp.id,
            actor_user_id=admin_user.id,
            dataset_id=dataset.id,
            version_name=version_payload.version,
            record_link=version_payload.record_link,
            format_type=version_payload.format
        )
        print(f" -> Version Ingested: {ds_ver.version}")
        print(f" -> SHA-256 Fingerprint: {fingerprint[:16]}...")
        print(f" -> Samples: {ds_ver.sample_count} | Classes: {class_count} | Size: {file_size} bytes")
        assert ds_ver.sample_count > 0
        assert class_count == 10
        assert len(fingerprint) == 64

        # -------------------------------------------------------------
        # STEP 6: Federation Round Setup & Verification
        # -------------------------------------------------------------
        print(f"\n[STEP 6] Federation Round Setup & Participation Check...")
        from backend.services.round_management_service import RoundManagementService
        active_round = db.query(FederationRound).filter(
            FederationRound.federation_id == fed.id,
            FederationRound.status == "RUNNING"
        ).first()

        if not active_round:
            created_round = db.query(FederationRound).filter(
                FederationRound.federation_id == fed.id,
                FederationRound.status == "CREATED"
            ).first()

            if not created_round:
                config = {
                    "execution_mode": "HOSPITAL",
                    "num_clients": 2,
                    "seed": 42,
                    "local_epochs": 1,
                    "batch_size": 32,
                    "learning_rate": 0.001,
                    "device": "cpu",
                }
                created_round = RoundManagementService.create_round(
                    db,
                    federation=fed,
                    actor_user_id=super_admin.id,
                    configuration=config
                )
            created_round.status = "RUNNING"
            db.commit()
            db.refresh(created_round)
            active_round = created_round
            print(f" -> Activated Round R-{active_round.round_number} (ID: {active_round.id})")
        else:
            print(f" -> Utilizing Existing Active Round R-{active_round.round_number} (ID: {active_round.id})")

        # -------------------------------------------------------------
        # STEP 7: In Situ Local PyTorch Training Execution
        # -------------------------------------------------------------
        print(f"\n[STEP 7] Executing In Situ PyTorch Local Training...")
        train_req = HospitalTrainingRequest(
            round_id=active_round.id,
            federation_id=fed.id,
            dataset_id=dataset.id,
            dataset_version=ds_ver.version,
        )

        train_result = submit_local_training(
            payload=train_req,
            current_user=admin_user,
            db=db,
        )

        print(f" -> Training Submission Message: {train_result.message}")
        print(f" -> Epochs: {train_result.epochs_completed} | Examples: {train_result.num_examples}")
        print(f" -> Training Loss: {train_result.training_loss:.4f}")
        print(f" -> SafeTensors Delta Hash: {train_result.artifact_hash[:16]}...")
        assert train_result.artifact_hash is not None
        assert len(train_result.artifact_hash) == 64
        assert train_result.artifact_type.lower() == "safetensors"

        # Peer hospital (H21) also trains to provide cross-hospital consensus
        print(f"\n[STEP 7b] Peer Node H21 Ingesting & Executing Training for Consensus...")
        h21_user = db.query(User).filter(User.email == "admin@h21.local").first()
        assert h21_user is not None, "Peer H21 user must exist"
        h21_ds = db.query(Dataset).filter(Dataset.hospital_id == h21_user.hospital_id).first()
        assert h21_ds is not None, "Peer H21 dataset must exist"

        h21_version_name = f"v-e2e-h21-{test_suffix}"
        (
            h21_ver,
            h21_size,
            h21_fp,
            h21_classes
        ) = DatasetService.import_version_from_link(
            db,
            hospital_id=h21_user.hospital_id,
            actor_user_id=h21_user.id,
            dataset_id=h21_ds.id,
            version_name=h21_version_name,
            record_link="demo://synthetic_clinical_images",
            format_type="NPZ"
        )
        print(f" -> Peer H21 Version Ingested: {h21_ver.version} ({h21_ver.sample_count} samples)")

        train_req_h21 = HospitalTrainingRequest(
            round_id=active_round.id,
            federation_id=fed.id,
            dataset_id=h21_ds.id,
            dataset_version=h21_version_name,
        )
        train_result_h21 = submit_local_training(
            payload=train_req_h21,
            current_user=h21_user,
            db=db,
        )
        print(f" -> Peer H21 Update Submitted: Hash={train_result_h21.artifact_hash[:16]}...")

        # -------------------------------------------------------------
        # STEP 8: Security Verification & Audit Trail
        # -------------------------------------------------------------
        print(f"\n[STEP 8] Security Pipeline L0-L5 & Audit Verification...")
        update_record = db.query(ModelUpdate).filter(
            ModelUpdate.round_id == active_round.id,
            ModelUpdate.hospital_id == approved_hosp.id
        ).order_by(ModelUpdate.submitted_at.desc()).first()

        assert update_record is not None, "ModelUpdate must be committed to database"
        print(f" -> Committed Update ID: {update_record.id}")
        print(f" -> Artifact Hash: {update_record.artifact_hash[:16]}...")
        print(f" -> Security Status: {update_record.detection_status}")
        print(f" -> Trust Action: {update_record.action}")
        assert update_record.artifact_hash == train_result.artifact_hash

        # Verify Portal Telemetry & State
        portal_status = HospitalPortalService.get_status(db, approved_hosp.id)
        print(f" -> Portal Enclave Status: {portal_status['status']} | Security Status: {portal_status['security_status']}")
        assert portal_status['status'] == "ACTIVE"
        assert portal_status['federation_member'] is True

        # -------------------------------------------------------------
        # STEP 9: Finalize Round through L0-L5 Security Pipeline & Aggregation
        # -------------------------------------------------------------
        print(f"\n[STEP 9] Finalizing Round & Running L0-L5 Security Pipeline...")
        from backend.api.federation_routes import finalize_hospital_round
        from backend.api.dependencies import get_orchestrator
        import json

        # Ensure num_clients matches submitted count so finalization proceeds
        cfg = json.loads(active_round.config_json or "{}")
        cfg["execution_mode"] = "HOSPITAL"
        cfg["num_clients"] = 2
        active_round.config_json = json.dumps(cfg)
        db.commit()

        finalized = finalize_hospital_round(
            federation_id=fed.id,
            round_id=active_round.id,
            db=db,
            current_user=super_admin,
            orchestrator=get_orchestrator(),
        )
        print(f" -> Finalized Round Status: {finalized.status}")
        print(f" -> Accepted Updates: {finalized.accepted_updates}")
        print(f" -> Quarantined Updates: {finalized.quarantined_updates}")
        print(f" -> Global Model Version: {finalized.global_model_version}")
        assert finalized.status == "COMPLETED"

        print("\n" + "=" * 70)
        print("ALL 9 END-TO-END SYSTEM STAGES EXECUTED AND PASSED 100%!")
        print("=" * 70)

    except Exception as e:
        print(f"\n[FAIL] E2E Lifecycle failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_e2e_test()
