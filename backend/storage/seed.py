"""
Production database initialization for FedSentinel-X.
Ensures the Super Admin and root Federation exist in new environments.

Per strict production architecture rules:
- No automatic creation of demo hospitals or synthetic H02-H20 nodes.
- No fabricated .local hospitals created as legitimate institutions.
- No fake default clinical datasets assigned automatically.
- No automatic federation membership before administrator approval.
Development fixtures are separated into scripts/seed_dev_fixtures.py.
"""
from __future__ import annotations

import os
from backend.auth.roles import Role
from backend.auth.security import hash_password
from backend.storage.database import SessionLocal
from backend.storage.models import User, Federation

DEFAULT_FEDERATION_ID = "413ef0b3-a947-4a02-a652-d963ef14b8da"

def seed_default_data() -> None:
    """
    Idempotently initialize production baseline: Super Admin and default Federation container.
    Does NOT seed synthetic hospitals or demo accounts into production.
    """
    db = SessionLocal()
    try:
        # 1. Seed Super Admin (configurable via environment variables)
        admin_email = os.getenv("ADMIN_EMAIL", "admin@fedsentinel.local").strip().lower()
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!")

        admin = db.query(User).filter(User.role == Role.SUPER_ADMIN.value).first()
        if not admin:
            admin = User(
                email=admin_email,
                password_hash=hash_password(admin_password),
                role=Role.SUPER_ADMIN.value,
                hospital_id=None,
                is_active=True,
                full_name="Global Security Administrator",
            )
            db.add(admin)
            db.commit()
            print(f"[Production Baseline] Seeded initial Super Admin: {admin_email}")

        # 2. Seed Default Federation container
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
            print("[Production Baseline] Initialized Federation: FedSentinel Healthcare Consortium")

    except Exception as e:
        db.rollback()
        print(f"Warning during production seeding: {e}")
    finally:
        db.close()
