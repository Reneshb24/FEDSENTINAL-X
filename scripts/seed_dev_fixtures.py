"""
Development & Simulation Fixtures Seeder.

This script is strictly for local development and test simulations.
It is NEVER automatically invoked in production environments.
"""
from __future__ import annotations

import uuid
from backend.auth.roles import Role
from backend.auth.security import hash_password
from backend.storage.database import SessionLocal
from backend.storage.models import (
    User,
    Hospital,
    Federation,
    FederationMembership,
)

DEFAULT_FEDERATION_ID = "413ef0b3-a947-4a02-a652-d963ef14b8da"

DEV_HOSPITALS = [
    {
        "code": "H01",
        "name": "General Hospital Clinical Node",
        "email": "h01-dev@hospital.org",
        "location": "Boston, MA",
        "country": "United States",
        "region": "Massachusetts",
        "institution_type": "REGIONAL_HOSPITAL",
    },
    {
        "code": "H21",
        "name": "Research Medical Center",
        "email": "h21-dev@research.org",
        "location": "Cambridge, MA",
        "country": "United States",
        "region": "Massachusetts",
        "institution_type": "ACADEMIC_MEDICAL_CENTER",
    },
    {
        "code": "H30",
        "name": "Advanced AI Health Enclave",
        "email": "h30-dev@healthnetwork.org",
        "location": "Chennai, India",
        "country": "India",
        "region": "Tamil Nadu",
        "institution_type": "SPECIALTY_HOSPITAL",
    },
]

def seed_dev_fixtures():
    db = SessionLocal()
    try:
        fed = db.query(Federation).filter(Federation.id == DEFAULT_FEDERATION_ID).first()
        if not fed:
            print("Please run database baseline initialization first.")
            return

        for h in DEV_HOSPITALS:
            existing = db.query(Hospital).filter(Hospital.code == h["code"]).first()
            if not existing:
                h_obj = Hospital(
                    code=h["code"],
                    name=h["name"],
                    status="ACTIVE",
                    application_status="APPROVED",
                    security_status="TRUSTED",
                    is_eligible=True,
                    is_simulation=False,
                    contact_email=h["email"],
                    location=h["location"],
                    country=h["country"],
                    region=h["region"],
                    institution_type=h["institution_type"],
                )
                db.add(h_obj)
                db.flush()

                mem = FederationMembership(
                    federation_id=DEFAULT_FEDERATION_ID,
                    hospital_id=h_obj.id,
                    status="ACTIVE",
                )
                db.add(mem)

                user = User(
                    email=h["email"],
                    password_hash=hash_password("Hospital123!"),
                    role=Role.HOSPITAL_ADMIN.value,
                    hospital_id=h_obj.id,
                    is_active=True,
                    full_name=f"{h['name']} Administrator",
                )
                db.add(user)
                print(f"Created dev hospital {h['code']}: {h['email']}")

        db.commit()
        print("Dev fixtures seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding dev fixtures: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_dev_fixtures()
