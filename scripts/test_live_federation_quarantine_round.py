import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import io
import json
import base64
import torch
import numpy as np
from PIL import Image, ImageDraw

from backend.storage.database import SessionLocal
from backend.storage.models import (
    Federation,
    FederationRound,
    Hospital,
    Dataset,
    AggregatedDiseaseUpdate,
    User,
)
from backend.services.hospital_portal_service import HospitalPortalService
from backend.services.disease_registry_service import DiseaseRegistryService
from backend.services.round_orchestrator import RoundOrchestrator
from backend.models.cnn import FedSentinelCNN
from backend.models.update import create_model_update
from backend.layers.layer3_influence.subset_sampler import create_validation_loader
from data.dataset import load_mnist_test

def make_test_chest_xray():
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

def make_test_skull_xray():
    img = Image.new("L", (256, 256), color=10)
    draw = ImageDraw.Draw(img)
    draw.ellipse([35, 25, 221, 215], fill=70, outline=220, width=8)
    draw.rectangle([60, 160, 196, 235], fill=140, outline=200, width=5)
    draw.ellipse([55, 45, 201, 165], fill=50)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

def make_test_dermoscopy():
    img = Image.new("RGB", (256, 256), color=(180, 140, 120))
    draw = ImageDraw.Draw(img)
    draw.polygon([(90, 70), (180, 85), (205, 150), (160, 195), (105, 180), (70, 120)], fill=(35, 20, 25), outline=(15, 10, 12))
    draw.ellipse([110, 95, 155, 140], fill=(70, 30, 20))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

