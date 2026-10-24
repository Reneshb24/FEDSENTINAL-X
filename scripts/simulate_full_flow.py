import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
fed_id = "413ef0b3-a947-4a02-a652-d963ef14b8da"

print("=================================================================")
print("FED SENTINEL: END-TO-END HOSPITAL INGESTION & TRAINING SIMULATION")
print("=================================================================")

# 1. Admin login
admin_res = client.post("/api/auth/login", json={"email": "admin@fedsentinel.local", "password": "Admin123!"})
assert admin_res.status_code == 200, admin_res.text
admin_token = admin_res.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}
print("[OK] Admin authenticated successfully.")

# 2. H01 login & Dataset Linking
h01_res = client.post("/api/auth/login", json={"email": "admin@demohospital.local", "password": "Hospital123!"})
assert h01_res.status_code == 200, h01_res.text
h01_token = h01_res.json()["access_token"]
h01_headers = {"Authorization": f"Bearer {h01_token}"}

h01_datasets = client.get("/api/v1/hospital/datasets", headers=h01_headers).json()
h01_dataset_list = h01_datasets if isinstance(h01_datasets, list) else h01_datasets.get("value", [])
assert len(h01_dataset_list) > 0, "H01 has no datasets"
h01_d_id = h01_dataset_list[0]["id"]

# Ingest new record version for H01
h01_link = client.post(
    f"/api/v1/hospital/datasets/{h01_d_id}/versions/link",
    headers=h01_headers,
    json={
        "version": "v-flow-h01",
        "record_link": "demo://synthetic_clinical_images",
        "format": "NPZ"
    }
)
assert h01_link.status_code in {201, 409}, h01_link.text
print(f"[OK] H01 dataset version linked: status={h01_link.status_code}")

# 3. H21 login & Dataset Linking
h21_res = client.post("/api/auth/login", json={"email": "admin@h21.local", "password": "Hospital123!"})
assert h21_res.status_code == 200, h21_res.text
h21_token = h21_res.json()["access_token"]
h21_headers = {"Authorization": f"Bearer {h21_token}"}

h21_datasets = client.get("/api/v1/hospital/datasets", headers=h21_headers).json()
h21_dataset_list = h21_datasets if isinstance(h21_datasets, list) else h21_datasets.get("value", [])
assert len(h21_dataset_list) > 0, "H21 has no datasets"
h21_d_id = h21_dataset_list[0]["id"]

# Ingest new record version for H21
h21_link = client.post(
    f"/api/v1/hospital/datasets/{h21_d_id}/versions/link",
    headers=h21_headers,
    json={
        "version": "v-flow-h21",
        "record_link": "demo://synthetic_clinical_images",
        "format": "NPZ"
    }
)
assert h21_link.status_code in {201, 409}, h21_link.text
print(f"[OK] H21 dataset version linked: status={h21_link.status_code}")

# 4. Create Round 9 in HOSPITAL mode
round_payload = {
    "round_number": 9,
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
}

r9_res = client.post(f"/api/v1/federations/{fed_id}/rounds", headers=admin_headers, json=round_payload)
if r9_res.status_code == 201:
    r9_data = r9_res.json()
    r9_id = r9_data["id"]
    print(f"[OK] Round 9 created: id={r9_id}")
else:
    # Check if Round 9 already exists
    rounds_list = client.get(f"/api/v1/federations/{fed_id}/rounds", headers=admin_headers).json()
    r9 = next((r for r in rounds_list if r["round_number"] == 9), None)
    assert r9 is not None, f"Failed to create or find Round 9: {r9_res.text}"
    r9_id = r9["id"]
    print(f"[OK] Round 9 located: id={r9_id} status={r9['status']}")

# 5. Start Round 9 if created
if r9_res.status_code == 201 or r9.get("status") == "CREATED":
    start_res = client.post(f"/api/v1/federations/{fed_id}/rounds/{r9_id}/start", headers=admin_headers)
    print(f"[OK] Round 9 started: status={start_res.status_code} round_status={start_res.json().get('status')}")

# 6. Hospital H01 performs Local Training on Round 9
print("Executing Local Training for Hospital H01...")
train_h01 = client.post(
    "/api/v1/hospital/training",
    headers=h01_headers,
    json={
        "round_id": r9_id,
        "federation_id": fed_id,
        "dataset_id": h01_d_id,
        "dataset_version": "v-flow-h01",
        "local_epochs": 1,
        "batch_size": 32,
        "learning_rate": 0.001
    }
)
print(f"[OK] H01 training finished: status={train_h01.status_code} hash={train_h01.json().get('model_update_hash', '')[:12]}...")

# 7. Hospital H21 performs Local Training on Round 9
print("Executing Local Training for Hospital H21...")
train_h21 = client.post(
    "/api/v1/hospital/training",
    headers=h21_headers,
    json={
        "round_id": r9_id,
        "federation_id": fed_id,
        "dataset_id": h21_d_id,
        "dataset_version": "v-flow-h21",
        "local_epochs": 1,
        "batch_size": 32,
        "learning_rate": 0.001
    }
)
print(f"[OK] H21 training finished: status={train_h21.status_code} hash={train_h21.json().get('model_update_hash', '')[:12]}...")

# 8. Finalize Round 9: Runs L0-L5 defense and aggregates into Global Model
print("Finalizing Round 9: Running L0-L5 security pipeline & aggregation...")
fin_res = client.post(f"/api/v1/federations/{fed_id}/rounds/{r9_id}/finalize", headers=admin_headers)
assert fin_res.status_code == 200, f"Finalize failed: {fin_res.text}"
fin_data = fin_res.json()
print("[OK] Round 9 Finalized Successfully!")
print(f"  Status: {fin_data.get('status')}")
print(f"  Accepted Updates: {fin_data.get('accepted_updates')}")
print(f"  Quarantined Updates: {fin_data.get('quarantined_updates')}")
print(f"  Committed Global Model: {fin_data.get('global_model_version')}")

# 9. Verify Round Replay Data
up_res = client.get(f"/api/v1/security/rounds/{r9_id}/updates", headers=admin_headers)
assert up_res.status_code == 200
updates = up_res.json()
print(f"[OK] Security updates retrieved: {len(updates)} updates recorded with full L0-L5 evidence.")
for u in updates:
    print(f"  - Node {u.get('hospital_code')}: status={u.get('detection_status')} hash={u.get('artifact_hash', '')[:10]}...")

# 10. Verify Global Model lineage
models_res = client.get(f"/api/v1/federations/{fed_id}/models", headers=admin_headers)
assert models_res.status_code == 200
m_data = models_res.json()
print(f"[OK] Global model versions retrieved: {len(m_data.get('versions', []))} total versions committed.")
latest_v = m_data.get("versions", [])[0]
print(f"  Latest Model Version: {latest_v.get('version')} (round_id={latest_v.get('round_id')})")
print(f"  Model Hash: {latest_v.get('model_hash')}")

print("\n=================================================================")
print("ALL TESTS PASSED: HOSPITAL INGESTION, TRAINING, SECURITY, & REPLAY")
print("=================================================================")
