import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

res1 = client.post("/api/auth/login", json={"email": "admin@fedsentinel.local", "password": "Admin123!"})
print("Admin login status:", res1.status_code, "role:", res1.json().get("user", {}).get("role"))

res2 = client.post("/api/auth/login", json={"email": "admin@h21.local", "password": "Hospital123!"})
print("Hospital H21 login status:", res2.status_code, "role:", res2.json().get("user", {}).get("role"), "hosp_id:", res2.json().get("user", {}).get("hospital_id"))
