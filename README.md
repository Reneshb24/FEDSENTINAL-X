# FEDSENTINEL-X — FEDERATED AI SECURITY CONTROL PLANE & HEALTHCARE ENCLAVE CLUSTER PLATFORM

FedSentinel-X is an enterprise-grade cybersecurity control plane and distributed cluster operations platform designed specifically for **Federated Machine Learning (FL)** in healthcare AI consortiums. Built as a high-assurance, defense-in-depth web application, it orchestrates two distinct operational experiences:

* **Global Administrator Security Control Plane (`/`)** — Mission control for platform security officers, chief medical information officers (CMIOs), and ML engineers. Features include live round configuration (Simulation vs. Hospital Mode), institutional registration intake review, 3D orbital radar network topology, multi-tier L0–L5 defense analysis, human-in-the-loop quarantine adjudication, safe aggregation (FedAvg, Coordinate-Median, Trimmed-Mean), cryptographic model lineage, tamper-evident audit trails, and publication-grade attestation dossiers.
* **Hospital Clinical Enclave Portal (`/hospital/login`)** — Dedicated enclave workspace for member healthcare institutions. Member facilities manage in situ patient data cohorts, import datasets via local uploads (.zip, .tar.gz, .csv, .parquet, .npz) or verified remote URL streams/online dataset repositories (Hugging Face, GitHub, Zenodo, Kaggle, Mendeley) with strict SSRF protection, run authentic PyTorch CNN training locally on private hardware, manage enclave staff and operator accounts, and submit `.safetensors` model updates without ever exposing patient EHR or imaging records.

The platform unites modern dark-slate SOC aesthetics with mathematical rigor, backed by **FastAPI**, **PyTorch 2.2+**, **SQLAlchemy ORM**, **React 19**, **Vite 8**, **Three.js / React Three Fiber**, and automated deployment on **Render** and **Vercel**.

---

## 🌐 Live Production Links

