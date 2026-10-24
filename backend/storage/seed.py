"""
Automatic database seeding for production deployment and new environments.
Ensures Super Admin, Default Federation, and Pre-configured Hospitals exist.
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
    Dataset,
)

DEFAULT_FEDERATION_ID = "413ef0b3-a947-4a02-a652-d963ef14b8da"

HOSPITALS_TO_SEED = [
    {
        "id": "21d2bb59-614a-4ba7-919d-451937b48386",
        "name": "Demo General Hospital (H01)",
        "email": "admin@demohospital.local",
        "location": "Boston, MA",
    },
    {
        "id": "da739305-819d-44c2-be4c-7b44005a859b",
        "name": "Demo Research Hospital (H21)",
        "email": "admin@h21.local",
        "location": "Cambridge, MA",
    },
    {
        "id": "20d9dda5-24a9-43cb-a408-b51ae07f87b5",
        "name": "Apollo Advanced AI Research Hospital (H30)",
        "email": "admin@apollo.local",
        "location": "Chennai, India",
    },
]

def seed_default_data() -> None:
    """Idempotently seed default admin, federation, and hospital accounts."""
    db = SessionLocal()
    try:
        # 1. Seed Super Admin
        admin = db.query(User).filter(User.email == "admin@fedsentinel.local").first()
        if not admin:
            admin = User(
                email="admin@fedsentinel.local",
                password_hash=hash_password("Admin123!"),
                role=Role.SUPER_ADMIN.value,
                hospital_id=None,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print("Seeded default Super Admin: admin@fedsentinel.local")

        # 2. Seed Default Federation
        federation = db.query(Federation).filter(Federation.id == DEFAULT_FEDERATION_ID).first()
        if not federation:
            federation = Federation(
                id=DEFAULT_FEDERATION_ID,
                name="FedSentinel Healthcare Consortium",
                description="Collaborative Healthcare AI Security & Federated Learning Network",
                status="ACTIVE",
            )
            db.add(federation)
            db.commit()
            print("Seeded default Federation: FedSentinel Healthcare Consortium")

        # 3. Seed Core Hospitals & Accounts
        for h_info in HOSPITALS_TO_SEED:
            hospital = db.query(Hospital).filter(Hospital.id == h_info["id"]).first()
            if not hospital:
                hospital = Hospital(
                    id=h_info["id"],
                    name=h_info["name"],
                    status="ACTIVE",
                    trust_status="TRUSTED",
                    is_eligible=True,
                    location=h_info["location"],
                    contact_email=h_info["email"],
                )
                db.add(hospital)
                db.commit()

            # Membership
            membership = (
                db.query(FederationMembership)
                .filter(
                    FederationMembership.federation_id == DEFAULT_FEDERATION_ID,
                    FederationMembership.hospital_id == hospital.id,
                )
                .first()
            )
            if not membership:
                membership = FederationMembership(
                    federation_id=DEFAULT_FEDERATION_ID,
                    hospital_id=hospital.id,
                    status="ACTIVE",
                )
                db.add(membership)
                db.commit()

            # User account
            user = db.query(User).filter(User.email == h_info["email"]).first()
            if not user:
                user = User(
                    email=h_info["email"],
                    password_hash=hash_password("Hospital123!"),
                    role=Role.HOSPITAL_ADMIN.value,
                    hospital_id=hospital.id,
                    is_active=True,
                )
                db.add(user)
                db.commit()
                print(f"Seeded hospital user: {h_info['email']}")

            # Seed default dataset
            ds = db.query(Dataset).filter(Dataset.hospital_id == hospital.id).first()
            if not ds:
                ds = Dataset(
                    id=str(uuid.uuid4()),
                    hospital_id=hospital.id,
                    name="Clinical EHR Imaging Hub",
                    dataset_type="IMAGE_CLASSIFICATION",
                    sample_count=200,
                    num_classes=10,
                    is_active=True,
                )
                db.add(ds)
                db.commit()

        # 4. Seed simulated federation cohort (H02-H20) if not present
        existing_count = db.query(Hospital).count()
        if existing_count < 10:
            for i in range(2, 21):
                h_code = f"H{i:02d}"
                h_name = f"FedSentinel Hospital {h_code}"
                h_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"fedsentinel-{h_code}"))
                if not db.query(Hospital).filter(Hospital.id == h_id).first():
                    sim_h = Hospital(
                        id=h_id,
                        name=h_name,
                        status="ACTIVE",
                        trust_status="TRUSTED",
                        is_eligible=True,
                        location="Federated Node",
                        contact_email=f"node-{h_code.lower()}@fedsentinel.local",
                    )
                    db.add(sim_h)
                    db.commit()

                    sim_mem = FederationMembership(
                        federation_id=DEFAULT_FEDERATION_ID,
                        hospital_id=h_id,
                        status="ACTIVE",
                    )
                    db.add(sim_mem)
                    db.commit()
            print("Seeded simulated federation cohort nodes (H02-H20)")

    except Exception as e:
        db.rollback()
        print(f"Error seeding default data: {e}")
    finally:
        db.close()
