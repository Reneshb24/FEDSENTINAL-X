import base64
import io
import json
import requests
from PIL import Image, ImageDraw

BASE_URL = "http://127.0.0.1:8000"

s = requests.Session()
s.trust_env = False  # Avoid proxy loop

print("======================================================================")
print("FedSentinel-X Full Consortium & Multi-Disease Verification Test")
print("======================================================================")

# 1. Authenticate All 5 Hospitals and Super Admin
HOSPITALS = [
    {"code": "H101", "name": "Mount Sinai Pulmonary & Respiratory Center", "email": "admin@h101-sinai.org", "pwd": "Hospital123!"},
    {"code": "H102", "name": "Joslin Diabetes Center & Metabolic Institute", "email": "admin@h102-joslin.org", "pwd": "Hospital123!"},
    {"code": "H103", "name": "Cleveland Clinic Cardiovascular AI Enclave", "email": "admin@h103-cleveland.org", "pwd": "Hospital123!"},
    {"code": "H104", "name": "Memorial Sloan Kettering Dermatopathology Enclave", "email": "admin@h104-msk.org", "pwd": "Hospital123!"},
    {"code": "H105", "name": "Johns Hopkins Clinical AI & Infectious Disease Center", "email": "admin@h105-hopkins.org", "pwd": "Hospital123!"},
]

tokens = {}

print("\n--- 1. Testing Hospital Enclave Authentication ---")
for h in HOSPITALS:
    resp = s.post(f"{BASE_URL}/api/v1/auth/login", json={"email": h["email"], "password": h["pwd"]})
    assert resp.status_code == 200, f"Login failed for {h['code']}: {resp.text}"
    token = resp.json()["access_token"]
    tokens[h["code"]] = token
    # Verify profile
    p_resp = s.get(f"{BASE_URL}/api/v1/hospital/me", headers={"Authorization": f"Bearer {token}"})
    assert p_resp.status_code == 200, f"Profile failed for {h['code']}: {p_resp.text}"
    p_data = p_resp.json()
    print(f"  [PASS] {h['code']}: {p_data['name']} (Status: {p_data['status']}, Eligible: {p_data.get('is_eligible')})")

# Login Super Admin
admin_resp = s.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "admin@fedsentinel.local", "password": "Admin123!"})
assert admin_resp.status_code == 200, f"Admin login failed: {admin_resp.text}"
admin_token = admin_resp.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}
print("  [PASS] Super Admin: Authenticated successfully.")

# 2. Check Consortium Aggregated Global Updates for Different Diseases
print("\n--- 2. Verifying Consortium Stored Aggregated Disease Updates ---")
agg_resp = s.get(f"{BASE_URL}/api/v1/hospital/disease-updates", headers={"Authorization": f"Bearer {tokens['H101']}"})
assert agg_resp.status_code == 200, f"Failed to get disease updates: {agg_resp.text}"
agg_data = agg_resp.json()
print(f"  Found {len(agg_data['updates'])} global disease models:")
for upd in agg_data["updates"]:
    print(f"    - Domain: {upd['disease_domain']} | Model: {upd['display_name']} ({upd['model_version']}) | Verdict: {upd['security_verdict']} | Accuracy: {upd['accuracy_score']}%")

# 3. Test Local Training Submission from Hospital Enclaves
print("\n--- 3. Testing Hospital Local Training Execution ---")
# Get active federation
fed_resp = s.get(f"{BASE_URL}/api/v1/federations", headers=admin_headers)
assert fed_resp.status_code == 200, f"Failed to get federations: {fed_resp.text}"
feds = fed_resp.json()
target_fed = feds[0]
fed_id = target_fed["id"]

# Get real dataset for H101
ds_resp = s.get(f"{BASE_URL}/api/v1/hospital/datasets", headers={"Authorization": f"Bearer {tokens['H101']}"})
assert ds_resp.status_code == 200, f"Failed to get datasets: {ds_resp.text}"
datasets = ds_resp.json()
assert len(datasets) > 0, "No datasets found for H101"
target_ds = datasets[0]
ds_id = target_ds["id"]
ds_ver = "1.0.0"
print(f"  H101 Active Clinical Dataset: {target_ds['name']} (ID={ds_id[:8]}..., Type={target_ds['dataset_type']})")

