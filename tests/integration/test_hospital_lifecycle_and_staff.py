"""
Integration tests for Hospital Application Lifecycle, Review, Approval, Rejection,
Staff Management, and Profile Updates.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.main import app
from backend.storage.database import SessionLocal
from backend.storage.models import Hospital, User, FederationMembership, Federation
from backend.auth.security import hash_password


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def admin_token(client: TestClient, db: Session) -> str:
    admin = db.query(User).filter(User.role == "SUPER_ADMIN").first()
    assert admin is not None
    admin.password_hash = hash_password("Admin123!")
    admin.is_active = True
    db.commit()

    login_res = client.post("/api/v1/auth/login", json={"email": admin.email, "password": "Admin123!"})
    assert login_res.status_code == 200, login_res.text
    return login_res.json()["access_token"]


def test_hospital_registration_and_application_lifecycle(client: TestClient, db: Session, admin_token: str):
    # 1. Public Registration
    reg_payload = {
        "code": "TEST_CLINIC_99",
        "name": "St. Jude Test Medical Center",
        "contact_email": "contact@stjude-test.org",
        "contact_phone": "+1-555-0199",
        "address": "123 Research Way",
        "country": "United States",
        "institution_type": "ACADEMIC_MEDICAL_CENTER",
        "admin_name": "Dr. Sarah Connor",
        "admin_email": "admin@stjude-test.org",
        "admin_password": "SecurePassword123!"
    }

    # Clean up prior test run if exists
    existing = db.query(Hospital).filter(Hospital.code == "TEST_CLINIC_99").first()
    if existing:
        db.query(FederationMembership).filter(FederationMembership.hospital_id == existing.id).delete()
        db.query(User).filter(User.hospital_id == existing.id).delete()
        db.delete(existing)
        db.commit()

    res = client.post("/api/v1/hospitals/register", json=reg_payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["code"] == "TEST_CLINIC_99"
    assert data["status"] == "PENDING"
    assert data["application_status"] == "SUBMITTED"
    hospital_id = data["id"]

    # Verify hospital cannot train or join rounds while pending
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    assert hospital is not None
    assert hospital.is_eligible is False

    # 2. Global Admin lists applications
    headers = {"Authorization": f"Bearer {admin_token}"}
    apps_res = client.get("/api/v1/hospitals/applications", headers=headers)
    assert apps_res.status_code == 200
    app_ids = [a["id"] for a in apps_res.json()]
    assert hospital_id in app_ids

    # 3. Mark Under Review
    rev_res = client.post(
        f"/api/v1/hospitals/{hospital_id}/review",
        json={"notes": "Credential audit started."},
        headers=headers
    )
    assert rev_res.status_code == 200
    assert rev_res.json()["application_status"] == "UNDER_REVIEW"

    # 4. Approve Application
    fed = db.query(Federation).first()
    appr_res = client.post(
        f"/api/v1/hospitals/{hospital_id}/application-approve",
        json={"federation_id": fed.id if fed else None, "notes": "Approved for active oncology cohort."},
        headers=headers
    )
    assert appr_res.status_code == 200
    approved_data = appr_res.json()
    assert approved_data["status"] == "ACTIVE"
    assert approved_data["application_status"] == "APPROVED"
    assert approved_data["is_eligible"] is True

    # Verify federation membership was automatically assigned
    if fed:
        mem = (
            db.query(FederationMembership)
            .filter(
                FederationMembership.hospital_id == hospital_id,
                FederationMembership.federation_id == fed.id
            )
            .first()
        )
        assert mem is not None
        assert mem.status == "ACTIVE"

    # 5. Hospital Admin logs in using real credentials
    hosp_login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@stjude-test.org", "password": "SecurePassword123!"}
    )
    assert hosp_login_res.status_code == 200, hosp_login_res.text
    hosp_token = hosp_login_res.json()["access_token"]
    hosp_headers = {"Authorization": f"Bearer {hosp_token}"}

    # Add staff member
    staff_payload = {
        "email": "operator1@stjude-test.org",
        "password": "OperatorPassword123!",
        "full_name": "Nurse Kelly",
        "role": "HOSPITAL_OPERATOR"
    }
    staff_res = client.post("/api/v1/hospital/staff", json=staff_payload, headers=hosp_headers)
    assert staff_res.status_code == 201, staff_res.text
    staff_data = staff_res.json()
    assert staff_data["email"] == "operator1@stjude-test.org"
    assert staff_data["is_active"] is True
    staff_id = staff_data["id"]

    # List staff
    list_staff_res = client.get("/api/v1/hospital/staff", headers=hosp_headers)
    assert list_staff_res.status_code == 200
    assert len(list_staff_res.json()) >= 2  # Admin + Operator

    # Toggle active
    toggle_res = client.patch(f"/api/v1/hospital/staff/{staff_id}", json={"is_active": False}, headers=hosp_headers)
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_active"] is False

    # Update hospital profile
    prof_res = client.patch(
        "/api/v1/hospital/profile",
        json={"website": "https://stjude-research.org", "contact_phone": "+1-800-STJUDE"},
        headers=hosp_headers
    )
    assert prof_res.status_code == 200
    assert prof_res.json()["website"] == "https://stjude-research.org"
    assert prof_res.json()["contact_phone"] == "+1-800-STJUDE"


def test_hospital_rejection_lifecycle(client: TestClient, db: Session, admin_token: str):
    # Clean up prior test run if exists
    existing = db.query(Hospital).filter(Hospital.code == "REJECT_CLINIC").first()
    if existing:
        db.query(FederationMembership).filter(FederationMembership.hospital_id == existing.id).delete()
        db.query(User).filter(User.hospital_id == existing.id).delete()
        db.delete(existing)
        db.commit()

    reg_payload = {
        "code": "REJECT_CLINIC",
        "name": "Unverified Health Entity",
        "contact_email": "unverified@entity.org",
        "admin_name": "Unknown Admin",
        "admin_email": "unknown@entity.org",
        "admin_password": "SecurePassword123!"
    }
    res = client.post("/api/v1/hospitals/register", json=reg_payload)
    assert res.status_code == 201
    h_id = res.json()["id"]

    headers = {"Authorization": f"Bearer {admin_token}"}

    # Reject without reason fails validation
    bad_rej = client.post(f"/api/v1/hospitals/{h_id}/application-reject", json={"rejection_reason": " "}, headers=headers)
    assert bad_rej.status_code == 422

    # Reject with valid mandatory reason
    valid_rej = client.post(
        f"/api/v1/hospitals/{h_id}/application-reject",
        json={"rejection_reason": "Failed HIPAA compliance certification and domain ownership verification."},
        headers=headers
    )
    assert valid_rej.status_code == 200
    r_data = valid_rej.json()
    assert r_data["status"] == "REJECTED"
    assert r_data["application_status"] == "REJECTED"
    assert r_data["is_eligible"] is False
    assert "HIPAA" in r_data["rejection_reason"]
