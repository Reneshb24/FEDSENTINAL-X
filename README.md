# FEDSENTINEL-X — UNIFIED FEDERATED AI SECURITY CONTROL PLANE, ROLE-BASED PORTALS & ENCLAVE CLUSTER OPERATIONS PLATFORM

<div align="center">

```
  ███████╗███████╗██████╗ ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     
  ██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     
  █████╗  █████╗  ██║  ██║███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     
  ██╔══╝  ██╔══╝  ██║  ██║╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     
  ██║     ███████╗██████╔╝███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
  ╚═╝     ╚══════╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝
                                             - X -                                         
```

### Institutional Security Control Plane for Federated Machine Learning & Healthcare AI Consortiums

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite 8](https://img.shields.io/badge/Vite-8.2-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Zero--Trust](https://img.shields.io/badge/Security-Zero--Trust%20L0--L5-00e5ff?style=for-the-badge)](https://fedsentinel.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

[Live Production Links](#-live-production-links) • [The Problem](#the-problem) • [Why FedSentinel-X?](#why-fedsentinel-x) • [Key Features](#key-features) • [Test Accounts & Credentials](#-test-accounts--team-mate-credentials) • [Technology Stack](#technology-stack) • [System Walkthrough](#target-workflow--system-walkthrough) • [Operator Runbook](#step-by-step-operator-runbook)

</div>

---

**FedSentinel-X** is an enterprise-grade, zero-trust cybersecurity control plane and distributed cluster operations platform designed specifically for **Federated Machine Learning (FL)** and collaborative healthcare AI consortiums. Built as a unified, high-assurance web application, it orchestrates two distinct operational experiences:

* **Super Admin SOC Control Plane (`/`)** — Mission control for security analysts, platform operators, and chief medical information officers (CMIOs) to initiate aggregation rounds, inspect incoming weight gradients across a **6-Layer Defense-in-Depth Pipeline (L0–L5)**, isolate Byzantine adversaries with automated quarantine containment, replay rounds via an interactive 10-stage forensic scrubber, and certify global model weights with cryptographic attestation dossiers.
* **Hospital Clinical Enclave Portal (`/hospital/login`)** — Dedicated enclave portal for member healthcare institutions (such as Demo Research Hospital, Apollo Health Network, and general hospital networks) to manage local patient data cohorts, import datasets via direct `.NPZ` upload or remote record URL streaming, execute local PyTorch model training directly in situ, and submit privacy-preserving model updates without leaking private patient data.

The platform bridges dark-slate cyber-defense SOC aesthetics with mathematical rigour, backed by FastAPI, PyTorch 2.2+, SQLAlchemy ORM, React 18, Vite 8, and automated deployment architectures on **Render** (API backend) and **Vercel** (global edge frontend).

---

## 🌐 Live Production Links

| Service / Interface | Cloud Platform | Live URL | Operational Status |
| :--- | :--- | :--- | :--- |
| **Super Admin SOC Plane** | Vercel Edge CDN | [https://fedsentinel-x.vercel.app](https://fedsentinel-x.vercel.app) | 🟢 Protected / Live |
| **Hospital Clinical Enclave** | Vercel Edge CDN | [https://fedsentinel-x.vercel.app/hospital/login](https://fedsentinel-x.vercel.app/hospital/login) | 🟢 Protected / Live |
| **Interactive Round Replay** | Vercel Edge CDN | [https://fedsentinel-x.vercel.app/replay](https://fedsentinel-x.vercel.app/replay) | 🟢 Live / Operational |
| **Executive Attestation Dossier** | Vercel Edge CDN | [https://fedsentinel-x.vercel.app/reports](https://fedsentinel-x.vercel.app/reports) | 🟢 Certified / Live |
| **API Backend Server** | Render Cloud PaaS | [https://fedsentinel-api.onrender.com](https://fedsentinel-api.onrender.com) | 🟢 Healthy (`200 OK`) |
| **Interactive API Documentation**| Render Cloud PaaS | [https://fedsentinel-api.onrender.com/docs](https://fedsentinel-api.onrender.com/docs) | 🟢 Swagger UI Live |
| **Database & Evidence Store** | Local Enclave / SQLite | `sqlite:///./fedsentinel.db` (Persistent Storage) | 🟢 Connected |
| **Master Documentation** | GitHub Master Spec | [FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md](docs/FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md) | 🟢 Read Full Spec |

---

## The Problem

Modern distributed machine learning and clinical AI consortiums suffer from critical structural vulnerabilities:

1. **Blind Model Update Ingestion**: Traditional federated averaging algorithms (such as standard FedAvg) blindly calculate the weighted mean of candidate client models ($\theta_{\text{global}} = \sum_{k=1}^K \frac{n_k}{N} \theta_k$). A single malicious participant submitting scaled adversarial gradients (+25.0 scale backdoor) poisons the entire global model consensus.
2. **Naive Metric Equivalence (`ANOMALY == MALICIOUS`)**: Naive anomaly detection algorithms automatically classify statistical outliers as malicious attacks. In clinical environments, specialized healthcare centers treating rare patient demographics naturally exhibit non-IID variations; falsely isolating them degrades diagnostic utility.
3. **Data Privacy Perimeter Breaches**: Naive attempts to verify model updates by transferring sample raw client data violate strict healthcare regulations, including **HIPAA Safe Harbor (45 CFR § 164.514)** and **GDPR Article 25**.
4. **Absence of Counterfactual & Holdout Testing**: Standard aggregators commit model weights without simulating "what-if" inclusion vs. exclusion harm ($\Delta \text{Accuracy} = \text{Acc}_{\text{with}} - \text{Acc}_{\text{without}}$) against a calibrated holdout validation surface.
5. **Lack of Tamper-Evident Forensic Auditability**: Regulated healthcare environments (FDA 21 CFR Part 11) require an immutable audit trail of participant identity, model weight lineage, and administrator override rationale.

---

## Why FedSentinel-X?

FedSentinel-X solves these challenges through a unified, defense-in-depth architecture:

* **Unified Domain & Seamless Role Isolation**: Platform administrators and hospital operators navigate their respective consoles through a unified login and portal-switching system with instant demo access chips and fail-closed routing guards.
* **Strict Server-Enforced RBAC & Cryptographic Signing**: Every administrative and clinical endpoint is guarded by stateless HMAC-SHA256 JWT tokens, Argon2id password hashing, and database-backed active status checks.
* **Core Security Axioms**:
  ```text
  1. RISK != VERDICT: Anomaly score is evidence, not a conviction.
  2. DON'T TRUST THE UPDATE. VERIFY IT: Updates are untrusted until attested across L0–L5.
  3. DATASET != MODEL UPDATE: Patient data NEVER crosses the enclave boundary.
  ```
* **Autonomous 6-Layer Defense-in-Depth Pipeline (L0–L5)**: From L0 floating-point verification and L1 128-dimensional privacy-preserving fingerprints to L2 robust MAD z-scores, L3 influence profiling, L4 counterfactual harm testing, and L5 Bayesian threat attribution.
* **True Local PyTorch Enclave Training**: Real PyTorch backward passes and weight optimization run in situ on local hospital hardware; only `.safetensors` gradient parameters cross the network.
* **Interactive 10-Stage Scrubber & Gate Inspector**: Allows forensic investigators to scrub backward and forward through any historical round, inspecting node topology orbs and layer-by-layer gate verdicts.
* **Publication-Grade Attestation Dossier / Report**: Generates formal compliance reports with double cyan cyber-borders (`border: 4px double #00e5ff`), cryptographic SHA-256 digital seals, and tripartite signature attestations (CMIO, AI Security Architect, Autonomous Control Plane).

---

## Key Features

### 1. Unified Multi-Role Portal Switcher & Access Control
The application features a unified entrance with tab switching between **Sign In** and **Register Hospital**, equipped with one-click demo access chips for immediate testing across Super Admin and Hospital roles (H01, H21, H30).

### 2. Dynamic Dataset Ingestion & Tensor Shape Validation
The Hospital Portal's **Dataset Hub** enables healthcare institutions to either:
* Upload a local `.NPZ` array containing multi-dimensional imaging arrays.
* Link an external record URL or local file path (`http://`, `file://`, local disk) with automated streaming download, SHA-256 fingerprinting, finite numerical checking, and CNN input shape validation `(N, 1, 28, 28)`.

### 3. Enclave-Bound PyTorch Training & SafeTensors Serialization
Hospitals train models locally on private hardware using real PyTorch optimizers (SGD/Adam). Gradient weights are packaged using `safetensors` to eliminate arbitrary code execution vulnerabilities common in Python pickle serialization.

### 4. Autonomous 6-Layer Security Engine (L0–L5)
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
* Interactive Gate Inspector drawer displaying L0–L5 metrics for any selected hospital.

### 7. Publication-Grade Executive Compliance Dossier / Report
Generates formal attestation documents featuring:
* Institutional double cyber-borders (`border: 4px double #00e5ff`).
* Dynamic cryptographic SHA-256 seal verified against round model artifacts.
* Participant disposition registry, active incident log, and global model lineage metrics.
* Tripartite signature attestations (CMIO, AI Security Architect, Autonomous Control Plane).
* Fully optimized `@media print` layout for print-to-PDF regulatory reporting.

### 8. Append-Only Forensic Audit Trail & Regulatory Ledger
Every security event, human override, quarantine decision, and round finalization is permanently logged with timestamps, operator IDs, and cryptographic hashes, fulfilling **FDA 21 CFR Part 11** and **HIPAA Security Rule** compliance requirements.

---

## 🔑 Test Accounts & Team Mate Credentials

You can test all portals and roles immediately using these credentials:

| Experience | Portal Link | Username / Email | Password | Operational Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Platform Super Admin** | [`/`](https://fedsentinel-x.vercel.app) | `admin@fedsentinel.local` | `Admin123!` | Complete control: trigger federation rounds, inspect L0–L5 forensic gates, execute manual quarantine overrides, scrub Round Replays, and generate official compliance reports. |
| **Hospital Administrator (H21)** | [`/hospital/login`](https://fedsentinel-x.vercel.app/hospital/login) | `admin@h21.local` | `Hospital123!` | Demo Research Hospital: view cohort membership, upload local .NPZ datasets, link external record URLs, run local PyTorch training, and submit weights. |
| **Hospital Administrator (H01)** | [`/hospital/login`](https://fedsentinel-x.vercel.app/hospital/login) | `admin@demohospital.local` | `Hospital123!` | Demo General Hospital: manage clinical imaging hub, inspect local dataset tensors, execute model updates, and monitor enclave telemetry. |
| **Hospital Administrator (H30)** | [`/hospital/login`](https://fedsentinel-x.vercel.app/hospital/login) | `admin@apollo.local` | `Hospital123!` | Apollo Health Network: real-time dataset linking, enclave training, and model update submission. |
| **New Hospital Self-Registration** | [`/`](https://fedsentinel-x.vercel.app) $\to$ **Register Hospital** | *User Defined* | *User Defined* | Self-service registration: automatically enrolls new hospital node into active federation, provisions default clinical imaging dataset, and launches dedicated enclave portal. |

---

## Technology Stack

### Frontend Architecture
* **Framework**: React 18 (`react`, `react-dom`)
* **Build Tool**: Vite 8 (Hot Module Replacement, fast tree-shaking ESModule bundling)
* **Language**: JavaScript / JSX with strict ES6+ modular architecture
* **Routing**: React Router-style stateful client navigation with persistent tab state
* **Styling**: Modern Cyber-Defense SOC Design System (Vanilla CSS3, CSS Grid, Flexbox, responsive breakpoints)
* **Icons**: `lucide-react`
* **Typography**: `Inter` (clean UI font) and `JetBrains Mono` (hashes, logs, tensors)
* **Hosting**: Vercel (Global Edge CDN, automatic HTTPS, SPA rewrites via `vercel.json`)

### Backend API & Security Service
* **Runtime**: Python 3.11 / 3.12 / 3.13
* **Web Framework**: FastAPI with asynchronous endpoints & WebSocket streams
* **ASGI Server**: Uvicorn with HTTP/2 protocol support
* **Security & Auth**:
  * `PyJWT`: Stateless 256-bit HMAC-SHA256 signed access & refresh tokens
  * `pwdlib[argon2]`: Password hashing with memory-hard Argon2id algorithm
  * `python-multipart`: Streaming file ingestion
* **CORS**: Starlette CORSMiddleware configured with domain regex (`*.vercel.app`, `localhost`)
* **Hosting**: Render (Web Service container with health check monitoring)

### Machine Learning & Data Pipeline
* **Deep Learning Framework**: PyTorch 2.2+ (`torch`, `torchvision`) CPU/CUDA optimized
* **Model Architecture**: `FedSentinelCNN` (2 Convolutional layers, MaxPool, Dropout, 2 Dense layers, exact 105,866 parameters)
* **Safe Serialization**: `safetensors` (zero-pickle security format) and verified `.npz` buffers
* **Data Processing**: NumPy, SciPy, Pandas, Scikit-Learn
* **Distribution Scheme**: Non-IID Dirichlet distribution ($\alpha = 0.5$) across 20+ clients

### Database & ORM
* **ORM**: SQLAlchemy 2.0 with strongly typed declarative models
* **Migrations**: Alembic 1.13+
* **Database Engine**: SQLite development / PostgreSQL production compatible

---

## Project Structure

```text
FedSentinel-X/
├── frontend/                               # React 18 + Vite Frontend SPA
│   ├── public/                             # Static favicon, icons, and SVG assets
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
│   │   ├── security_routes.py              # L0–L5 forensic gate endpoints
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
│   │   └── security_pipeline.py            # Autonomous L0–L5 analytical engine
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

```text
 PHASE 1: Self-Registration ──> PHASE 2: Dynamic Ingestion ──> PHASE 3: Enclave Training
            │                                                         │
            ▼                                                         ▼
 PHASE 4: Round Orchestration <── Gradients & Hashes Only ─────────────┘
            │
            ▼
 PHASE 5: Autonomous L0-L5 Defense & Multi-Signal Containment
            │
            ▼
 PHASE 6: Safe Global Aggregation & Model Registry Commit
            │
            ▼
 PHASE 7: Interactive Round Replay ──> PHASE 8: Executive Attestation Dossier
```

### Phase 1: Hospital Self-Registration & Enclave Onboarding
1. Navigate to the live web application at [https://fedsentinel-x.vercel.app](https://fedsentinel-x.vercel.app).
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
1. Access the Admin Control Plane at [https://fedsentinel-x.vercel.app](https://fedsentinel-x.vercel.app) with `admin@fedsentinel.local` / `Admin123!`.
2. Inspect the **Command Center** HUD and navigate to **Update Intake**.
3. Review newly submitted client gradient updates awaiting gate evaluation.

### Phase 5: Autonomous Multi-Layer Defense Evaluation (L0–L5) & Containment
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

## Step-by-Step Operator Runbook

### Scenario A: How to Place an Update into Manual Quarantine
1. In the Admin SOC Plane, navigate to **Update Intake** or **Incidents**.
2. Locate the candidate client update (e.g., from Node `H11`).
3. Click **Inspect Telemetry** to review MAD deviation, gradient alignment, and counterfactual harm.
4. Click **Enforce Manual Quarantine**, input an operational rationale, and confirm.
5. The update is instantly isolated, excluded from the aggregation pool, and logged in the immutable audit ledger.

### Scenario B: How to Advance and Finalize an FL Round
1. In the Admin SOC Plane, navigate to **Federation Overview**.
2. Select the active round in progress.
3. Ensure participating nodes have submitted local gradients.
4. Navigate to **Safe Aggregation**, verify that quarantined updates are excluded, and click **Finalize & Commit Round**.
5. The global consensus model is updated, and a new round is opened.

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

## Cloud Deployment Guide (Render + Vercel)

### Backend Deployment on [Render](https://render.com) (Free Web Service)
1. Fork or push repository to GitHub: `https://github.com/Reneshb24/FEDSENTINAL-X`.
2. In Render, select **New +** $\to$ **Web Service**.
3. Connect your repository. Render auto-detects `render.yaml`, or configure manually:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
4. Add Environment Variables:
   - `PYTHON_VERSION`: `3.11.9`
   - `ENVIRONMENT`: `production`
   - `JWT_SECRET_KEY`: *(Generate a secure 32-character random string)*
   - `CORS_ORIGINS`: `https://fedsentinel-x.vercel.app,http://localhost:5173`
   - `DATABASE_URL`: `sqlite:///./fedsentinel.db`
5. Click **Create Web Service**.

### Frontend Deployment on [Vercel](https://vercel.com) (Free Global Edge)
1. In Vercel, select **Add New...** $\to$ **Project** and import `FEDSENTINAL-X`.
2. Configure settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend` *(or leave blank; root `vercel.json` will auto-route)*
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Add Environment Variables:
   - `VITE_API_BASE_URL`: Your Render backend URL (e.g., `https://fedsentinel-api.onrender.com`)
   - `VITE_FEDERATION_ID`: `413ef0b3-a947-4a02-a652-d963ef14b8da`
4. Click **Deploy**.

---

## Future Improvements

* **Differential Privacy ($\epsilon, \delta$) Budget Tracker**: Client-side calibrated Gaussian noise injection with formal RDP privacy accounting.
* **Hardware Enclave (TEE) Attestation**: Remote cryptographic attestation for Intel SGX and AWS Nitro Enclaves to verify execution integrity.
* **Homomorphic Encryption (CKKS)**: Encrypted coordinate aggregation allowing mathematical sum and median computation over encrypted ciphertexts.
* **Automated Neural Watermarking**: Embedding non-invasive cryptographic watermarks into global model weights to trace unauthorized weight exfiltration.

---

## Author

**Renesh B** – [@Reneshb24](https://github.com/Reneshb24)  
Project Repository: [https://github.com/Reneshb24/FEDSENTINAL-X](https://github.com/Reneshb24/FEDSENTINAL-X)

For detailed relational schemas, mathematical derivations, API contracts, and operator runbooks, consult the master document:  
👉 [**docs/FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md**](docs/FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md)

---

<div align="center">
<b>FedSentinel-X — Transforming Federated Machine Learning into a High-Assurance Security Plane</b><br>
<sub>Zero-Trust Architectural Engineering for Mission-Critical Distributed AI.</sub>
</div>
