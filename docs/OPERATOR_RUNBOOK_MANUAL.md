# FEDSENTINEL-X — OPERATOR RUNBOOK MANUAL
## Comprehensive End-to-End Operational Guide for Administrator Control Plane & Hospital Enclave Portals

---

## 1. System Overview & Core Boundaries

FedSentinel-X is a production-grade security control plane and distributed operations platform for Federated Learning in healthcare AI consortiums.

### Core Security Axioms
* **`RISK != VERDICT`** — Statistical anomaly detection represents evidence for adjudication, not an automatic conviction.
* **`DATASET != MODEL UPDATE`** — Raw clinical records, patient EHRs, and radiology images remain strictly inside local hospital enclaves. Only signed, validated SafeTensors differential model weight deltas are submitted to the control plane.
* **`DON'T TRUST THE UPDATE. VERIFY IT.`** — Every submitted model delta is untrusted until verified through autonomous L0–L5 defense gates.

---

## 2. Local Environment Setup & Execution

### Prerequisites
* Python 3.11+ (Python 3.13 tested) with virtual environment (`.venv`)
* Node.js 18+ and npm
* SQLite 3 (`fedsentinel.db`)

### Running Locally (Two Parallel Services)

#### Terminal 1 — FastAPI Backend (Port 8000)
```powershell
# Activate Python virtual environment
.\.venv\Scripts\Activate.ps1

# Start Uvicorn backend server
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
* Backend Health check: `http://127.0.0.1:8000/api/v1/health`
* Swagger OpenAPI Docs: `http://127.0.0.1:8000/docs`

#### Terminal 2 — Vite React Frontend (Port 5173)
```powershell
cd frontend
npm install
npm run dev
```
* Control Plane & Portals: `http://localhost:5173`

---

## 3. Verified Portal Credentials

| Portal | Login URL | Default Username | Default Password | Role | Scope |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Global Administrator Control Plane** | `http://localhost:5173/admin/login` | `admin@fedsentinel.local` | `Admin123!` | `SUPER_ADMIN` | Global SOC & Federation Control |
| **Hospital Clinical Enclave (H21)** | `http://localhost:5173/hospital/login` | `admin@h21.local` | `Hospital123!` | `HOSPITAL_ADMIN` | Enclave `H21` (Stanford Clinical AI) |
| **Hospital Clinical Enclave (H01)** | `http://localhost:5173/hospital/login` | `admin@demohospital.local` | `Hospital123!` | `HOSPITAL_ADMIN` | Enclave `H01` (General Medical Center) |

> **Note:** The login screens have dedicated entry points with clean separated authentication. Direct quick-switch links are positioned below each login card to toggle between Administrator Control Plane and Hospital Enclave Access.

---

## 4. End-to-End Walkthrough: Global Administrator Security Control Plane

### Step 1: Administrator Authentication
1. Navigate to `http://localhost:5173/admin/login`.
2. Enter email `admin@fedsentinel.local` and password `Admin123!`.
3. Click **ENTER SECURITY CONTROL PLANE**.
4. You are routed to the central SOC Command Dashboard (`/`).

### Step 2: 3D Orbital Radar Topology & Cluster State
1. Observe the **3D Orbital Radar Network Topology** (`HospitalNetwork3D`) showing enrolled hospitals, orbital status rings, and live node pings.
2. Click on any hospital node in the 3D canvas or in the **HOSPITAL DIRECTORY** to inspect institution health, risk classification, accepted/quarantined updates, and trust score.

### Step 3: Institutional Onboarding & Registration Review
1. In the sidebar, navigate to **HOSPITALS & ENCLAVES -> Registration Requests** (`/requests`).
2. Review institutions in `SUBMITTED / PENDING` status.
3. Click **REVIEW APPLICATION** on a pending institution to transition it to `UNDER_REVIEW`.
4. Click **APPROVE & ONBOARD** to grant active federation membership, or **REJECT WITH REASON** to decline.

### Step 4: Round Configuration & Execution Control
1. In the sidebar, navigate to **FEDERATION OPERATIONS -> Round Configuration** (`/rounds/configure`).
2. Select **EXECUTION MODE**:
   * **`SIMULATION MODE`** (Amber Visuals) — Controlled experiment using synthetic simulation nodes (2 to 20 clients) with optional adversarial attack injection.
   * **`HOSPITAL MODE`** (Cyan Visuals) — Production federated training using approved, active healthcare enclaves. Attack injection is strictly disabled.
