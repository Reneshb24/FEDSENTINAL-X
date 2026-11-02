import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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

print("\n--- 1. Testing Hospital Enclave Authentication & Multiple Datasets ---")
for h in HOSPITALS:
    resp = s.post(f"{BASE_URL}/api/v1/auth/login", json={"email": h["email"], "password": h["pwd"]})
    assert resp.status_code == 200, f"Login failed for {h['code']}: {resp.text}"
    token = resp.json()["access_token"]
    tokens[h["code"]] = token

    # Verify profile
    p_resp = s.get(f"{BASE_URL}/api/v1/hospital/me", headers={"Authorization": f"Bearer {token}"})
    assert p_resp.status_code == 200, f"Profile failed for {h['code']}: {p_resp.text}"
    p_data = p_resp.json()

    # Verify multiple datasets
    d_resp = s.get(f"{BASE_URL}/api/v1/hospital/datasets", headers={"Authorization": f"Bearer {token}"})
    assert d_resp.status_code == 200, f"Datasets failed for {h['code']}: {d_resp.text}"
    ds_list = d_resp.json()
    assert len(ds_list) >= 2, f"Expected at least 2 datasets for {h['code']}, found {len(ds_list)}"

    print(f"  [PASS] {h['code']}: {p_data['name']} (Datasets: {len(ds_list)}, Eligible: {p_data.get('is_eligible')})")
    for d in ds_list:
        print(f"         - {d['name']} [{d['dataset_type']}]")

# Login Super Admin
admin_resp = s.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "admin@fedsentinel.local", "password": "Admin123!"})
assert admin_resp.status_code == 200, f"Admin login failed: {admin_resp.text}"
admin_token = admin_resp.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}
print("  [PASS] Super Admin: Authenticated successfully.")

# 2. Check Consortium Aggregated Global Updates for Different Diseases
print("\n--- 2. Verifying Consortium Stored Aggregated Disease Updates & Weights ---")
agg_resp = s.get(f"{BASE_URL}/api/v1/hospital/disease-updates", headers={"Authorization": f"Bearer {tokens['H101']}"})
assert agg_resp.status_code == 200, f"Failed to get disease updates: {agg_resp.text}"
agg_data = agg_resp.json()
assert len(agg_data['updates']) == 5, f"Expected 5 disease models, found {len(agg_data['updates'])}"
print(f"  Found {len(agg_data['updates'])} global disease models:")
for upd in agg_data["updates"]:
    assert upd['model_weights_hash'].startswith("sha256-"), f"Invalid hash: {upd['model_weights_hash']}"
    print(f"    - Domain: {upd['disease_domain']} | Model: {upd['display_name']} ({upd['model_version']}) | Verdict: {upd['security_verdict']} | Hash: {upd['model_weights_hash'][:22]}...")

# 3. Test Local Training Execution Across Hospital Enclaves
print("\n--- 3. Testing Hospital Local Training Execution (Multiple Hospitals) ---")
fed_resp = s.get(f"{BASE_URL}/api/v1/federations", headers=admin_headers)
assert fed_resp.status_code == 200, f"Failed to get federations: {fed_resp.text}"
feds = fed_resp.json()
target_fed = feds[0]
fed_id = target_fed["id"]

# Run training in pre-flight mode for H101 and H102
for test_hosp in ["H101", "H102"]:
    ds_resp = s.get(f"{BASE_URL}/api/v1/hospital/datasets", headers={"Authorization": f"Bearer {tokens[test_hosp]}"})
    target_ds = ds_resp.json()[0]
    train_payload = {
        "federation_id": fed_id,
        "round_id": f"PRE_FLIGHT_{test_hosp}",
        "dataset_id": target_ds["id"],
        "dataset_version": "1.0.0",
    }
    t_resp = s.post(f"{BASE_URL}/api/v1/hospital/training", json=train_payload, headers={"Authorization": f"Bearer {tokens[test_hosp]}"})
    assert t_resp.status_code == 201, f"Training failed for {test_hosp}: {t_resp.text}"
    t_data = t_resp.json()
    print(f"  [PASS] {test_hosp} In-Situ Local Training: UpdateID={t_data['update_id']}, Status={t_data['security_status']}, Loss={t_data['training_loss']:.4f}, Hash={t_data['artifact_hash'][:16]}...")

# 4. Multi-Modal Prediction Testing Across Hospitals
print("\n--- 4. Testing Multi-Modal Clinical Diagnostic Predictions Across Enclaves ---")

