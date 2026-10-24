# FEDSENTINEL-X - UNIFIED FEDERATED AI SECURITY CONTROL PLANE, ROLE-BASED PORTALS & ENCLAVE CLUSTER OPERATIONS PLATFORM

FedSentinel-X is an enterprise-grade cybersecurity control plane and distributed cluster operations platform designed specifically for **Federated Machine Learning (FL)** and collaborative healthcare AI consortiums. Built as a single, cohesive high-assurance web application, it orchestrates two distinct operational experiences:

* **Super Admin SOC Control Plane (`/`)**  -  Mission control for security analysts, platform operators, and chief medical information officers (CMIOs) to initiate aggregation rounds, inspect incoming weight gradients across an autonomous 6-layer defense-in-depth pipeline (L0-L5), isolate Byzantine adversaries with automated quarantine containment, scrub rounds via an interactive 10-stage forensic replay scrubber, and certify global model weights with cryptographic attestation dossiers.
* **Hospital Clinical Enclave Portal (`/hospital/login`)**  -  Dedicated enclave portal for member healthcare institutions (such as Demo Research Hospital, Apollo Health Network, and general hospital networks) to manage local patient data cohorts, import datasets via direct `.NPZ` upload or remote record URL streaming, execute local PyTorch model training directly in situ, and submit privacy-preserving model updates without leaking private patient data.

The platform bridges dark-slate cyber-defense SOC aesthetics with mathematical rigour, backed by FastAPI, PyTorch 2.2+, SQLAlchemy ORM, React 18, Vite 8, and automated deployment architectures on Render and Vercel.

---

## 🌐 Live Production Links