3. Use the **Client Count Slider / Presets / Numeric Input** to select the exact participant count (validated between 2 and available capacity).
4. Configure learning rate (`0.001`), batch size (`32`), local epochs (`1`), and Dirichlet concentration ($\alpha = 0.5$).
5. Click **CREATE NEW FEDERATION ROUND**.
6. When the round appears in `CREATED` status, click **START ROUND EXECUTION**.
7. If an orphaned round is ever detected in `RUNNING` status without recent heartbeat, the system displays an option to **FAIL / CANCEL STALE ROUND** with audited reason.

### Step 5: Multi-Tier L0–L5 Defense & Human-in-the-Loop Quarantine
1. Navigate to **SECURITY PIPELINE -> Multi-Tier Defense (L0-L5)**.
2. Inspect how candidate updates pass through autonomous gates:
   * **L0**: SafeTensors format validation & SHA-256 integrity hash.
   * **L1**: Shape verification & NaN/Inf numeric sanity filter.
   * **L2**: Coordinate-wise Median Absolute Deviation (MAD) outlier z-score.
   * **L3**: Holdout validation loss gradient trajectory profiling.
   * **L4**: Counterfactual shadow consensus simulation ($\Delta \text{Acc}$).
   * **L5**: Bayesian Dynamic Trust scoring & reputation attenuation.
3. Navigate to **HUMAN ADJUDICATION -> Quarantine Approvals** (`/adjudication`).
4. If an update was diverted to quarantine, security analysts can inspect forensic telemetry, review Bayesian threat hypotheses, and execute an audited **RELEASE FROM QUARANTINE** or **CONFIRM DISCARD**.

### Step 6: Model Lineage, Audit Trail & Executive Dossiers
1. Navigate to **COMPLIANCE & AUDIT -> Model Lineage** (`/lineage`) to inspect the parent-child cryptographic DAG across rounds.
2. Navigate to **COMPLIANCE & AUDIT -> Audit Ledger** (`/audit`) to review append-only cryptographic event logs (actor ID, IP address, timestamp, action, disposition).
3. Navigate to **COMPLIANCE & AUDIT -> Attestation Dossiers** (`/reports`) to export publication-grade regulatory attestation certificates (HIPAA, FDA 21 CFR Part 11, EU AI Act).

---

## 5. End-to-End Walkthrough: Hospital Clinical Enclave Portal

### Step 1: Hospital Enclave Authentication
1. Navigate to `http://localhost:5173/hospital/login`.
2. To sign into an existing enclave (e.g. Stanford AI Enclave `H21`):
   * Email: `admin@h21.local`
   * Password: `Hospital123!`
3. Click **SIGN IN TO ENCLAVE**.

### Step 2: Enclave Profile & Password Management
1. Inside the hospital portal, navigate to **HOSPITAL -> My Hospital**.
2. Notice the clean, aligned posture indicators:
   * Enclave Operating Status: `ACTIVE`
   * Security Classification: `TRUSTED`
   * Federation Eligibility: `ELIGIBLE`
   * Data Privacy Boundary: `ENCLAVE LOCKED`
3. Click **EDIT PROFILE** in the top right or inline on the Identity card:
   * Update Contact Phone, Physical Address, Website, or Specialization Description.
   * Click **SAVE CHANGES** (`PATCH /api/v1/hospital/profile`). The UI updates immediately without needing a page refresh.
4. Click **CHANGE PASSWORD**:
   * Enter Current Password, New Password (minimum 8 characters), and Confirm New Password.
   * Click **UPDATE PASSWORD** (`POST /api/v1/hospital/change-password`). The backend updates credentials, logs the audit event, and keeps the user's active session valid.

### Step 3: Multi-Format Clinical Datasets & Ingestion Hub
1. Navigate to **DATA -> Datasets**.
2. To create a new clinical dataset, click **CREATE DATASET**:
   * Use one of the **Quick Clinical Templates**:
     * *Chest X-Ray Pneumonia* (`IMAGE_CLASSIFICATION`, 2 classes: Normal vs Pneumonia, 100 samples)
     * *Diabetic Retinopathy Screening* (5 classes: Graded fundus lesions, 200 samples)
     * *Brain MRI Lesions* (4 classes: Neurological scans, 150 samples)
     * *MedMNIST Pathology* (10 classes: Multi-tissue diagnostic benchmark, 250 samples)
   * Click **CREATE & INGEST**.
