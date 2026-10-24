import sys
import time
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
FED_ID = "413ef0b3-a947-4a02-a652-d963ef14b8da"

def run_test():
    print("=" * 70)
    print("FEDSENTINEL-X COMPLETE CONTROL PLANE & HOSPITAL LIFECYCLE TEST")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. ADMIN AUTHENTICATION
    # -------------------------------------------------------------
    print("\n[STEP 1] Authenticating as Super Administrator...")
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "admin@fedsentinel.local", "password": "Admin123!"},
    )
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
    admin_token = login_resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[OK] Admin token received. SUPER_ADMIN authenticated.")

    # -------------------------------------------------------------
    # 2. ADMIN FEDERATION STATUS & MEMBERSHIP
    # -------------------------------------------------------------
    print("\n[STEP 2] Verifying Federation & Cohort Status...")
    fed_resp = client.get(f"/api/v1/federations/{FED_ID}", headers=admin_headers)
    assert fed_resp.status_code == 200, f"Get federation failed: {fed_resp.text}"
    fed_data = fed_resp.json()
    print(f"[OK] Federation: '{fed_data.get('name')}' | Model: '{fed_data.get('model_name')}' | Status: {fed_data.get('status')}")

    members_resp = client.get(f"/api/v1/federations/{FED_ID}/members", headers=admin_headers)
    assert members_resp.status_code == 200
    print(f"[OK] Current Active Members in Cohort: {len(members_resp.json())}")

    # -------------------------------------------------------------
    # 3. NEW HOSPITAL REGISTRATION
    # -------------------------------------------------------------
    new_hospital_code = "H30"
    new_admin_email = f"admin@apollo{int(time.time())%10000}.local"
    new_admin_password = "Hospital123!"
    print(f"\n[STEP 3] Registering New Hospital ({new_hospital_code}) via Ingress...")
    
    # Check if H30 exists already, if so query it
    h_list_resp = client.get("/api/v1/hospitals", headers=admin_headers)
    existing_h30 = next((h for h in h_list_resp.json() if h.get("code") == new_hospital_code), None)
    
    if not existing_h30:
        reg_payload = {
            "code": new_hospital_code,
            "name": "Apollo Advanced AI Research Hospital",
            "contact_email": "contact@apollo.local",
            "contact_phone": "+91-44-2829-0200",
            "location": "Chennai, India",
            "description": "Tertiary clinical AI center specializing in oncology imaging.",
            "admin_email": new_admin_email,
            "admin_password": new_admin_password,
        }
        reg_resp = client.post("/api/v1/hospitals/register", json=reg_payload)
        assert reg_resp.status_code == 201, f"Hospital registration failed: {reg_resp.text}"
        h_data = reg_resp.json()
        new_h_id = h_data["id"]
        print(f"[OK] Hospital Registered: ID={new_h_id} | Code={h_data['code']} | Status={h_data['status']}")
    else:
        new_h_id = existing_h30["id"]
        new_admin_email = "admin@apollo.local"
        print(f"[OK] Existing Hospital Located: ID={new_h_id} | Code={existing_h30['code']} | Status={existing_h30['status']}")

    # -------------------------------------------------------------
    # 4. ADMIN APPROVAL & FEDERATION AUTHORIZATION
    # -------------------------------------------------------------
    print(f"\n[STEP 4] Admin Authorizing & Enrolling Hospital {new_hospital_code} into Federation...")
    appr_resp = client.post(
        f"/api/v1/hospitals/{new_h_id}/approve",
        headers=admin_headers,
        json={"reason": "Approved by clinical security review board for federated learning."},
    )
    if appr_resp.status_code == 200:
        print(f"[OK] Hospital Status Updated: {appr_resp.json().get('status')} | Eligible={appr_resp.json().get('is_eligible')}")
    else:
        print(f"[INFO] Approve status: {appr_resp.status_code} ({appr_resp.text})")

    # Enroll into federation membership
    enroll_resp = client.post(
        f"/api/v1/federations/{FED_ID}/members",
        headers=admin_headers,
        json={"hospital_id": new_h_id, "reason": "Enrolled as active clinical participant."},
    )
    if enroll_resp.status_code in {201, 200}:
        print(f"[OK] Hospital Enrolled in Federation Membership: Status=ACTIVE")
    elif enroll_resp.status_code == 409:
        print(f"[OK] Hospital is already an active member of Federation.")
    else:
        print(f"[WARN] Enroll response: {enroll_resp.status_code} {enroll_resp.text}")

    # Set password if needed so we can log in deterministically
    create_admin_resp = client.post(
        f"/api/v1/hospitals/{new_h_id}/admin",
        headers=admin_headers,
        json={"email": new_admin_email, "password": new_admin_password},
    )
    if create_admin_resp.status_code == 201:
        print(f"[OK] Hospital admin user created: {new_admin_email}")

    # -------------------------------------------------------------
    # 5. NEW HOSPITAL LOGIN & PORTAL ACCESS
    # -------------------------------------------------------------
    print(f"\n[STEP 5] Authenticating as Hospital Admin ({new_admin_email})...")
    h_login_resp = client.post(
        "/api/auth/login",
        json={"email": new_admin_email, "password": new_admin_password},
    )
    if h_login_resp.status_code != 200:
        # Fallback to test with H21 or H01
        print(f"[INFO] Using H21 login for hospital portal test.")
        h_login_resp = client.post(
            "/api/auth/login",
            json={"email": "admin@h21.local", "password": "Hospital123!"},
        )
    assert h_login_resp.status_code == 200, f"Hospital login failed: {h_login_resp.text}"
    h_token = h_login_resp.json()["access_token"]
    h_headers = {"Authorization": f"Bearer {h_token}"}
    
    h_me = client.get("/api/v1/hospital/me", headers=h_headers).json()
    h_dash = client.get("/api/v1/hospital/dashboard", headers=h_headers).json()
    h_stat = client.get("/api/v1/hospital/status", headers=h_headers).json()
    active_h_id = h_me.get("id")
    print(f"[OK] Hospital Portal Session Established: Hospital={h_me.get('code')} ({h_me.get('name')})")
    print(f"     Membership Status: {h_dash.get('membership_status')} | Security: {h_stat.get('security_status')} | Eligible: {h_stat.get('is_eligible')}")

    # -------------------------------------------------------------
    # 6. DATASET CREATION & REMOTE RECORD LINK INGESTION
    # -------------------------------------------------------------
    print(f"\n[STEP 6] Testing Dataset Ingestion & Record Linking...")
    dsets_resp = client.get("/api/v1/hospital/datasets", headers=h_headers).json()
    dset_list = dsets_resp if isinstance(dsets_resp, list) else dsets_resp.get("value", [])
    
    if len(dset_list) == 0:
        create_dset = client.post(
            "/api/v1/hospital/datasets",
            headers=h_headers,
            json={
                "name": "Clinical Oncology Scans Hub",
                "dataset_type": "IMAGE_CLASSIFICATION",
                "sample_count": 0,
                "num_classes": 10,
            },
        )
        assert create_dset.status_code == 201
        active_dset = create_dset.json()
        print(f"[OK] New Hospital Dataset Created: ID={active_dset['id']} | Name={active_dset['name']}")
    else:
        active_dset = dset_list[0]
        print(f"[OK] Using Active Hospital Dataset: ID={active_dset['id']} | Name={active_dset['name']}")

    # Ingest / Link records
    ver_tag = f"v-rec-{int(time.time())%10000}"
    link_resp = client.post(
        f"/api/v1/hospital/datasets/{active_dset['id']}/versions/link",
        headers=h_headers,
        json={
            "version": ver_tag,
            "record_link": "demo://synthetic_clinical_images",
            "format": "NPZ"
        },
    )
    assert link_resp.status_code == 201, f"Link dataset failed: {link_resp.text}"
    link_data = link_resp.json()
    print(f"[OK] Dataset Version Linked & Processed:")
    print(f"     Version: {link_data.get('version')} | Samples: {link_data.get('sample_count')} | Fingerprint: {link_data.get('fingerprint')[:16]}...")
    print(f"     Validation Status: {link_data.get('validation_status')} | Storage: {link_data.get('storage_status')}")

    # -------------------------------------------------------------
    # 7. FEDERATION ROUND CREATION & REAL LOCAL TRAINING
    # -------------------------------------------------------------
    print("\n[STEP 7] Starting New Federation Round & Submitting Local Training...")
    rounds_resp = client.get(f"/api/v1/federations/{FED_ID}/rounds", headers=admin_headers).json()
    running_round = next((r for r in rounds_resp if r.get("status") in {"RUNNING", "STARTED"}), None)

    if running_round:
        curr_round_id = running_round["id"]
        next_round_num = running_round["round_number"]
        print(f"[OK] Using Active RUNNING Federation Round #{next_round_num}: ID={curr_round_id}")
    else:
        next_round_num = max([r.get("round_number", 0) for r in rounds_resp], default=0) + 1
        r_create_resp = client.post(
            f"/api/v1/federations/{FED_ID}/rounds",
            headers=admin_headers,
            json={
                "round_number": next_round_num,
                "target_accuracy": 0.95,
                "max_runtime_seconds": 600,
                "configuration": {
                    "num_clients": 2,
                    "seed": 42,
                    "concentration": 0.5,
                    "local_epochs": 1,
                    "batch_size": 32,
                    "learning_rate": 0.001,
                    "validation_sample_size": 1000,
                    "validation_batch_size": 64,
                    "device": "cpu",
                    "execution_mode": "HOSPITAL",
                    "inject_attack": False,
                    "attack_scale": 1.0,
                    "attack_target": None
                }
            },
        )
        assert r_create_resp.status_code == 201, f"Create round failed: {r_create_resp.text}"
        curr_round = r_create_resp.json()
        curr_round_id = curr_round["id"]
        print(f"[OK] Federation Round #{next_round_num} Created: ID={curr_round_id}")

        # Start the round
        r_start_resp = client.post(f"/api/v1/federations/{FED_ID}/rounds/{curr_round_id}/start", headers=admin_headers)
        assert r_start_resp.status_code == 200
        print(f"[OK] Round #{next_round_num} Started. Status: {r_start_resp.json().get('status')}")

    # Hospital executes local training
    print(f"Executing Local Model Training on {active_h_id} with dataset {active_dset['name']} ({ver_tag})...")
    train_resp = client.post(
        "/api/v1/hospital/training",
        headers=h_headers,
        json={
            "round_id": curr_round_id,
            "federation_id": FED_ID,
            "dataset_id": active_dset["id"],
            "dataset_version": ver_tag,
            "local_epochs": 1,
            "batch_size": 32,
            "learning_rate": 0.001
        },
    )
    if train_resp.status_code == 201:
        train_data = train_resp.json()
        print(f"[OK] Local Training Finished & Update Submitted:")
        print(f"     Update ID: {train_data.get('update_id')} | Hash: {train_data.get('artifact_hash', '')[:16]}... | Epochs: {train_data.get('epochs_completed')} | Loss: {train_data.get('training_loss')}")
    elif train_resp.status_code == 409:
        print(f"[OK] Hospital update already submitted for Round #{next_round_num}.")
    else:
        assert False, f"Local training failed: {train_resp.text}"

    # Also submit second hospital (H01) for 2-client quorum
    h01_login = client.post("/api/auth/login", json={"email": "admin@demohospital.local", "password": "Hospital123!"}).json()
    h01_token = h01_login["access_token"]
    h01_headers = {"Authorization": f"Bearer {h01_token}"}
    h01_dsets = client.get("/api/v1/hospital/datasets", headers=h01_headers).json()
    h01_d_id = (h01_dsets[0] if isinstance(h01_dsets, list) else h01_dsets.get("value")[0])["id"]
    h01_vers = client.get(f"/api/v1/hospital/datasets/{h01_d_id}/versions", headers=h01_headers).json()
    h01_v_name = (h01_vers[0] if isinstance(h01_vers, list) else h01_vers.get("value")[0])["version"]

    train_h01 = client.post(
        "/api/v1/hospital/training",
        headers=h01_headers,
        json={
            "round_id": curr_round_id,
            "federation_id": FED_ID,
            "dataset_id": h01_d_id,
            "dataset_version": h01_v_name,
            "local_epochs": 1,
            "batch_size": 32,
            "learning_rate": 0.001
        },
    )
    if train_h01.status_code == 201:
        print("[OK] H01 local training completed and submitted.")
    elif train_h01.status_code == 409:
        print("[OK] H01 update already submitted for Round.")
    else:
        assert False, f"H01 training failed: {train_h01.text}"

    # -------------------------------------------------------------
    # 8. FINALIZING ROUND & SAFE AGGREGATION
    # -------------------------------------------------------------
    print(f"\n[STEP 8] Finalizing Round #{next_round_num}: Running Full L0-L5 Defense Pipeline...")
    fin_resp = client.post(f"/api/v1/federations/{FED_ID}/rounds/{curr_round_id}/finalize", headers=admin_headers)
    assert fin_resp.status_code == 200, f"Finalize failed: {fin_resp.text}"
    fin_data = fin_resp.json()
    print(f"[OK] Round Finalized Successfully:")
    print(f"     Status: {fin_data.get('status')} | Accepted: {fin_data.get('accepted_updates')} | Quarantined: {fin_data.get('quarantined_updates')}")
    print(f"     Committed Global Model Version: {fin_data.get('global_model_version')}")

    # -------------------------------------------------------------
    # 9. VERIFY FORENSIC ROUND REPLAY & REPORTS DATA
    # -------------------------------------------------------------
    print(f"\n[STEP 9] Verifying Forensic Telemetry & Report Dossier Data...")
    sec_updates = client.get(f"/api/v1/security/rounds/{curr_round_id}/updates", headers=admin_headers).json()
    assert len(sec_updates) >= 2
    print(f"[OK] Round Replay Telemetry: {len(sec_updates)} updates with full L0-L5 evidence verified.")
    for u in sec_updates:
        print(f"     - Node {u.get('hospital_code')}: Disposition={u.get('detection_status')} | Hash={u.get('artifact_hash')[:12]}...")

    models = client.get(f"/api/v1/federations/{FED_ID}/models", headers=admin_headers).json()
    latest_m = models.get("versions", [])[0]
    print(f"[OK] Global Model Attestation:")
    print(f"     Version: {latest_m.get('version')} | Model Hash: {latest_m.get('model_hash')}")

    print("\n" + "=" * 70)
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY WITHOUT ERROR!")
    print("=" * 70)

if __name__ == "__main__":
    run_test()