def make_test_ood_image():
    img = Image.new("RGB", (256, 256), color=(255, 100, 20))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 140, 256, 256], fill=(0, 180, 255))
    draw.ellipse([100, 70, 156, 126], fill=(255, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

def model_factory():
    return FedSentinelCNN(num_classes=10)

def main():
    print("======================================================================")
    print("FedSentinel-X: Live Multi-Hospital Federation, Defense & Prediction Test")
    print("======================================================================")
    db = SessionLocal()

    # Step 1: Verify 5 Clean Consortium Hospitals
    print("\n--- Step 1: Verifying 5 Clean Consortium Hospitals ---")
    hospitals = db.query(Hospital).order_by(Hospital.code).all()
    assert len(hospitals) >= 5, f"Expected 5 hospitals, got {len(hospitals)}"
    for h in hospitals:
        ds_count = db.query(Dataset).filter(Dataset.hospital_id == h.id).count()
        print(f"  [OK] Hospital: {h.code} - {h.name} (Datasets: {ds_count}, Status: {h.security_status})")
        assert ds_count >= 2, f"Hospital {h.code} must have at least 2 datasets"

    # Step 2: Prepare Live Multi-Hospital Updates (5 Benign + 1 Malicious Attacker)
    print("\n--- Step 2: Generating Live Hospital Model Updates (5 Benign + 1 Malicious) ---")
    base_model = FedSentinelCNN(num_classes=10)
    base_state = {k: v.clone() for k, v in base_model.state_dict().items()}

    round_id = "round-consortium-test-01"
    runtime_updates = []
    # 5 Benign Updates from H101 - H105
    for idx, h in enumerate(hospitals[:5]):
        torch.manual_seed(100 + idx)
        client_delta = {}
        for k, v in base_state.items():
            noise = torch.randn_like(v.float()) * 0.02
            client_delta[k] = noise
        
        upd = create_model_update(
            update_id=f"upd-{h.code}-r10",
            client_id=h.id,
            round_id=round_id,
            delta=client_delta,
            num_examples=600,
        )
        runtime_updates.append(upd)
        print(f"  [BENIGN] Update prepared for {h.code} (Norm: {upd.l2_norm:.4f}, Examples: {upd.num_examples})")

    # 1 Malicious Poisoned Update (Poisoning Attack: Gradient scaling & backdoor noise)
    malicious_hosp_id = "malicious-adversary-node"
    malicious_delta = {}
    for k, v in base_state.items():
        # Large adversarial perturbation (+25.0 scale)
        adv_noise = torch.ones_like(v.float()) * 25.0
        malicious_delta[k] = adv_noise

    malicious_update = create_model_update(
        update_id="upd-malicious-r10",
        client_id=malicious_hosp_id,
        round_id=round_id,
        delta=malicious_delta,
        num_examples=1200,
    )
    runtime_updates.append(malicious_update)
    print(f"  [MALICIOUS] Adversarial Poisoned Update prepared (Norm: {malicious_update.l2_norm:.4f}, Client: {malicious_hosp_id})")

    # Step 3: Execute FedSentinel Complete L0-L5 Defense Pipeline & Quarantine
    print("\n--- Step 3: Executing FedSentinel L0-L5 Defense & Quarantine Review ---")
    test_dataset = load_mnist_test()
    val_loader = create_validation_loader(dataset=test_dataset, sample_size=100)
    orchestrator = RoundOrchestrator()
    orchestrator.create_round(round_id=round_id, target_clients=len(runtime_updates))

    round_result = orchestrator.execute_round(
        round_id=round_id,
        updates=runtime_updates,
        global_state=base_state,
        model_factory=model_factory,
        validation_loader=val_loader,
        device="cpu",
    )

    accepted_ids = [u.client_id for u in round_result.accepted_updates]
    quarantined_ids = [u.client_id for u in round_result.quarantined_updates]

    print(f"  Total Updates Submitted: {len(runtime_updates)}")
    print(f"  Accepted by Defense:      {len(round_result.accepted_updates)}")
    print(f"  Quarantined by Defense:   {len(round_result.quarantined_updates)}")

    # Strict Assertions on Security Integrity
    assert malicious_hosp_id in quarantined_ids, "SECURITY FAILURE: Adversarial attack was NOT quarantined!"
    assert malicious_hosp_id not in accepted_ids, "SECURITY FAILURE: Adversarial attack reached accepted pool!"
    for h in hospitals[:5]:
        assert h.id in accepted_ids, f"Hospital {h.code} should be accepted"

    print("  [PASS] FedSentinel Defense: Malicious update intercepted and quarantined into isolation vault!")
    print("  [PASS] Robust Aggregation: Only verified hospital updates aggregated into global model.")

    # Step 4: Save & Publish Disease-Specific Aggregated Checkpoint
    print("\n--- Step 4: Publishing Aggregated Disease Model Checkpoint ---")
    target_domain = "PULMONARY_IMAGE"
    contributing = [{"code": h.code, "name": h.name, "accepted_updates": 1} for h in hospitals[:5]]
    meta = {
        "disease_domain": target_domain,
        "model_version": "v3.0-pulmonary-consortium",
        "round_number": 10,
        "accepted_updates_count": len(round_result.accepted_updates),
        "quarantined_prevented_count": len(round_result.quarantined_updates),
        "total_updates_reviewed": len(runtime_updates),
        "security_verdict": "POISONING_ATTEMPT_PREVENTED",
        "contributing_hospitals": contributing,
        "aggregation_algorithm": "Robust-Coordinate-Median",
    }

    ckpt_path, weights_hash = DiseaseRegistryService.save_checkpoint(
        target_domain,
        round_result.global_state,
        meta,
    )

    assert ckpt_path.exists(), f"Checkpoint file missing: {ckpt_path}"
    cfg_path = ckpt_path.parent / "config.json"
    assert cfg_path.exists(), f"Config file missing: {cfg_path}"

    with open(cfg_path, "r") as f:
        saved_cfg = json.load(f)
    print(f"  [OK] Saved SafeTensors Checkpoint: {ckpt_path.name}")
    print(f"  [OK] Model Weights SHA-256 Hash:   {weights_hash}")
    print(f"  [OK] Saved Configuration Metadata: Domain={saved_cfg['disease_domain']}, Classes={len(saved_cfg.get('label_mapping', {}))}")

    # Update AggregatedDiseaseUpdate in DB
    dis_rec = db.query(AggregatedDiseaseUpdate).filter(
        AggregatedDiseaseUpdate.disease_domain == target_domain
    ).first()
    if not dis_rec:
        dis_rec = AggregatedDiseaseUpdate(disease_domain=target_domain, display_name="Pulmonary Infiltration")
        db.add(dis_rec)
    dis_rec.model_version = "v3.0-pulmonary-consortium"
    dis_rec.round_number = 10
    dis_rec.model_weights_hash = weights_hash
    dis_rec.accepted_updates_count = len(round_result.accepted_updates)
    dis_rec.quarantined_prevented_count = len(round_result.quarantined_updates)
    dis_rec.total_updates_reviewed = len(runtime_updates)
    dis_rec.security_verdict = "POISONING_ATTEMPT_PREVENTED"
    dis_rec.aggregation_algorithm = "Robust-Coordinate-Median"
    dis_rec.prevention_summary = "FedSentinel intercepted and quarantined 1 malicious poisoning attack; safely aggregated 5 hospital updates."
    dis_rec.contributing_hospitals_json = json.dumps(contributing)
    db.commit()
    print("  [OK] Updated Consortium Aggregated Disease Registry record in database.")

    # Step 5: Execute Cross-Hospital Clinical Predictions
    print("\n--- Step 5: Testing Cross-Hospital Clinical Predictions ---")
    h101 = hospitals[0]
    h102 = hospitals[1]
    h103 = hospitals[2]
    h104 = hospitals[3]
    h105 = hospitals[4]

    # Test 5.1: Chest X-Ray at H101 (Supported Disease)
    cxr = make_test_chest_xray()
    p1 = HospitalPortalService.predict_disease(
        db,
        hospital_id=h101.id,
        patient_id="PT-CXR-001",
        modality="IMAGE",
        condition="PULMONARY_IMAGE",
        image_data=cxr,
        clinical_text=None,
        features=None,
    )
    print(f"  [Test 5.1 - Chest X-Ray at H101]:")
    print(f"    Prediction: {p1['prediction']} | Confidence: {p1['probability']}% | Risk: {p1['risk_level']}")
    assert "Pneumonia" in p1["prediction"] or "Infiltration" in p1["prediction"]
    assert p1["probability"] > 80.0
    print("    [PASS] Chest X-Ray correctly diagnosed.")

    # Test 5.2: Skull X-Ray at H101 (Safety Screening: MUST NOT predict pneumonia!)
    skull = make_test_skull_xray()
    p2 = HospitalPortalService.predict_disease(
        db,
        hospital_id=h101.id,
        patient_id="PT-SKULL-002",
        modality="IMAGE",
        condition="PULMONARY_IMAGE",
        image_data=skull,
        clinical_text=None,
        features=None,
    )
    print(f"  [Test 5.2 - Skull X-Ray at H101 (Safety Screening)]:")
    print(f"    Prediction: {p2['prediction']}")
    print(f"    Confidence: {p2['probability']}% | Risk Tier: {p2['risk_level']}")
    assert "UNSUPPORTED INPUT" in p2["prediction"]
    assert "Cranial" in p2["prediction"] or "Skull" in p2["prediction"]
    assert p2["probability"] == 0.0
    assert "Pneumonia" not in p2["prediction"], "CRITICAL ERROR: Lung disease predicted on cranial radiograph!"
    print("    [PASS] Cranial radiograph correctly identified as UNSUPPORTED INPUT; no false lung prediction.")

    # Test 5.3: Dermoscopy Scan at H104 (MSK Derm)
    derm = make_test_dermoscopy()
    p3 = HospitalPortalService.predict_disease(
        db,
        hospital_id=h104.id,
        patient_id="PT-DERM-003",
        modality="IMAGE",
        condition="DERMATOLOGIC",
        image_data=derm,
        clinical_text=None,
        features=None,
    )
    print(f"  [Test 5.3 - Dermoscopy at H104]:")
    print(f"    Prediction: {p3['prediction']} | Confidence: {p3['probability']}%")
    assert "Melanoma" in p3["prediction"] or "Cutaneous" in p3["prediction"]
    print("    [PASS] Cutaneous lesion correctly classified.")

    # Test 5.4: Clinical Diabetes Text at H102 (Joslin Diabetes)
    p4 = HospitalPortalService.predict_disease(
        db,
        hospital_id=h102.id,
        patient_id="PT-DIAB-004",
        modality="TEXT",
        condition="METABOLIC_DIABETES",
        image_data=None,
        clinical_text="Patient exhibits classic triad of polyuria, polydipsia, unexplained weight loss, HbA1c 10.1%, and fasting plasma glucose 232 mg/dL.",
        features=None,
    )
    print(f"  [Test 5.4 - Diabetes Clinical Text at H102]:")
    print(f"    Prediction: {p4['prediction']} | Confidence: {p4['probability']}%")
    assert "Diabetes" in p4["prediction"]
    assert p4["probability"] > 85.0
    print("    [PASS] Metabolic condition correctly diagnosed from clinical narrative.")

    # Test 5.5: Acute Coronary Syndrome at H103 (Cleveland Clinic)
    p5 = HospitalPortalService.predict_disease(
        db,
        hospital_id=h103.id,
        patient_id="PT-ACS-005",
        modality="TEXT",
        condition="CARDIOMETABOLIC",
        image_data=None,
        clinical_text="Emergency admission with acute crushing chest pressure, radiation to left jaw, diaphoresis, dyspnea, and elevated cardiac troponin.",
        features=None,
    )
    print(f"  [Test 5.5 - Acute Coronary Syndrome at H103]:")
    print(f"    Prediction: {p5['prediction']} | Confidence: {p5['probability']}%")
    assert "Coronary" in p5["prediction"] or "Cardiovascular" in p5["prediction"]
    assert p5["probability"] > 85.0
    print("    [PASS] Acute cardiovascular syndrome correctly identified.")

    # Test 5.6: Severe Sepsis / Shock at H105 (Johns Hopkins)
    p6 = HospitalPortalService.predict_disease(
        db,
        hospital_id=h105.id,
        patient_id="PT-SEP-006",
        modality="TEXT",
        condition="CONSENSUS_MULTI",
        image_data=None,
        clinical_text="ICU patient presenting with core temperature 39.5C, refractory hypotension, severe chills, leukocytosis WBC 24000, and serum lactate 4.8.",
        features=None,
    )
    print(f"  [Test 5.6 - Sepsis / Infectious Shock at H105]:")
    print(f"    Prediction: {p6['prediction']} | Confidence: {p6['probability']}%")
    assert "Sepsis" in p6["prediction"] or "Inflammatory" in p6["prediction"]
    print("    [PASS] Sepsis / shock presentation correctly identified.")

    # Test 5.7: Non-Medical Out-of-Distribution Image (Sunset Beach)
    ood_img = make_test_ood_image()
    p7 = HospitalPortalService.predict_disease(
        db,
        hospital_id=h105.id,
        patient_id="PT-OOD-007",
        modality="IMAGE",
        condition="AUTO_DETECT",
        image_data=ood_img,
        clinical_text=None,
        features=None,
    )
    print(f"  [Test 5.7 - Non-Medical Image (Beach Sunset) at H105]:")
    print(f"    Prediction: {p7['prediction']} | OOD Flag: {p7['is_out_of_distribution']}")
    assert p7["is_out_of_distribution"] is True
    assert "INCONCLUSIVE" in p7["prediction"] or "Out-of-Distribution" in p7["prediction"]
    print("    [PASS] Non-medical OOD image correctly rejected as INCONCLUSIVE.")

    # Test 5.8: Untrained / Unfamiliar Disease Description
    p8 = HospitalPortalService.predict_disease(
        db,
        hospital_id=h101.id,
        patient_id="PT-UNTRAINED-008",
        modality="TEXT",
        condition="CONSENSUS_MULTI",
        image_data=None,
        clinical_text="The quick brown fox jumps over the lazy dog in the sunny park with trees and birds.",
        features=None,
    )
    print(f"  [Test 5.8 - Untrained Clinical Text at H101]:")
    print(f"    Prediction: {p8['prediction']} | Confidence: {p8['probability']}%")
    assert "INCONCLUSIVE" in p8["prediction"]
    assert "Unfamiliar" in p8["prediction"] or "Untrained" in p8["prediction"]
    assert p8["probability"] == 0.0
    print("    [PASS] Untrained disease text correctly flagged as INCONCLUSIVE with 0.0% probability.")

    # Test 5.9: Corrupted / Short Text
    p9 = HospitalPortalService.predict_disease(
        db,
        hospital_id=h101.id,
        patient_id="PT-CORRUPT-009",
        modality="TEXT",
        condition="CONSENSUS_MULTI",
        image_data=None,
        clinical_text="hello",
        features=None,
    )
    print(f"  [Test 5.9 - Corrupted / Short Text at H101]:")
    print(f"    Prediction: {p9['prediction']} | Confidence: {p9['probability']}%")
    assert "UNSUPPORTED INPUT" in p9["prediction"]
    assert p9["probability"] == 0.0
    print("    [PASS] Insufficient/corrupted input correctly rejected.")

    # Test 5.10: Cross-Hospital Inference (H103 uses H101's updated pulmonary model)
    p10 = HospitalPortalService.predict_disease(
        db,
        hospital_id=h103.id,
        patient_id="PT-XFER-010",
        modality="IMAGE",
        condition="PULMONARY_IMAGE",
        image_data=cxr,
        clinical_text=None,
        features=None,
    )
    print(f"  [Test 5.10 - Cross-Hospital Inference (H103 Cleveland Clinic using Pulmonary Model)]:")
    print(f"    Prediction: {p10['prediction']} | Contributing Enclaves: {len(p10['contributing_hospitals'])}")
    assert "Pneumonia" in p10["prediction"] or "Infiltration" in p10["prediction"]
    assert len(p10['contributing_hospitals']) >= 5
    print("    [PASS] Cross-hospital inference successfully shared and evaluated.")

    db.close()
    print("\n======================================================================")
    print("ALL TESTS PASSED WITH ZERO ERRORS!")
    print("FedSentinel L0-L5 defense verified, quarantine confirmed,")
    print("and cross-hospital diagnostic inference is completely operational.")
    print("======================================================================")

if __name__ == "__main__":
    main()