3. In the Datasets table, click **VERSIONS & INGEST** on any dataset:
   * **Option 1: Direct File Upload**: Select a `.zip`, `.tar.gz`, `.csv`, or `.npz` file from disk. The backend standardizes archives, extracts multi-class image folders (e.g. `NORMAL/` vs `PNEUMONIA/`) into normalized $(1, 28, 28)$ tensors, enforces zero-pickle deserialization, and validates float bounds.
   * **Option 2: Remote Dataset URL & Public Repositories**: Supply an external HTTP/HTTPS URL or public repository link (Hugging Face, GitHub, Zenodo, Kaggle, Mendeley Data). The backend enforces SSRF validation, resolves direct artifacts, and classifies the source as `LOCAL_UPLOAD`, `DIRECT_URL`, or `ONLINE_DATASET_RESOURCE`.
   * **Option 3: In Situ Clinical Benchmark Generator**: Click **GENERATE LOCAL CLINICAL BENCHMARK RECORDS** to synthesize 200 real SafeTensors-compatible tensor samples directly inside the hospital boundary with zero network egress.
4. If an inactive dataset is uploaded to or updated, it is automatically reactivated.

### Step 4: Data Quality Register & Training Readiness
1. Navigate to **DATA -> Data Quality**.
2. Inspect the interactive dataset inspection cards displaying 5 real verification checks:
   * **Format & Zero-Pickle**: Confirmed SafeTensors/NPZ compatibility
   * **Tensor Shape**: Normalized $(1, 28, 28)$ single-channel tensors
   * **Finite Value Bounds**: 0% NaN and 0% Inf
   * **Classes Balanced**: Verified classification heads
   * **Sample Sufficiency**: $N \ge 10$ minimum training batch
3. Status badges distinguish **`ACTIVE`** (activated for federation) from **`QUALITY READY`** (all 5 checks passed). If unvalidated, a training lock is applied to prevent corrupt update submissions.

### Step 5: In Situ Local Model Training & Visual Pipeline
1. In the sidebar, navigate to **FEDERATED LEARNING -> Local Training**.
2. **Round State Detection**:
   * If the latest round is **`COMPLETED`**: The start button is locked with `ROUND {N} COMPLETED — WAITING FOR NEXT ROUND`, showing sealed round metrics.
   * If the round is **`OPEN` / `ACTIVE`**: Training is enabled.
3. Observe the **Live Visual 8-Stage Pipeline**:
   * `[01 Global Model Weights]` $\to$ `[02 Hospital Clinical Data]` $\to$ `[03 In Situ PyTorch Engine]` $\to$ `[04 Model Weight Delta]` $\to$ `[05 SafeTensors Serialization]` $\to$ `[06 SHA-256 Fingerprint]` $\to$ `[07 L0–L5 Security Intake]` $\to$ `[08 Federation Submission]`
4. Click **START LOCAL TRAINING & SUBMIT** to execute local training, compile differential delta weights, compute the SHA-256 hash, and dispatch the SafeTensors update to the control plane.

### Step 6: Visual Trust Engine & Bayesian Reputation
1. Navigate to **SECURITY -> Trust**.
2. Inspect the **Visual Reputation Gauge**:
   * Circular SVG dial displaying the institution's real-time trust score ($0.00 - 1.00$).
   * Security tier badge: `TRUSTED STATUS` / `PROBATION STATUS`.
   * Bayesian parameters: Prior $\text{Beta}(\alpha=10, \beta=1)$, Attenuation Decay $\lambda = 0.98$, Non-Punitive Tolerance $2.5\sigma$.
   * Sequential trust score evaluations table with audit stamps.
   * Non-Punitive Clinical Guarantee banner guaranteeing clinical good faith.

### Step 7: Security Telemetry & Incidents
1. Navigate to **SECURITY -> Security Status**:
   * Active round telemetry with Participating Enclaves, Total Updates Ingested, and Accepted vs Quarantined ratio bar.
   * **L0–L5 Security Gate Checkpoints**: Syntax & Headers, SafeTensors Deserialization, Numerical Bounds, Distribution Drift, Poisoning Defense, and Aggregation Gate.
   * Clean formatted hyperparameter specification cards (zero raw JSON dumps).
2. Navigate to **SECURITY -> Incidents**:
   * Visual incident cards with severity indicators (`CRITICAL`, `HIGH`, `MEDIUM`), forensic explanations, and containment guarantees.

---

## 6. Verification & Automated Test Suite

To verify all security boundaries, database migrations, authentication tokens, SSRF filters, multi-format dataset ingestion, and lifecycle flows:

```powershell
# Run full pytest suite (93 tests)
.\.venv\Scripts\pytest.exe tests/

# Build frontend production bundle (Vite 8)
npm --prefix frontend run build
```

Expected output:
* Pytest: `93 passed, 2 warnings in ~13s` (100% pass rate)
* Vite: `✓ built in ~2s` (zero compilation errors)
