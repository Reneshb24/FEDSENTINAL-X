import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from backend.main import app
from backend.storage.database import SessionLocal
from backend.storage.models import FederationRound, Dataset

client = TestClient(app)
db = SessionLocal()

r7 = db.query(FederationRound).filter(FederationRound.round_number == 7).first()
round_id = r7.id
fed_id = r7.federation_id

# 1. Login as H21 and train
res21 = client.post("/api/auth/login", json={"email": "admin@h21.local", "password": "Hospital123!"})
token21 = res21.json()["access_token"]
headers21 = {"Authorization": f"Bearer {token21}"}

dsets21 = client.get("/api/v1/hospital/datasets", headers=headers21).json()
ds21 = dsets21[0]
print("H21 dataset:", ds21["name"], "id:", ds21["id"], "v3 id:", ds21["versions"][-1]["id"])

# Submit local training for H21
train_res21 = client.post(
    "/api/v1/hospital/training",
    headers=headers21,
    json={
        "federation_id": fed_id,
        "round_id": round_id,
        "dataset_id": ds21["id"],
        "dataset_version": "v3",
    }
)
print("H21 training response:", train_res21.status_code)
if train_res21.status_code != 201:
    print("Error:", train_res21.text)

# 2. Login as H01 and train
res01 = client.post("/api/auth/login", json={"email": "admin@demohospital.local", "password": "Hospital123!"})
token01 = res01.json()["access_token"]
headers01 = {"Authorization": f"Bearer {token01}"}

dsets01 = client.get("/api/v1/hospital/datasets", headers=headers01).json()
ds01 = dsets01[0]
print("H01 dataset:", ds01["name"], "id:", ds01["id"])

train_res01 = client.post(
    "/api/v1/hospital/training",
    headers=headers01,
    json={
        "federation_id": fed_id,
        "round_id": round_id,
        "dataset_id": ds01["id"],
        "dataset_version": "v3",
    }
)
print("H01 training response:", train_res01.status_code)
if train_res01.status_code != 201:
    print("Error:", train_res01.text)

db.close()
