import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.storage.database import SessionLocal
from backend.storage.models import Hospital, User, Dataset, DatasetVersion


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def hospital_auth_token(client):
    # Authenticate as demo hospital admin
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@h21.local", "password": "Hospital123!"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def test_hospital_profile_update(client, hospital_auth_token):
    headers = {"Authorization": f"Bearer {hospital_auth_token}"}
    
    # 1. Update hospital profile
    res = client.patch(
        "/api/v1/hospital/profile",
        headers=headers,
        json={
            "location": "Palo Alto Clinical AI Enclave",
            "contact_phone": "+1 650-555-9988",
            "website": "https://clinical-ai.stanford.edu",
            "description": "Pulmonary and cardiovascular imaging research enclave",
        },
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["location"] == "Palo Alto Clinical AI Enclave"
    assert data["contact_phone"] == "+1 650-555-9988"
    assert data["website"] == "https://clinical-ai.stanford.edu"


def test_password_change_flow(client, hospital_auth_token):
    headers = {"Authorization": f"Bearer {hospital_auth_token}"}

    # 1. Reject incorrect current password
    bad_res = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={
            "current_password": "WrongPassword999!",
            "new_password": "NewHospitalPassword123!",
        },
    )
    assert bad_res.status_code == 400
    assert "Current password is incorrect" in bad_res.json()["detail"]

    # 2. Reject short password
    short_res = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={
            "current_password": "Hospital123!",
            "new_password": "short",
        },
    )
    assert short_res.status_code == 400

    # 3. Successfully change password
    ok_res = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={
            "current_password": "Hospital123!",
            "new_password": "TemporaryHospital123!",
        },
    )
    assert ok_res.status_code == 200
    assert ok_res.json()["success"] is True

    # 4. Revert password back so subsequent tests and fixtures keep standard credentials
    revert_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@h21.local", "password": "TemporaryHospital123!"},
    )
    assert revert_login.status_code == 200
    new_token = revert_login.json()["access_token"]
    
    revert_res = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {new_token}"},
        json={
            "current_password": "TemporaryHospital123!",
            "new_password": "Hospital123!",
        },
    )
    assert revert_res.status_code == 200


def test_dataset_creation_and_synthetic_link(client, hospital_auth_token):
    headers = {"Authorization": f"Bearer {hospital_auth_token}"}

    # 1. Create a dataset
    res = client.post(
        "/api/v1/hospital/datasets",
        headers=headers,
        json={
            "name": "Automated Pneumonia Test Cohort",
            "dataset_type": "IMAGE_CLASSIFICATION",
            "sample_count": 200,
            "num_classes": 2,
        },
    )
    assert res.status_code == 201, res.text
    dataset = res.json()
    dataset_id = dataset["id"]
    assert dataset["is_active"] is True

    # 2. Deactivate it to test reactivation on ingestion
    client.post(
        f"/api/v1/hospital/datasets/{dataset_id}/deactivate",
        headers=headers,
    )

    # 3. Generate in-situ benchmark dataset version (should auto-activate)
    link_res = client.post(
        f"/api/v1/hospital/datasets/{dataset_id}/versions/link",
        headers=headers,
        json={
            "version": "v1-benchmark",
            "record_link": "sample_clinical_records",
            "format": "AUTO",
        },
    )
    assert link_res.status_code == 201, link_res.text
    version_data = link_res.json()
    assert version_data["storage_status"] == "STORED_LOCALLY"
    assert version_data["validation_status"] == "VALIDATED"
    assert version_data["sample_count"] == 200
    assert version_data["num_classes"] == 2

    # 4. Verify dataset was auto-activated
    check_res = client.get(
        f"/api/v1/hospital/datasets/{dataset_id}",
        headers=headers,
    )
    assert check_res.status_code == 200
    assert check_res.json()["is_active"] is True