def create_chest_xray():
    img = Image.new("L", (256, 256), color=15)
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, 236, 236], fill=100)
    draw.ellipse([35, 40, 115, 200], fill=50)
    draw.ellipse([141, 40, 221, 200], fill=50)
    draw.ellipse([45, 120, 110, 190], fill=170)
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
assert "Pneumonia" in res1["prediction"] or "Infiltration" in res1["prediction"]
assert res1["probability"] > 80.0

# Test 4.2: Skull X-ray at H101 (Safety Screening: MUST NOT predict lung disease!)
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
assert "Cranial" in res2["prediction"] or "Skull" in res2["prediction"]
assert res2["probability"] == 0.0
assert "Pneumonia" not in res2["prediction"], "SAFETY VIOLATION: Predicted lung disease on skull scan!"

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

# Test 4.6: Infectious Disease & Sepsis at H105 (Johns Hopkins)
p6 = s.post(f"{BASE_URL}/api/v1/hospital/predict", json={
    "modality": "TEXT",
    "condition": "CONSENSUS_MULTI",
    "clinical_text": "Patient admitted with high fever 39.4C, severe chills, leukocytosis WBC 22000, elevated lactate 4.2 mmol/L, refractory hypotension, and acute septic shock.",
}, headers={"Authorization": f"Bearer {tokens['H105']}"})
assert p6.status_code == 200, f"Prediction 4.6 failed: {p6.text}"
res6 = p6.json()
print(f"\n  [Test 4.6 - Severe Sepsis / Infectious Disease at H105]:")
print(f"    Prediction: {res6['prediction']}")
print(f"    Confidence: {res6['probability']}% | Risk Tier: {res6['risk_level']}")
assert "Sepsis" in res6["prediction"] or "Inflammatory" in res6["prediction"]

# Test 4.7: Cross-Hospital Collaborative Prediction
# H105 (Johns Hopkins) uses collaborative weights from H101 to predict pneumonia from a CXR
p7 = s.post(f"{BASE_URL}/api/v1/hospital/predict", json={
    "modality": "IMAGE",
    "condition": "PULMONARY_IMAGE",
    "image_data": cxr_b64,
}, headers={"Authorization": f"Bearer {tokens['H105']}"})
assert p7.status_code == 200, f"Cross-hospital prediction failed: {p7.text}"
res7 = p7.json()
print(f"\n  [Test 4.7 - Cross-Hospital Collaborative Prediction (H105 evaluating CXR using H101 consensus)]:")
print(f"    Prediction: {res7['prediction']}")
print(f"    Confidence: {res7['probability']}% | Contributing Enclaves: {len(res7['contributing_hospitals'])}")
assert "Pneumonia" in res7["prediction"] or "Infiltration" in res7["prediction"]
assert len(res7['contributing_hospitals']) > 0

# Test 4.8: Non-Medical Image (Sunset Beach)
beach_b64 = create_non_medical_image()
p8 = s.post(f"{BASE_URL}/api/v1/hospital/predict", json={
    "modality": "IMAGE",
    "condition": "AUTO_DETECT",
    "image_data": beach_b64,
}, headers={"Authorization": f"Bearer {tokens['H105']}"})
assert p8.status_code == 200, f"Prediction 8 failed: {p8.text}"
res8 = p8.json()
print(f"\n  [Test 4.8 - Non-Medical Image at H105 (OOD Rejection)]:")
print(f"    Prediction: {res8['prediction']}")
print(f"    Risk Tier: {res8['risk_level']}")
print(f"    Out-of-Distribution Detected: {res8['is_out_of_distribution']}")
assert res8["is_out_of_distribution"] is True
assert "Inconclusive" in res8["prediction"] or "Out-of-Distribution" in res8["prediction"]

# 5. Verify FedSentinel Security Control Plane Defense (Quarantine Prevention)
print("\n--- 5. Verifying FedSentinel Defense Control Plane (Quarantine Prevention) ---")
# Query incidents via admin control plane
inc_resp = s.get(f"{BASE_URL}/api/v1/incidents", headers=admin_headers)
assert inc_resp.status_code == 200, f"Failed to get incidents: {inc_resp.text}"
inc_data = inc_resp.json()
inc_list = inc_data.get("incidents", [])
print(f"  [PASS] FedSentinel Security Telemetry: Active Security Incidents={len(inc_list)}")

print("\n======================================================================")
print("ALL MULTI-HOSPITAL, MULTI-DATASET & MULTI-DISEASE TESTS PASSED!")
print("======================================================================")