| Service | Platform | Live URL | Status |
| :--- | :--- | :--- | :--- |
| **Global Administrator Control Plane** | Vercel | [https://fedsentinal-x.vercel.app](https://fedsentinal-x.vercel.app) | Protected / Live |
| **Hospital Clinical Enclave Portal** | Vercel | [https://fedsentinal-x.vercel.app/hospital/login](https://fedsentinal-x.vercel.app/hospital/login) | Protected / Live |
| **Interactive Round Replay** | Vercel | [https://fedsentinal-x.vercel.app/replay](https://fedsentinal-x.vercel.app/replay) | Operational |
| **Executive Attestation Dossier** | Vercel | [https://fedsentinal-x.vercel.app/reports](https://fedsentinal-x.vercel.app/reports) | Certified / Live |
| **API Backend Server** | Render | [https://fedsentinel-api.onrender.com](https://fedsentinel-api.onrender.com) | Healthy (200 OK) |
| **Interactive API Documentation** | Render | [https://fedsentinel-api.onrender.com/docs](https://fedsentinel-api.onrender.com/docs) | Swagger UI Live |
| **Master Architectural Specification** | GitHub | [FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md](docs/FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md) | Read Full Spec |
| **Complete Operator Runbook Manual** | GitHub | [OPERATOR_RUNBOOK_MANUAL.md](docs/OPERATOR_RUNBOOK_MANUAL.md) | End-to-End Walkthrough |

---

## The Problem

Modern distributed machine learning and clinical AI consortiums suffer from critical structural vulnerabilities:

* **Blind Model Update Ingestion**: Traditional federated averaging algorithms (such as standard FedAvg) calculate the weighted mean of candidate client models ($\theta_{\text{global}} = \sum_{k=1}^K \frac{n_k}{N} \theta_k$). A single malicious participant submitting scaled adversarial gradients (+25.0 scale backdoor) poisons the entire global consensus model.
* **Naive Metric Equivalence (`ANOMALY == MALICIOUS`)**: Naive anomaly detection algorithms automatically classify statistical outliers as malicious attacks. In clinical environments, specialized healthcare centers treating rare patient demographics naturally exhibit non-IID variations; falsely isolating them degrades diagnostic utility.
* **Data Privacy Perimeter Breaches**: Attempts to verify model updates by transferring raw client data violate strict healthcare regulations, including HIPAA Safe Harbor (45 CFR § 164.514) and GDPR Article 25.
* **Absence of Counterfactual & Holdout Testing**: Standard aggregators commit model weights without simulating "what-if" inclusion vs. exclusion harm ($\Delta \text{Accuracy} = \text{Acc}_{\text{with}} - \text{Acc}_{\text{without}}$) against a calibrated holdout validation surface.
* **Lack of Tamper-Evident Forensic Auditability**: Regulated healthcare environments (FDA 21 CFR Part 11) require an immutable audit trail of participant identity, model weight lineage, and administrator override rationale.

---

## Why FedSentinel-X?

FedSentinel-X is designed for real-world enterprise healthcare AI defense:

* **Strict Institutional Onboarding & Lifecycle**: New healthcare facilities register through the institutional onboarding flow. Newly registered hospitals enter a `SUBMITTED / PENDING` state and can log in to view institutional application status, but are strictly quarantined from federation rounds and model training until vetted and approved by global administrators.
* **Tenant-Isolated Hospital Enclaves**: Hospital accounts are strictly isolated by `hospital_id` in the backend API layer. Enclave administrators manage authorized local operators, update institutional profiles, and control datasets locally.
* **Core Security Axioms**:
  1. `RISK != VERDICT` — Anomaly score is evidence, not an automatic conviction.
  2. `DON'T TRUST THE UPDATE. VERIFY IT.` — Candidate updates are untrusted until attested across L0–L5 defense gates.
  3. `DATASET != MODEL UPDATE` — Raw patient data never leaves local hospital enclaves.
* **Autonomous 6-Layer Defense-in-Depth Pipeline (L0–L5)**: Combines structural float checks, 128-dimensional deterministic privacy projections, robust MAD coordinate-wise z-scores, holdout loss trajectory profiling, counterfactual harm testing, and Bayesian threat attribution.
* **3D Visualizations with Graceful WebGL Fallbacks**:
  * **3D Orbital Radar Network Topology** (`HospitalNetwork3D`): Interactive Three.js/R3F orbital mesh of hospital nodes with live status halos, ping beams, and click inspection.
  * **3D Neural Architecture Explorer** (`NeuralModel3D`): Interactive layer visualization of `FedSentinelCNN` feature maps, synaptic weight lines, and output class logits.
  * **3D Multi-Tier Defense Pipeline** (`SecurityPipeline3D`): Visualizes model update trajectories passing through L0–L5 gates, the red quarantine diversion chute, and the safe aggregation core.
* **Enterprise Ingestion Security (SSRF & Path Traversal Prevention)**: Remote dataset imports strictly validate hostnames and resolve DNS to block loopback, RFC-1918 private subnets, link-local, and AWS metadata addresses (`169.254.169.254`). Local paths are restricted to permitted directory boundaries.

---

## System Architecture

```text
                                  +---------------------------------------+
                                  |   Global Administrator SOC Plane      |
                                  |   (Registration, Security, Lineage)  |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |   Autonomous L0-L5 Defense Engine     |
                                  |  L0: Hash & SafeTensors Validation    |
                                  |  L1: Shape, NaN & Privacy Projection  |
                                  |  L2: Robust Coordinate MAD Outlier    |
                                  |  L3: Gradient Influence & Backdoor    |
                                  |  L4: Counterfactual Shadow Simulation |
                                  |  L5: Dynamic Trust & Reputation       |
                                  +---------+-------------------+---------+
                                            |                   |
                         Pass All Gates     v                   v   Adversarial Threat Flagged
                     +---------------------------+     +---------------------------+
                     | Safe Aggregation Core     |     | Forensic Quarantine Vault |
                     | (FedAvg, Coord-Median)    |     | (Isolated from Consensus) |
                     +-------------+-------------+     +---------------------------+
                                   |
                                   v
                     +---------------------------+
                     | Global Model Registry     |
                     | FedSentinelCNN SafeTensors|
                     +---------------------------+
                                   ^
                                   | Verified Model Parameters Only
                                   | (Zero Raw Data Transferred)
          +------------------------+------------------------+
          |                                                 |
+---------+-----------------------+     +-------------------+-------------------+
| Hospital Enclave A (Mayo)       |     | Hospital Enclave B (Johns Hopkins)    |
| - Private Patient Data In Situ  |     | - Private Patient Data In Situ        |
| - Local PyTorch SGD Training    |     | - Local PyTorch SGD Training          |
| - Staff & Operator Management   |     | - Staff & Operator Management         |
+---------------------------------+     +---------------------------------------+
```

---

## Key Features

### 1. Global Administrator Security Control Plane
* **Registration Requests Queue**: Review incoming healthcare institution applications, inspect legal contact information, mark under review, approve (auto-enrolling into active federation membership), or reject with a mandatory justification.
* **Hospital Directory**: Real-time directory of verified production hospitals with interactive 3D Orbital Radar topology.
* **Hospital Lifecycle Management**: Authoritative controls to suspend, restore, quarantine, release, or revoke hospital nodes with permanent audit log entries.
* **Federation Cohort Management**: Orchestrate federation clusters, inspect member join dates, and assign approved hospitals.
* **Round Configuration**: True separation of **Simulation Mode** (using isolated synthetic nodes for adversarial stress testing) vs. **Hospital Mode** (coordinating real approved hospital enclaves).
* **Live Round & Telemetry**: Real-time round progress monitoring via REST and WebSocket streaming (`/ws/events`).
* **Update Intake & L0–L5 Gate Telemetry**: Deep forensic inspection of candidate updates across all 6 analytical gates.
* **Human-in-the-Loop Overrides**: Authoritative adjudications for quarantined updates with logged justification notes.
* **Model Lineage & 3D Neural Explorer**: Sequential model lineage tree showing accuracy deltas, participant attributions, and interactive 3D layer visualization.
* **Forensic Round Replay & Reports**: 10-stage timeline scrubber and publication-grade executive attestation reports with print-to-PDF support.

### 2. Hospital Clinical Enclave Portal
* **Application Status Monitoring**: Unapproved hospitals see an institutional status screen with submitted details, current review state, or rejection reasons, with training strictly disabled until approved.
* **My Hospital Enclave Profile**: Update contact phone, email, official website, address, country, and institutional description via `PATCH /api/v1/hospital/profile`.
* **Team & Access Management**: Enclave administrators can list staff members, invite operators (`POST /api/v1/hospital/staff`), and toggle active status (`PATCH /api/v1/hospital/staff/{id}`).
* **Dataset Management Hub**: Ingest datasets via multi-format file uploads (.zip image archives, .tar.gz, .csv, .parquet, .npz) or external URLs/online repositories with automated shape validation `(N, 1, 28, 28)` and strict SSRF blocking.
* **Local In Situ Training**: Real PyTorch training runs locally on hospital hardware using server-verified global models; generates `.safetensors` update packages.
* **Submitted Updates Ledger**: Real-time view of submitted updates and security dispositions from `/api/v1/hospital/updates`.

---

## Authentication & Access Control

Access control is strictly enforced on the backend via stateless 256-bit JWT access tokens with Argon2id password hashing, database-backed active session checks, and tenant isolation:

1. **Initial Super Admin**: Initialized securely on first application startup via environment variables:
   * `ADMIN_EMAIL` (default: `admin@fedsentinel.org` or configured value)
   * `ADMIN_PASSWORD` (default: `Admin123!` or configured value)
2. **Hospital Enclave Registration**: Healthcare facilities submit an institutional application via the registration form on the portal login screen.
3. **Application Review**: Global administrators inspect credentials in the **Registration Requests** view and approve the institution, granting active federation access.
4. **Local Fixtures (Development/Testing)**: Run `python scripts/seed_dev_fixtures.py` to seed isolated local test fixtures without polluting production databases.

---

## Technology Stack

### Frontend SPA
* **Framework**: React 19 (`react`, `react-dom`)
* **3D Visualizations**: Three.js (`three`), React Three Fiber (`@react-three/fiber`), Drei (`@react-three/drei`)
* **Build Tool**: Vite 8 with Rollup bundling
* **Icons**: Lucide React
* **Typography**: Inter (UI elements) and JetBrains Mono (cryptographic hashes, tensors)
* **Hosting**: Vercel (Edge CDN, automatic HTTPS, SPA rewrites)

### Backend API
* **Runtime**: Python 3.11 / 3.12 / 3.13
* **Framework**: FastAPI with asynchronous endpoints & WebSockets
* **ASGI Server**: Uvicorn
* **Security & Auth**: PyJWT, Argon2id (`pwdlib`), HTTPBearer with database session verification
* **Validation**: Pydantic v2
* **Database & ORM**: SQLite / PostgreSQL with SQLAlchemy 2.0
* **Hosting**: Render (Web Service container with automated health checks)

### ML & Security Pipeline
* **Deep Learning Framework**: PyTorch 2.2+ (`torch`, `torchvision`)
* **Model Architecture**: `FedSentinelCNN` (Exact 105,866 parameters)
* **Serialization**: `safetensors` (zero-pickle security format) and verified `.npz` buffers
* **Data Processing**: NumPy, SciPy, Scikit-Learn

---

## Local Setup & Development

### 1. Prerequisites
* **Python**: 3.11+ (`python --version`)
* **Node.js**: v18+ & `npm` (`node -v`, `npm -v`)
* **Git**: (`git --version`)

### 2. Clone the Repository
```bash
git clone https://github.com/Reneshb24/FEDSENTINAL-X.git
cd FEDSENTINAL-X
```

### 3. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend server (Port 8000)
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation is available at: `http://127.0.0.1:8000/docs`

### 4. Frontend Setup
In a second terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server (Port 5173)
npm run dev
```
Open `http://localhost:5173` in your browser.

### 5. Running the Complete Verification Test Suite
```bash
# Run complete 89-item Pytest suite
pytest tests/ -v
```

---

## Cloud Deployment Guide

### Deploy Backend API on Render
1. Go to [dashboard.render.com](https://dashboard.render.com) and click **New +** $\\to$ **Web Service**.
2. Connect repository **Reneshb24/FEDSENTINAL-X**.
3. Configure:
   * **Runtime**: Python 3
   * **Build Command**: pip install -r requirements.txt
   * **Start Command**: uvicorn backend.main:app --host 0.0.0.0 --port 
   * **Environment Variables**:
     * ENVIRONMENT: production
     * JWT_SECRET_KEY: <secure-random-32-chars-key>
     * DATABASE_URL: sqlite:///./fedsentinel.db
4. Deploy and copy your Render URL (e.g. https://fedsentinel-api.onrender.com).

### Deploy Frontend on Vercel
1. Go to [vercel.com/new](https://vercel.com/new) and import **Reneshb24/FEDSENTINAL-X**.
2. Configure:
   * **Framework Preset**: Vite
   * **Root Directory**: rontend
   * **Build Command**: 
pm run build
   * **Output Directory**: dist
   * **Environment Variables**:
     * VITE_API_BASE_URL: <your-render-backend-url>
     * VITE_FEDERATION_ID: 413ef0b3-a947-4a02-a652-d963ef14b8da
3. Click **Deploy**. Vercel launches the application with instant edge delivery.

---

## Future Improvements

* **Differential Privacy ($\\epsilon, \\delta$) Budget Tracker**: Client-side calibrated Gaussian noise injection with formal RDP privacy accounting.
* **Hardware Enclave (TEE) Attestation**: Remote cryptographic attestation for Intel SGX and AWS Nitro Enclaves to verify execution integrity.
* **Homomorphic Encryption (CKKS)**: Encrypted coordinate aggregation allowing mathematical sum and median computation over encrypted ciphertexts.
* **Automated Neural Watermarking**: Embedding non-invasive cryptographic watermarks into global model weights to trace unauthorized weight exfiltration.

---

## Author

**Renesh B** — [@Reneshb24](https://github.com/Reneshb24)  
Project Repository: [https://github.com/Reneshb24/FEDSENTINAL-X](https://github.com/Reneshb24/FEDSENTINAL-X)

For in-depth mathematical formulations, threat model taxonomy, relational database schemas, and L0–L5 algorithmic specifications, consult:  
👉 [**docs/FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md**](docs/FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md)
