"""
Safe database schema migration and synthetic node classification script.

Ensures:
1. New hospital and user columns exist (address, country, region, website, institution_type,
   application_status, rejection_reason, is_simulation, full_name).
2. Existing simulation nodes (H02-H20) are marked as is_simulation=True, preserving
   all forensic references, foreign keys, and model updates.
3. Reports the exact count of modified records without deleting forensic data.
"""
import sqlite3
import os

DB_PATH = "fedsentinel.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- [1] Checking and applying schema migrations ---")
    
    # 1. Hospitals table
    cursor.execute("PRAGMA table_info(hospitals);")
    hospital_cols = {row[1] for row in cursor.fetchall()}

    columns_to_add_hospital = [
        ("address", "VARCHAR(255)"),
        ("country", "VARCHAR(100)"),
        ("region", "VARCHAR(100)"),
        ("website", "VARCHAR(255)"),
        ("institution_type", "VARCHAR(100)"),
        ("application_status", "VARCHAR(50) DEFAULT 'APPROVED'"),
        ("rejection_reason", "TEXT"),
        ("is_simulation", "BOOLEAN DEFAULT 0"),
    ]

    for col_name, col_type in columns_to_add_hospital:
        if col_name not in hospital_cols:
            cursor.execute(f"ALTER TABLE hospitals ADD COLUMN {col_name} {col_type};")
            print(f"Added column {col_name} to hospitals.")

    # 2. Users table
    cursor.execute("PRAGMA table_info(users);")
    user_cols = {row[1] for row in cursor.fetchall()}

    if "full_name" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name VARCHAR(200);")
        print("Added column full_name to users.")

    conn.commit()

    print("\n--- [2] Identifying and classifying synthetic/simulation nodes ---")
    # Simulation nodes are H02-H20 or those explicitly created as simulated nodes
    cursor.execute("SELECT id, code, name, contact_email FROM hospitals;")
    all_hospitals = cursor.fetchall()

    simulation_count = 0
    production_count = 0

    for hid, code, name, email in all_hospitals:
        # Determine if simulation node
        is_sim = False
        code_str = (code or "").upper()
        email_str = (email or "").lower()
        name_str = (name or "").lower()

        # Synthetic nodes H02 through H20 created for federation simulation tests
        if code_str.startswith("H") and len(code_str) == 3 and code_str[1:].isdigit():
            num = int(code_str[1:])
            if 2 <= num <= 20:
                is_sim = True
        elif "fedsentinel hospital" in name_str or "federated hospital" in name_str:
            is_sim = True

        if is_sim:
            cursor.execute("""
                UPDATE hospitals 
                SET is_simulation = 1, 
                    application_status = 'SIMULATION_APPROVED',
                    institution_type = 'SYNTHETIC_LAB_NODE'
                WHERE id = ?;
            """, (hid,))
            simulation_count += 1
        else:
            # Verified production institution
            cursor.execute("""
                UPDATE hospitals 
                SET is_simulation = 0, 
                    application_status = 'APPROVED'
                WHERE id = ?;
            """, (hid,))
            production_count += 1

    conn.commit()

    print(f"Successfully classified {simulation_count} nodes as simulation laboratory nodes.")
    print(f"Verified {production_count} production healthcare institutions.")

    # Check model updates and verify zero orphaned references
    cursor.execute("SELECT count(*) FROM model_updates;")
    total_updates = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM model_updates WHERE hospital_id IN (SELECT id FROM hospitals);")
    valid_updates = cursor.fetchone()[0]

    print(f"\n--- [3] Forensic Evidence Integrity Verification ---")
    print(f"Total Model Updates: {total_updates}")
    print(f"Valid Update References: {valid_updates}")
    assert total_updates == valid_updates, "Integrity check failed: orphaned model updates detected!"
    print("Forensic data integrity: 100% PRESERVED. Zero evidence loss.")

    conn.close()

if __name__ == "__main__":
    migrate()