# Run training in pre-flight mode for H101
train_payload = {
    "federation_id": fed_id,
    "round_id": "PRE_FLIGHT_TEST",
    "dataset_id": ds_id,
    "dataset_version": ds_ver,
}
t_resp = s.post(f"{BASE_URL}/api/v1/hospital/training", json=train_payload, headers={"Authorization": f"Bearer {tokens['H101']}"})
assert t_resp.status_code == 201, f"Training failed: {t_resp.text}"
t_data = t_resp.json()
print(f"  [PASS] H101 Local In-Situ Training: UpdateID={t_data['update_id']}, SecurityStatus={t_data['security_status']}, Loss={t_data['training_loss']:.4f}, Hash={t_data['artifact_hash'][:16]}...")

# 4. Multi-Modal Prediction Testing Across Hospitals
print("\n--- 4. Testing Multi-Modal Clinical Diagnostic Predictions ---")

def create_chest_xray():
    img = Image.new("L", (256, 256), color=15)
    draw = ImageDraw.Draw(img)
    # Thoracic silhouette
    draw.ellipse([20, 20, 236, 236], fill=100)
    # Bilateral lung fields (radiolucent = darker)
    draw.ellipse([35, 40, 115, 200], fill=50)
    draw.ellipse([141, 40, 221, 200], fill=50)
    # Infiltrate opacity in right lower quadrant (consolidation = bright)
    draw.ellipse([45, 120, 110, 190], fill=170)
    # Spine and mediastinum (radiopaque = bright)
    draw.rectangle([115, 30, 141, 230], fill=180)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

def create_skull_xray():
    img = Image.new("L", (256, 256), color=10)
    draw = ImageDraw.Draw(img)
    draw.ellipse([35, 25, 221, 215], fill=70, outline=220, width=8)
    draw.rectangle([60, 160, 196, 235], fill=140, outline=200, width=5)
    draw.ellipse([55, 45, 201, 165], fill=50)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

def create_dermoscopy_lesion():
    img = Image.new("RGB", (256, 256), color=(180, 140, 120))
    draw = ImageDraw.Draw(img)
    draw.polygon([(90, 70), (180, 85), (205, 150), (160, 195), (105, 180), (70, 120)], fill=(35, 20, 25), outline=(15, 10, 12))
    draw.ellipse([110, 95, 155, 140], fill=(70, 30, 20))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

