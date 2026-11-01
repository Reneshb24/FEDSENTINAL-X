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
* **14 Specialized 3D Visualizations with Interactive Telemetry & WebGL Fallbacks**:
  * **SOC Defense Shield** (`DefenseShield3D`): Interactive orbital shield in the Command Center with active health telemetry, pulse beacons, and risk rings.
  * **Federation Orbital Radar** (`FederationOrbit3D`): Multi-tier concentric orbits visualizing Trusted, Probation, and Quarantined institutions.
  * **Hospital Topology Radar** (`HospitalNetwork3D`): Geographic/network mesh of hospital nodes with live status halos, ping beams, and click inspection.
  * **L0 Volumetric Tensor Scanner** (`L0TensorScanner3D`): Rotating 3D tensor lattice with an animated scanning laser plane verifying SafeTensors format and zero-pickle integrity.
  * **L1 Norm Distribution Manifold** (`L1NormDistribution3D`): 3D update norm scatter plot showing 128-D projection boundaries and clipping envelopes.
  * **L2 Cosine Cluster Manifold** (`L2CosineCluster3D`): 3D angular coordinate cluster showing consensus convergence and robust MAD outlier separation.
  * **L3 Loss Surface Landscape** (`L3LossSurface3D`): 3D wireframe loss surface tracing candidate update gradient trajectories against holdout validation minima.
  * **L4 Counterfactual Trajectory** (`L4Counterfactual3D`): Dual-path 3D trajectory comparing consensus state with vs. without (Leave-One-Out) candidate updates.
  * **L5 Threat Attribution Radar** (`L5AttributionRadar3D`): 3D multi-axis radar chart projecting Bayesian posterior attack hypotheses (Backdoor, Scaling, Free-rider, Label-flip, Sybil, Benign non-IID).
  * **Trust Matrix Manifold** (`TrustMatrix3D`): 3D interactive matrix nodes dynamically color-coded by Bayesian reputation and historical consistency.
  * **Safe Aggregation Fusion Vortex** (`SafeAggregationVortex3D`): 3D particle vortex demonstrating candidate update convergence into the global model core via FedAvg, Coordinate Median, or Trimmed Mean.
  * **Neural Architecture Explorer** (`NeuralModel3D`): Interactive layer visualization of `FedSentinelCNN` feature maps, synaptic weight lines, and output class logits.
  * **Cryptographic Lineage Tree** (`ModelLineageTree3D`): 3D directed acyclic graph (DAG) of model checkpoint versions, SHA-256 hashes, and accuracy progressions.
  * **Synthetic Distribution Lab** (`SyntheticLab3D`): 3D client node manifold with real-time Dirichlet partition curves and class distribution histograms.
  * **Hospital Clinical Enclave Pipeline** (`HospitalEnclave3D`): 3D in situ enclave training pipeline visualizing local patient data isolation, PyTorch SGD execution, differential delta extraction, and SafeTensors packaging with zero data egress.
* **Synthetic Attack Sandbox & Benchmark Lab**: Test the defense pipeline against synthetic cohorts with configurable distribution models: Clean IID, Non-IID Dirichlet ($\alpha \in [0.05, 10.0]$), Pathological Label Skew, Pixel-pattern Backdoor Triggers, and Sybil Model Replacement attacks.
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
* **SOC Command Center**: High-level federation posture, live incident feed, round metrics, and interactive 3D Defense Shield (`DefenseShield3D`).
* **Federation Overview**: Multi-tier orbital topology (`FederationOrbit3D`) categorizing nodes by Trusted, Probation, and Quarantined tiers with live ping status.
* **Registration Requests Queue**: Review incoming healthcare institution applications, inspect contact and legal credentials, transition to under-review, approve with instant federation onboarding, or reject with a mandatory justification.
* **Hospital Control Center**: Consolidated hospital fleet operations featuring 3D topology radar (`HospitalNetwork3D`), search and filtering by security status/tier, hospital cards with trust metrics, and an integrated management drawer with instant actions (Approve, Suspend, Quarantine, Release, Revoke).
* **Federation Cohort Management**: Orchestrate federation clusters, configure participant eligibility toggles, and view institutional join history.
* **Synthetic Lab & Attack Sandbox**: Interactive benchmarking environment with `SyntheticLab3D` visualization. Configure Dirichlet skew ($\alpha \in [0.05, 10.0]$), pathological label concentration, backdoor triggers, and sybil model replacements to evaluate L0–L5 defense gates without impacting production clinical enclaves.
* **Round Configuration**: Strict separation of **Simulation Mode** (isolated synthetic clients for adversarial experimentation) vs. **Hospital Mode** (coordinating real, verified clinical enclaves). Dynamic participant slider, preset buttons, hyperparameter inputs, and stale round cancellation.
* **Live Round & Telemetry**: 10-stage execution pipeline monitoring with real-time participant progress, loss tracking, and gate-by-gate verification.
* **Update Intake Ledger**: Ingested candidate SafeTensors updates, SHA-256 fingerprint verification, payload inspector, and defense pipeline triggers.
* **Multi-Tier L0–L5 Defense Suite**:
  * **L0 Verify**: SafeTensors format and zero-pickle verification with 3D volumetric tensor scanner (`L0TensorScanner3D`).
  * **L1 Inspect**: 128-D privacy projection and NaN/Inf numeric sanity filter with 3D norm distribution manifold (`L1NormDistribution3D`).
  * **L2 Correlate**: Robust MAD coordinate-wise outlier scores and cosine similarity matrix with 3D cluster manifold (`L2CosineCluster3D`).
  * **Quarantine Vault**: Forensic isolation chamber for suspicious updates with audited release and permanent discard actions.
  * **L3 Influence**: Holdout validation loss gradient trajectory profiling with 3D loss surface landscape (`L3LossSurface3D`).
  * **L4 Simulate**: Leave-One-Out counterfactual shadow consensus simulation ($\Delta \text{Acc}$) with 3D trajectory visualizer (`L4Counterfactual3D`).
  * **L5 Attribute**: Dynamic Bayesian threat hypothesis attribution with 3D multi-axis radar chart (`L5AttributionRadar3D`).