| Service | Platform | Live URL | Status |
| :--- | :--- | :--- | :--- |
| **Super Admin SOC Control Plane** | Vercel | [https://fedsentinal-x.vercel.app/admin/login](https://fedsentinal-x.vercel.app/admin/login) | Protected / Live |
| **Hospital Clinical Enclave** | Vercel | [https://fedsentinal-x.vercel.app/hospital/login](https://fedsentinal-x.vercel.app/hospital/login) | Protected / Live |
| **Interactive Round Replay** | Vercel | [https://fedsentinal-x.vercel.app/replay](https://fedsentinal-x.vercel.app/replay) | Operational |
| **Executive Attestation Dossier** | Vercel | [https://fedsentinal-x.vercel.app/reports](https://fedsentinal-x.vercel.app/reports) | Certified / Live |
| **API Backend Server** | Render | [https://fedsentinel-api.onrender.com](https://fedsentinel-api.onrender.com) | Healthy (200 OK) |
| **Interactive API Documentation** | Render | [https://fedsentinel-api.onrender.com/docs](https://fedsentinel-api.onrender.com/docs) | Swagger UI Live |
| **Database & Evidence Store** | Enclave SQLite | sqlite:///./fedsentinel.db | Connected & Auto-Seeded |
| **Master Architectural Specification** | GitHub | [FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md](docs/FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md) | Read Full Spec |
| **Operator Runbook & System Manual** | GitHub | [OPERATOR_RUNBOOK_MANUAL.md](docs/OPERATOR_RUNBOOK_MANUAL.md) | Full A-Z Manual |

---

## The Problem

Modern distributed machine learning and clinical AI consortiums suffer from critical structural vulnerabilities:

* **Blind Model Update Ingestion**: Traditional federated averaging algorithms (such as standard FedAvg) blindly calculate the weighted mean of candidate client models ($\theta_{\text{global}} = \sum_{k=1}^K \frac{n_k}{N} \theta_k$). A single malicious participant submitting scaled adversarial gradients (+25.0 scale backdoor) poisons the entire global model consensus.
* **Naive Metric Equivalence (`ANOMALY == MALICIOUS`)**: Naive anomaly detection algorithms automatically classify statistical outliers as malicious attacks. In clinical environments, specialized healthcare centers treating rare patient demographics naturally exhibit non-IID variations; falsely isolating them degrades diagnostic utility.
* **Data Privacy Perimeter Breaches**: Naive attempts to verify model updates by transferring sample raw client data violate strict healthcare regulations, including HIPAA Safe Harbor (45 CFR § 164.514) and GDPR Article 25.
* **Absence of Counterfactual & Holdout Testing**: Standard aggregators commit model weights without simulating "what-if" inclusion vs. exclusion harm ($\Delta \text{Accuracy} = \text{Acc}_{\text{with}} - \text{Acc}_{\text{without}}$) against a calibrated holdout validation surface.
* **Lack of Tamper-Evident Forensic Auditability**: Regulated healthcare environments (FDA 21 CFR Part 11) require an immutable audit trail of participant identity, model weight lineage, and administrator override rationale.

---

## Why FedSentinel-X?

FedSentinel-X is designed to simulate a real-world enterprise healthcare AI defense operation:

* **Unified Domain & Seamless Navigation**: Security administrators and hospital operators access their respective interfaces through a unified portal switcher available on the login screen with one-click demo login chips and strict fail-closed route guards.
* **Strict Server-Enforced RBAC**: Every administrative or clinical endpoint is protected by stateless JWT verification, Argon2id password hashing, database-backed account active checks, and automated tenant scoping.
* **Core Security Axioms**:
  1. `RISK != VERDICT`  -  Anomaly score is evidence, not an automatic conviction.
  2. `DON'T TRUST THE UPDATE. VERIFY IT.`  -  Candidate updates are untrusted until attested across L0-L5 defense gates.
  3. `DATASET != MODEL UPDATE`  -  Raw patient data never leaves local hospital enclaves.
* **Autonomous 6-Layer Defense-in-Depth Pipeline (L0-L5)**: Combines structural float checks, 128-dimensional deterministic privacy projections, robust MAD coordinate-wise z-scores, holdout loss trajectory profiling, counterfactual harm testing, and Bayesian threat attribution.
* **True Local PyTorch Enclave Training**: Real PyTorch backward passes and weight optimization run directly in situ on hospital hardware; only `.safetensors` gradient parameters cross the network.
* **Interactive 10-Stage Scrubber & Gate Inspector**: Allows forensic investigators to scrub backward and forward through any historical round, inspecting node topology orbs and layer-by-layer gate verdicts.
* **Publication-Grade Attestation Dossier / Report**: Generates formal compliance reports with double cyan cyber-borders, cryptographic SHA-256 digital seals, and tripartite signature attestations.

---

## Key Features

### 1. Unified Multi-Role Portal Switcher & Access Control
The application features a unified entrance with tab switching between Sign In and Register Hospital, equipped with one-click demo access chips for immediate testing across Super Admin and Hospital roles (H01, H21, H30).

### 2. Dynamic Dataset Ingestion & Tensor Shape Validation
The Hospital Portal's Dataset Hub enables healthcare institutions to either upload a local `.NPZ` array or link an external record URL or local file path (`http://`, `file://`, local disk) with automated streaming download, SHA-256 fingerprinting, finite numerical checking, and CNN input shape validation `(N, 1, 28, 28)`.

### 3. Enclave-Bound PyTorch Training & SafeTensors Serialization
Hospitals train models locally on private hardware using real PyTorch optimizers (SGD/Adam). Gradient weights are packaged using `safetensors` to eliminate arbitrary code execution vulnerabilities common in Python pickle serialization.

### 4. Autonomous 6-Layer Security Engine (L0-L5)
* **L0 Verify**: Structural integrity, parameter length validation ($105,866$ floats for `FedSentinelCNN`), and floating-point finiteness checks (`isnan`/`isinf`).
* **L1 Inspect**: 128-dimensional deterministic projection ($seed=42$) generating a privacy-preserving gradient fingerprint.
* **L2 Correlate**: Robust Coordinate-Wise Median and Median Absolute Deviation ($\text{MAD}$) z-score analysis ($threshold=3.0$).
* **L3 Influence**: Directional alignment against a consensus validation loss trajectory.
* **L4 Simulate**: Counterfactual harm simulation calculating real-world accuracy degradation ($\Delta \text{Acc}$).
* **L5 Attribute**: Bayesian evidence fusion combining signals into an empirical threat hypothesis.

### 5. Multi-Signal Bayesian Trust Engine & Containment Gates
The Trust Engine fuses multi-layer evidence into an autonomous operational posture:
* $\ge 3$ Strong Signals or Integrity Failure $\to$ **QUARANTINE** (Excluded from consensus model).
* $2$ Strong Signals $\to$ **SUSPICIOUS** (Held for analyst review).
* $1$ Strong Signal $\to$ **REVIEW** (Logged with audit notice; benign non-IID tolerated).
* Otherwise $\to$ **TRUSTED** (Admitted into robust aggregation).

### 6. Interactive Visual Round Replay & 10-Stage Scrubber
Platform investigators can replay any completed or running federation round:
* 10 discrete execution stages from initialization to safe model commit.
* Variable playback controls ($1\times, 2\times, 4\times$) and timeline scrubber.
* Orbital node topology with live status orbs (`ACTIVE`, `PENDING`, `ACCEPTED`, `QUARANTINED`).
* Interactive Gate Inspector drawer displaying L0-L5 metrics for any selected hospital.

### 7. Publication-Grade Executive Compliance Dossier / Report
Generates formal attestation documents featuring:
* Institutional double cyber-borders (`border: 4px double #00e5ff`).
* Dynamic cryptographic SHA-256 seal verified against round model artifacts.
* Participant disposition registry, active incident log, and global model lineage metrics.
* Tripartite signature attestations (CMIO, AI Security Architect, Autonomous Control Plane).
* Fully optimized `@media print` layout for print-to-PDF regulatory reporting.

### 8. Append-Only Forensic Audit Trail & Regulatory Ledger
Every security event, human override, quarantine decision, and round finalization is permanently logged with timestamps, operator IDs, and cryptographic hashes, fulfilling FDA 21 CFR Part 11 and HIPAA Security Rule compliance requirements.

---

## 🔑 Test Accounts & Team Mate Credentials

You can test all portals and roles immediately using these credentials:

| Experience | Portal Link | Username / Email | Password | Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Platform Super Admin** | [/](https://fedsentinal-x.vercel.app) | `admin@fedsentinel.local` | `Admin123!` | Complete control: trigger federation rounds, inspect L0-L5 forensic gates, execute manual quarantine overrides, scrub round replay, and generate official compliance reports. |
| **Hospital Administrator (H21)** | [/hospital/login](https://fedsentinal-x.vercel.app/hospital/login) | `admin@h21.local` | `Hospital123!` | Demo Research Hospital: view cohort membership, upload local .NPZ datasets, link external record URLs, run local PyTorch training, and submit weights. |
| **Hospital Administrator (H01)** | [/hospital/login](https://fedsentinal-x.vercel.app/hospital/login) | `admin@demohospital.local` | `Hospital123!` | Demo General Hospital: manage clinical imaging hub, inspect local dataset tensors, execute model updates, and monitor enclave telemetry. |
| **Hospital Administrator (H30)** | [/hospital/login](https://fedsentinal-x.vercel.app/hospital/login) | `admin@apollo.local` | `Hospital123!` | Apollo Health Network: real-time dataset linking, enclave training, and model update submission. |
| **Hospital Self-Registration** | [/](https://fedsentinal-x.vercel.app) $\to$ **Register Hospital** | *User Defined* | *User Defined* | Self-service registration: automatically enrolls new hospital node into active federation, provisions default clinical imaging dataset, and launches dedicated enclave portal. |

---

## Technology Stack

### Frontend
* **Framework**: React 18 (`react`, `react-dom`)
* **Build Tool**: Vite 8 (Hot Module Replacement, fast bundling)
* **Language**: JavaScript / JSX
* **Routing**: React Router-style state navigation with persistent URL views
* **Styling**: Vanilla CSS3 (Custom design system, CSS Grid, Flexbox, responsive breakpoints)
* **Icons**: Lucide React
* **Typography**: Inter (UI elements) and JetBrains Mono (hashes, tensors, logs)
* **Hosting**: Vercel (Global Edge CDN, automatic HTTPS, SPA rewrites via `vercel.json`)

### Backend API
* **Runtime**: Python 3.11 / 3.12 / 3.13
* **Framework**: FastAPI with asynchronous route handlers & WebSockets
* **ASGI Server**: Uvicorn with HTTP/2 protocol support
* **Security & Auth**:
  * `PyJWT`: Stateless 256-bit signed JWT authentication
  * `pwdlib[argon2]`: Password hashing with 12 memory-hard rounds
  * `python-multipart`: Streaming file and dataset ingestion
* **Validation**: Pydantic v2 (Runtime payload parsing and strict schema validation)
* **Hosting**: Render (Web Service container with health check monitoring)

### Machine Learning & Data Pipeline
* **Deep Learning Framework**: PyTorch 2.2+ (`torch`, `torchvision`) CPU/CUDA
* **Model Architecture**: `FedSentinelCNN` (Exact 105,866 parameters)
* **Safe Serialization**: `safetensors` (zero-pickle security format) and verified `.npz` buffers
* **Data Processing**: NumPy, SciPy, Pandas, Scikit-Learn

### Database & ORM
* **Database Engine**: SQLite development / PostgreSQL production compatible
* **ORM**: SQLAlchemy 2.0 with strongly typed declarative models
* **Migrations**: Alembic 1.13+

---

## Project Structure

```text
FedSentinel-X/
├── frontend/                               # React 18 + Vite Frontend SPA
│   ├── public/                             # Static favicon and icon assets
│   │   ├── favicon.svg                     # FedSentinel cyber-shield emblem
│   │   └── icons.svg                       # Platform sprite sheet
│   ├── src/
│   │   ├── assets/                         # Visual assets & hero graphics
│   │   ├── pages/                          # SOC Control Plane Subsystems
│   │   │   ├── AuditTrailPage.jsx          # Tamper-evident regulatory security log
│   │   │   ├── GlobalModelPage.jsx         # SafeTensors model lineage & deployment
│   │   │   ├── IncidentsPage.jsx           # Active threat containment & overrides
│   │   │   ├── L0VerifyPage.jsx            # Structural & numerical integrity gate
│   │   │   ├── L1InspectPage.jsx           # 128-dim privacy fingerprint gate
│   │   │   ├── L2CorrelatePage.jsx         # Robust MAD outlier detection gate
│   │   │   ├── L3InfluencePage.jsx         # Validation loss influence gate
│   │   │   ├── L4SimulatePage.jsx          # Counterfactual delta impact gate
│   │   │   ├── L5AttributePage.jsx         # Bayesian threat attribution gate
│   │   │   ├── QuarantinePage.jsx          # Node containment & quarantine gate
│   │   │   ├── ReportsPage.jsx             # Official Executive Attestation Dossier
│   │   │   ├── RoundReplayPage.jsx         # Visual 10-stage scrubber & inspector
│   │   │   ├── SafeAggregationPage.jsx     # Robust Byzantine-safe aggregator
│   │   │   ├── TrustEnginePage.jsx         # Multi-signal trust scoring console
│   │   │   ├── UpdateIntakePage.jsx        # Candidate gradient evaluation gate
│   │   │   ├── pages.css                   # Specialized sub-page & report styles
│   │   │   └── securityUtils.jsx           # API clients, token interceptors, badges
│   │   ├── App.jsx                         # Super Admin SOC Application Root
│   │   ├── App.css                         # Dark SOC theme styling & animations
│   │   ├── HospitalPortal.jsx              # Clinical Enclave Application Root
│   │   ├── index.css                       # Global styles & JetBrains typography
│   │   └── main.jsx                        # React application DOM entry point
│   ├── vercel.json                         # Vercel SPA routing rewrites
│   └── package.json                        # Frontend dependencies & Vite scripts
│
├── backend/                                # FastAPI High-Performance Backend API
│   ├── api/                                # REST & WebSocket Route Controllers
│   │   ├── audit_routes.py                 # Forensic audit trail API endpoints
│   │   ├── dependencies.py                 # Dependency injection & orchestrators
│   │   ├── federation_routes.py            # Cohort, federation & round routes
│   │   ├── hospital_dataset_routes.py      # Dataset upload & link import routes
│   │   ├── hospital_portal_routes.py       # Enclave local training API endpoints
│   │   ├── hospital_routes.py              # Node lifecycle & quarantine routes
│   │   ├── routes.py                       # Core routes index
│   │   ├── security_routes.py              # L0-L5 forensic gate endpoints
│   │   └── websocket.py                    # Live telemetry streaming socket
│   ├── auth/                               # JWT, Argon2id & RBAC Security Module
│   │   ├── dependencies.py                 # Token decode & user role guards
│   │   ├── roles.py                        # System role enumerations
│   │   ├── routes.py                       # Login, refresh, registration routes
│   │   ├── schemas.py                      # Pydantic auth validation schemas
│   │   └── security.py                     # Argon2 password hasher & JWT tokens
│   ├── core/                               # System Configurations & Constants
│   │   ├── config.py                       # Environment settings & CORS policy
│   │   ├── constants.py                    # Platform metadata & defaults
│   │   └── types.py                        # Domain enumerations & event types
│   ├── schemas/                            # Pydantic Schemas for Strict Typing
│   │   ├── audit.py                        # Audit log validation schemas
│   │   ├── dataset.py                      # Ingestion & link import schemas
│   │   ├── federation.py                   # Federation configuration schemas
│   │   ├── federation_round.py             # Round execution & lifecycle schemas
│   │   ├── hospital.py                     # Node profile & enrollment schemas
│   │   └── hospital_training.py            # Enclave training parameter schemas
│   ├── services/                           # Business Logic & Security Engines
│   │   ├── dataset_service.py              # Tensor file & remote URL import engine
│   │   ├── federation_service.py           # Multi-node cohort coordinator
│   │   ├── hospital_service.py             # Enclave auto-enrollment service
│   │   ├── hospital_training_service.py    # In situ PyTorch training executor
│   │   ├── round_orchestrator.py           # Multi-round lifecycle pipeline
│   │   └── security_pipeline.py            # Autonomous L0-L5 analytical engine
│   └── storage/                            # Database Engine & SQLAlchemy Models
│       ├── database.py                     # SQLite / PostgreSQL session factory
│       └── models.py                       # Declarative ORM models
│
├── docs/                                   # Platform Documentation
│   └── FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md # Master architectural specification
├── scripts/                                # Automation, Seeding & Lifecycle Scripts
│   ├── create_admin.py                     # Initial admin & hospital cohort seeder
│   ├── simulate_full_flow.py               # Complete non-IID FL simulation
│   ├── simulate_hospital_training.py       # Client local training simulator
│   ├── test_complete_lifecycle.py          # End-to-end integration lifecycle test
│   ├── test_hospital_api.py                # API verification utility
│   └── test_logins.py                      # Credential & RBAC verification
├── tests/                                  # 84-Item Pytest Verification Suite
│   ├── integration/                        # FastAPI & WebSocket integration tests
│   └── unit/                               # Schema, ingestion & security unit tests
├── Dockerfile                              # Production Linux Container Definition
├── Procfile                                # Cloud PaaS Process Orchestration
├── render.yaml                             # Render Infrastructure-as-Code Blueprint
├── vercel.json                             # Root Vercel SPA Fallback Configuration
├── requirements.txt                        # Production Python Dependencies
├── LICENSE                                 # MIT Open Source License
└── README.md                               # Root System Showcase & Guide
```

---

## Target Workflow & System Walkthrough

### Phase 1: Hospital Self-Registration & Enclave Onboarding
1. Navigate to the live web application at [https://fedsentinal-x.vercel.app](https://fedsentinal-x.vercel.app).
2. Click the **Register Hospital** tab on the login screen.
3. Fill in Facility Name (e.g. `City Memorial Health`), Hospital ID (`H40`), and Administrator Credentials.
4. Click **Complete Hospital Registration**. The backend automatically creates the hospital node, enrolls it into the active federation cohort, seeds a local clinical dataset, and navigates directly into the hospital enclave.

### Phase 2: Dynamic Dataset Ingestion & Tensor Shape Validation
1. In the Hospital Portal, open the **Datasets** tab.
2. Select **Link Record URL / Path** to link external EHR/imaging records (or select **Upload File** for `.NPZ`).
3. Enter record URL or local path (`https://storage.googleapis.com/.../clinical_sample.npz`).
4. Click **Import & Validate Dataset Record**. The engine streams the record, verifies `(N, 1, 28, 28)` shapes, computes SHA-256 fingerprints, and confirms enclave ingestion.

### Phase 3: Enclave Local Training & Cryptographic Fingerprinting
1. In the Hospital Portal, navigate to **Local Training**.
2. Select the active round and configure hyperparameters (Epochs: `1`, Batch Size: `32`, LR: `0.001`).
3. Click **Start Enclave Training**.
4. The local PyTorch engine executes backward passes over private tensors, packages gradients into `.safetensors`, and submits the update with zero patient data transmission.

### Phase 4: Administrative Round Orchestration & Intake
1. Access the Admin Control Plane at [https://fedsentinal-x.vercel.app](https://fedsentinal-x.vercel.app) with `admin@fedsentinel.local` / `Admin123!`.
2. Inspect the **Command Center** HUD and navigate to **Update Intake**.
3. Review newly submitted client gradient updates awaiting gate evaluation.

### Phase 5: Autonomous Multi-Layer Defense Evaluation (L0-L5) & Containment
1. Updates pass through **L0 Verify** (structural sanity) and **L1 Inspect** (128-dim fingerprint).
2. The engine computes **L2 Correlate** (MAD z-score) and tests holdout impact in **L3 Influence** and **L4 Simulate**.
3. The **Trust Engine** evaluates the multi-signal matrix. Updates triggering $\ge 3$ adverse signals are automatically quarantined with incident tickets dispatched to the Audit Trail.

### Phase 6: Safe Global Aggregation & Model Registry Commit
1. In the Admin Panel, navigate to **Safe Aggregation**.
2. Select robust aggregation scheme (Coordinate Median, Trimmed-Mean, or Trust-Weighted Avg).
3. Finalize the round. The aggregated global model is cryptographically committed to the **Global Model Registry** as `FedSentinelCNN v{round}`.

### Phase 7: Interactive Forensic Round Replay & Gate Inspection
1. Navigate to **Round Replay** (`/replay`).
2. Select the completed round and use the **10-stage timeline scrubber** to examine round progression.
3. Click on any hospital orb in the live topology view to open the **Gate Inspector Drawer** and examine forensic evidence.

### Phase 8: Executive Attestation Dossier Generation & Export
1. Navigate to **Reports** (`/reports`).
2. Select the finalized round to inspect the complete compliance dossier with double borders, cryptographic SHA-256 seal, and participant disposition registry.
3. Click **Print Dossier / Export PDF** to generate an official attestation document for compliance records.

---

## Step-by-Step Operator Runbook & Playbooks

For complete, exhaustive end-to-end operational playbooks, troubleshooting flows, mathematical proofs, and incident responses, consult the dedicated manual:  
👉 **[docs/OPERATOR_RUNBOOK_MANUAL.md](docs/OPERATOR_RUNBOOK_MANUAL.md)**

### Standard Operational Scenarios:
* **Playbook Alpha: Standard Federated Training & Global Model Advancement** - Full lifecycle from round orchestration to multi-node SafeTensors aggregation.
* **Playbook Bravo: Real-Time Mitigation of a Byzantine Gradient Poisoning Attack** - Autonomous containment via L1 Frobenius norms, L2 cosine inversion, and Bayesian risk triggers.
* **Playbook Charlie: Neutralizing a Backdoor Trojan via L3/L4 Simulation** - Isolating stealth Trojans using counterfactual loss degradation before central model commit.
* **Playbook Delta: Hospital Node Onboarding with Isolated EHR Link Ingestion** - Enclave registration and dataset streaming without cross-tenant leakage.
* **Playbook Echo: Regulatory Compliance Audit & Dossier Extraction** - Generating HIPAA / FDA 21 CFR Part 11 cryptographic attestation certificates.
---

## Setup and Installation Guide

### 1. Prerequisites
Ensure the following tools are installed on your workstation:
* **Python**: 3.11, 3.12, or 3.13 (`python --version`)
* **Node.js**: v18.0.0 or higher & `npm` (`node -v`, `npm -v`)
* **Git**: (`git --version`)

### 2. Clone the Repository
```bash
git clone https://github.com/Reneshb24/FEDSENTINAL-X.git
cd FEDSENTINAL-X
```

### 3. Backend Setup & Local Server
```bash
# Create Python virtual environment
python -m venv .venv

# Activate environment:
# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed initial Super Admin and Hospital cohort
python scripts/create_admin.py

# Start FastAPI backend server (Port 8000)
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available at: `http://127.0.0.1:8000/docs`

### 4. Frontend Setup & Development Server
Open a second terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server (Port 5173)
npm run dev
```
Open your browser at `http://localhost:5173` to access FedSentinel-X locally.

### 5. Running the Verification Test Suite
```bash
# Run complete 84-item Pytest suite
pytest tests/ -v

# Run End-to-End Lifecycle Simulation
python scripts/test_complete_lifecycle.py
```

---


## Future Improvements

* **Differential Privacy ($\epsilon, \delta$) Budget Tracker**: Client-side calibrated Gaussian noise injection with formal RDP privacy accounting.
* **Hardware Enclave (TEE) Attestation**: Remote cryptographic attestation for Intel SGX and AWS Nitro Enclaves to verify execution integrity.
* **Homomorphic Encryption (CKKS)**: Encrypted coordinate aggregation allowing mathematical sum and median computation over encrypted ciphertexts.
* **Automated Neural Watermarking**: Embedding non-invasive cryptographic watermarks into global model weights to trace unauthorized weight exfiltration.

---

## Author

**Renesh B** - [@Reneshb24](https://github.com/Reneshb24)  
Project Repository: [https://github.com/Reneshb24/FEDSENTINAL-X](https://github.com/Reneshb24/FEDSENTINAL-X)

For detailed relational schemas, mathematical derivations, API contracts, and operator runbooks, consult the master document:  
👉 [**docs/FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md**](docs/FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md)