def create_non_medical_image():
    img = Image.new("RGB", (256, 256), color=(255, 100, 20))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 140, 256, 256], fill=(0, 180, 255))
    draw.ellipse([100, 70, 156, 126], fill=(255, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

# Test 4.1: Chest X-ray from H101 (Mount Sinai Pulmonary)
cxr_b64 = create_chest_xray()
p1 = s.post(f"{BASE_URL}/api/v1/hospital/predict", json={
    "modality": "IMAGE",
    "condition": "PULMONARY_IMAGE",
    "image_data": cxr_b64,
}, headers={"Authorization": f"Bearer {tokens['H101']}"})
assert p1.status_code == 200, f"Prediction 1 failed: {p1.text}"
res1 = p1.json()
print(f"\n  [Test 4.1 - Chest X-Ray at H101]:")
print(f"    Prediction: {res1['prediction']}")
print(f"    Confidence: {res1['probability']}% | Risk Tier: {res1['risk_level']}")
print(f"    Anatomy / Disease Domain: {res1['disease_domain']}")
assert "Pneumonia" in res1["prediction"] or "Infiltration" in res1["prediction"], f"Expected pneumonia, got {res1['prediction']}"
assert res1["probability"] > 80.0, f"Expected high confidence, got {res1['probability']}"

# Test 4.2: Skull X-ray at H101 (Mount Sinai Pulmonary) - MUST NOT predict lung disease!
skull_b64 = create_skull_xray()
p2 = s.post(f"{BASE_URL}/api/v1/hospital/predict", json={
    "modality": "IMAGE",
    "condition": "PULMONARY_IMAGE",
    "image_data": skull_b64,
}, headers={"Authorization": f"Bearer {tokens['H101']}"})
assert p2.status_code == 200, f"Prediction 2 failed: {p2.text}"
res2 = p2.json()
print(f"\n  [Test 4.2 - Skull / Cranial Radiograph at H101 (Safety Screening)]:")
print(f"    Prediction: {res2['prediction']}")
print(f"    Probability: {res2['probability']}% | Risk Tier: {res2['risk_level']}")
print(f"    Out-of-Distribution / Non-Thoracic: {res2['is_out_of_distribution']}")
assert "Cranial" in res2["prediction"] or "Skull" in res2["prediction"], f"Expected cranial scan recognition, got: {res2['prediction']}"
assert res2["probability"] == 0.0, f"Expected 0.0% probability for lung match on skull, got {res2['probability']}"
assert "Pneumonia" not in res2["prediction"], "FALSE PREDICTION: Predicted pneumonia on skull!"

# Test 4.3: Dermoscopy Lesion at H104 (MSK Derm)
derm_b64 = create_dermoscopy_lesion()
p3 = s.post(f"{BASE_URL}/api/v1/hospital/predict", json={
    "modality": "IMAGE",
    "condition": "DERMATOLOGIC",
    "image_data": derm_b64,
}, headers={"Authorization": f"Bearer {tokens['H104']}"})
assert p3.status_code == 200, f"Prediction 3 failed: {p3.text}"
res3 = p3.json()
print(f"\n  [Test 4.3 - Cutaneous Dermoscopy Scan at H104]:")
print(f"    Prediction: {res3['prediction']}")
print(f"    Confidence: {res3['probability']}% | Risk Tier: {res3['risk_level']}")
assert "Cutaneous" in res3["prediction"] or "Melanoma" in res3["prediction"] or "Lesion" in res3["prediction"]

# Test 4.4: Diabetes Clinical Notes & Vitals at H102 (Joslin Diabetes)
p4 = s.post(f"{BASE_URL}/api/v1/hospital/predict", json={
    "modality": "TEXT",
    "condition": "METABOLIC_DIABETES",
    "clinical_text": "Patient presents with persistent polyuria, polydipsia, blurred vision, fasting glucose 218 mg/dL, and HbA1c 9.4%. History of metabolic syndrome.",
}, headers={"Authorization": f"Bearer {tokens['H102']}"})
assert p4.status_code == 200, f"Prediction 4 failed: {p4.text}"
res4 = p4.json()
print(f"\n  [Test 4.4 - Clinical Diabetes Text & Vitals at H102]:")
print(f"    Prediction: {res4['prediction']}")
print(f"    Confidence: {res4['probability']}% | Risk Tier: {res4['risk_level']}")
assert "Diabetes" in res4["prediction"]
assert res4["probability"] > 85.0

# Test 4.5: Cardiovascular Acute Coronary Syndrome at H103 (Cleveland Clinic)
p5 = s.post(f"{BASE_URL}/api/v1/hospital/predict", json={
    "modality": "TEXT",
    "condition": "CARDIOMETABOLIC",
    "clinical_text": "Patient with sudden onset crushing substernal chest pain radiating to left arm and jaw, severe diaphoresis, dyspnea, and elevated troponin T.",
}, headers={"Authorization": f"Bearer {tokens['H103']}"})
assert p5.status_code == 200, f"Prediction 5 failed: {p5.text}"
res5 = p5.json()
print(f"\n  [Test 4.5 - Acute Coronary Syndrome at H103]:")
print(f"    Prediction: {res5['prediction']}")
print(f"    Confidence: {res5['probability']}% | Risk Tier: {res5['risk_level']}")
assert "Coronary" in res5["prediction"] or "Cardiovascular" in res5["prediction"]
assert res5["probability"] > 85.0

# Test 4.6: Non-Medical Image (Sunset Beach)
beach_b64 = create_non_medical_image()
p6 = s.post(f"{BASE_URL}/api/v1/hospital/predict", json={
    "modality": "IMAGE",
    "condition": "AUTO_DETECT",
    "image_data": beach_b64,
}, headers={"Authorization": f"Bearer {tokens['H105']}"})
assert p6.status_code == 200, f"Prediction 6 failed: {p6.text}"
res6 = p6.json()
print(f"\n  [Test 4.6 - Non-Medical Image at H105 (OOD Rejection)]:")
print(f"    Prediction: {res6['prediction']}")
print(f"    Risk Tier: {res6['risk_level']}")
print(f"    Out-of-Distribution Detected: {res6['is_out_of_distribution']}")
assert res6["is_out_of_distribution"] is True
assert "Inconclusive" in res6["prediction"] or "Out-of-Distribution" in res6["prediction"]

print("\n======================================================================")
print("ALL MULTI-HOSPITAL & MULTI-DISEASE PREDICTION TESTS PASSED!")
print("======================================================================")
