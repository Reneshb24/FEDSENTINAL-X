import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# Login as H21
res = client.post("/api/auth/login", json={"email": "admin@h21.local", "password": "Hospital123!"})
assert res.status_code == 200, res.text
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
fed_id = "413ef0b3-a947-4a02-a652-d963ef14b8da"

# Test me
me = client.get("/api/v1/hospital/me", headers=headers)
print("GET /hospital/me:", me.status_code, me.json().get("code"), me.json().get("name"))

# Test dashboard
dash = client.get("/api/v1/hospital/dashboard", headers=headers)
print("GET /hospital/dashboard:", dash.status_code, "active_datasets:", dash.json().get("active_datasets"), "membership:", dash.json().get("membership_status"))

# Test federation rounds discovery
rounds = client.get(f"/api/v1/federations/{fed_id}/rounds", headers=headers)
print(f"GET /federations/{fed_id}/rounds:", rounds.status_code, f"found {len(rounds.json())} rounds")
if rounds.status_code == 200 and len(rounds.json()) > 0:
    latest = rounds.json()[0]
    print(f"  Latest round: #{latest.get('round_number')} status={latest.get('status')} id={latest.get('id')}")
    # Test security updates for round
    sec_up = client.get(f"/api/v1/security/rounds/{latest['id']}/updates", headers=headers)
    print(f"  GET /security/rounds/{latest['id']}/updates:", sec_up.status_code, f"found {len(sec_up.json())} updates")

# Test datasets
dsets = client.get("/api/v1/hospital/datasets", headers=headers)
dset_list = dsets.json() if isinstance(dsets.json(), list) else dsets.json().get("value", [])
print("GET /hospital/datasets:", dsets.status_code, "count:", len(dset_list))

# Test linking a record to the first active dataset
if dset_list:
    d_id = dset_list[0]["id"]
    link_res = client.post(
        f"/api/v1/hospital/datasets/{d_id}/versions/link",
        headers=headers,
        json={
            "version": "v-linked-test",
            "record_link": "demo://synthetic_records",
            "format": "NPZ"
        }
    )
    print("POST /hospital/datasets/.../versions/link:", link_res.status_code, link_res.json().get("message") or link_res.text)
