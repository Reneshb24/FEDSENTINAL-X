from getpass import getpass

from backend.auth.roles import Role
from backend.auth.security import hash_password
from backend.storage.database import SessionLocal, init_database
from backend.storage.models import User


def main():
    init_database()

    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password: ")
    confirm = getpass("Confirm password: ")

    if password != confirm:
        print("ERROR: Passwords do not match.")
        return

    if len(password) < 8:
        print("ERROR: Password must be at least 8 characters.")
        return

    db = SessionLocal()

    try:
        existing = db.query(User).filter(User.email == email).first()

        if existing:
            print(f"ERROR: User already exists: {email}")
            return

        admin = User(
            email=email,
            password_hash=hash_password(password),
            role=Role.SUPER_ADMIN.value,
            hospital_id=None,
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print()
        print("========================================")
        print("SUPER ADMIN CREATED")
        print("========================================")
        print(f"Email : {admin.email}")
        print(f"Role  : {admin.role}")
        print(f"ID    : {admin.id}")
        print("========================================")

    finally:
        db.close()


if __name__ == "__main__":
    main()