* **Trust Engine**: Global Bayesian reputation scoring with interactive 3D trust matrix (`TrustMatrix3D`), dynamic attenuation decay, and non-punitive clinical tolerance.
* **Incident Management**: Centralized threat feed with severity filters (Critical, High, Medium, Low), incident acknowledgment, and forensic resolution logging.
* **Human-in-the-Loop Overrides**: Immutable audit ledger of security officer manual overrides with mandatory rationale recording.
* **Safe Aggregation Core**: Multi-algorithm consensus engine (FedAvg, Coordinate Median, Trimmed Mean) with 3D particle fusion vortex (`SafeAggregationVortex3D`).
* **Global Model Explorer**: Deep neural layer inspector for `FedSentinelCNN` (Conv1, Conv2, FC1, FC2) with 3D neural explorer (`NeuralModel3D`) and SafeTensors export.
* **Model Lineage DAG**: Cryptographic parent-child model version tree with 3D lineage visualization (`ModelLineageTree3D`) and audited checkpoint rollback.
* **Cryptographic Audit Ledger**: Immutable, append-only log of all federation events, actor identities, IP addresses, and timestamps with JSON/CSV export and SHA-256 chain verification.
* **Round Replay**: Interactive 10-stage timeline scrubber with play, pause, step-forward, and variable speed playback (`0.5x`, `1x`, `2x`, `4x`).
* **Attestation Dossiers**: Publication-grade compliance reports aligned with HIPAA Security Rule, FDA 21 CFR Part 11, EU AI Act, and NIST AI RMF with print-to-PDF export.

### 2. Hospital Clinical Enclave Portal
* **Institutional Registration**: Self-service onboarding portal allowing hospitals to submit legal credentials, primary contacts, and clinical specialization.
* **Application Status Monitoring**: Unapproved hospitals view application review status, submitted details, and administrative notes, with training strictly locked until approved.
* **Hospital Command**: Enclave operational dashboard with health posture, active round status, enrolled dataset count, and trust tier indicator.
* **My Hospital Enclave Profile**: Update institutional contact info, physical address, website, and clinical description, plus secure password change modal.
* **Federation Membership**: Consortium details, participating peers, active federation parameters, and institutional join dates.
* **Team & Access Management**: Enclave administrators manage local operators, invite staff members (`POST /api/v1/hospital/staff`), and toggle active account status.
* **Dataset Management Hub**: Ingest datasets via multi-format file uploads (.zip image archives, .tar.gz, .csv, .parquet, .npz), verified external URLs (Hugging Face, GitHub, Zenodo, Kaggle) with strict SSRF protection, or built-in in situ clinical benchmark generation.
* **Data Quality Register**: 5-point clinical data validation checklist (SafeTensors/Zero-Pickle, normalized $(1, 28, 28)$ tensor shape, 0% NaN/Inf finite values, class balance, minimum sample size) with one-click activation for federation training.
* **Current Round Inspection**: Real-time round progress, hyperparameter specifications, and enclave eligibility status.
* **In Situ Local Model Training**: Authentic PyTorch training running on private hospital hardware with 3D enclave pipeline visualizer (`HospitalEnclave3D`), live epoch-by-epoch loss tracking, differential delta extraction, and SafeTensors compilation with zero data egress.
* **Model Updates Ledger**: History of submitted differential updates, cryptographic hashes, and L0–L5 gate verdicts (Accepted vs. Quarantined).
* **Global Model Inspection**: Download consensus SafeTensors weights and verify model accuracy.
* **Enclave Security Status & Self-Test**: Hardware boundary verification, zero data egress guarantee, and 6-layer defense gate checklist.
* **Clinical Incidents**: Enclave-specific threat alerts, forensic explanations, and direct "Request Administrative Review" mechanism.
* **Visual Trust Engine**: Circular SVG reputation dial, Bayesian scoring parameters ($\alpha, \beta, \lambda$), evaluation log, and clinical good faith guarantee.
* **Reports & Local Audit**: Export local training logs, generate compliance summaries, and review local operator activity.

---

## Authentication & Access Control

Access control is strictly enforced on the backend via stateless 256-bit JWT access tokens with Argon2id password hashing, database-backed active session checks, and tenant isolation:

1. **Initial Super Admin**: Initialized securely on first application startup via environment variables:
   * `ADMIN_EMAIL` (default: `admin@fedsentinel.local` or configured value)
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
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   * **Environment Variables**:
     * `ENVIRONMENT`: `production`
     * `JWT_SECRET_KEY`: `<secure-random-32-chars-key>`
     * `DATABASE_URL`: `sqlite:///./fedsentinel.db`
4. Deploy and copy your Render URL (e.g. `https://fedsentinel-api.onrender.com`).

### Deploy Frontend on Vercel
1. Go to [vercel.com/new](https://vercel.com/new) and import **Reneshb24/FEDSENTINAL-X**.
2. Configure:
   * **Framework Preset**: Vite
   * **Root Directory**: `frontend`
   * **Build Command**: `npm run build`
   * **Output Directory**: `dist`
   * **Environment Variables**:
     * `VITE_API_BASE_URL`: `<your-render-backend-url>`
     * `VITE_FEDERATION_ID`: `413ef0b3-a947-4a02-a652-d963ef14b8da`
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
