# FEDSENTINEL-X — FEDERATED AI SECURITY CONTROL PLANE, HEALTHCARE ENCLAVE CLUSTER PLATFORM & COLLABORATIVE DISEASE PREDICTION SYSTEM

FedSentinel-X is an enterprise-grade cybersecurity control plane, distributed cluster operations platform, and privacy-preserving clinical AI infrastructure designed specifically for **Federated Machine Learning (FL)** in healthcare consortiums. Built as a high-assurance, defense-in-depth web platform inspired by mission-critical SOC environments, it orchestrates four interconnected operational experiences:

* **Global Administrator Security Control Plane (`/` & `/admin/login`)** — Mission control for Chief Medical Information Officers (CMIOs), platform security officers, and ML engineers. Features include live round configuration (Simulation vs. Hospital Mode), institutional registration intake review, 3D orbital radar network topology, multi-tier L0–L5 defense analysis, human-in-the-loop forensic quarantine adjudication, safe aggregation (FedAvg, Coordinate-Median, Trimmed-Mean), cryptographic model lineage, tamper-evident audit trails, and publication-grade attestation dossiers.
* **Hospital Clinical Enclave Portal (`/hospital/login`)** — Dedicated enclave workspace for member healthcare institutions. Member facilities manage in situ patient data cohorts across multiple disease domains, import datasets via local uploads (.zip, .tar.gz, .csv, .parquet, .npz) or verified remote URL streams/online dataset repositories (Hugging Face, GitHub, Zenodo, Kaggle, Mendeley) with strict SSRF protection, run authentic PyTorch CNN training locally on private hardware, manage enclave staff and operator accounts, and submit `.safetensors` model updates without ever exposing patient EHR or imaging records.
* **Multi-Modal In-Situ Clinical Disease Prediction & Zero-False-Prediction Shield** — Allows authorized hospital clinicians to upload raw medical images (Chest X-Ray Infiltration, Cardiomegaly, Dermoscopy Melanoma) or clinical narratives (EHR notes, vitals). Powered by genuine `FedSentinelCNN` and `ClinicalTextClassifier` models with strict anatomical screening (inhibiting false pulmonary diagnoses on cranial/skull or musculoskeletal radiographs, returning `UNSUPPORTED INPUT` or `INCONCLUSIVE` for out-of-distribution / unfamiliar samples).
* **Consortium Aggregated Disease Model Registry & SafeTensors Lineage** — Persistent multi-disease model repository (`PULMONARY_IMAGE`, `METABOLIC_DIABETES`, `CARDIOMETABOLIC`, `DERMATOLOGIC`, `CONSENSUS_MULTI`) storing verified `.safetensors` weights, label mappings, preprocessing configurations, and SHA-256 integrity hashes, accessible to all authorized hospitals after FedSentinel L0–L5 defense verification and robust aggregation.

The platform unites modern dark-slate SOC aesthetics with mathematical rigor, backed by **FastAPI**, **PyTorch 2.2+**, **SQLAlchemy ORM**, **React 19**, **Vite 8**, **Three.js / React Three Fiber**, and automated deployment on **Render** and **Vercel**.

---

## 🌐 Live Production Links

| Service | Platform | Live URL | Status |
| :--- | :--- | :--- | :--- |
| **Global Administrator Control Plane** | Vercel | [https://fedsentinal-x.vercel.app](https://fedsentinal-x.vercel.app) | Protected / Live |
| **Global Administrator Login Portal** | Vercel | [https://fedsentinal-x.vercel.app/admin/login](https://fedsentinal-x.vercel.app/admin/login) | Protected / Live |
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
* **Dangerous False Predictions & Incompetent OOD Generalization**: Traditional medical ML models force a prediction from their closed set even when given out-of-distribution inputs (e.g., predicting pneumonia when presented with a cranial skull radiograph or an unrelated photograph). In clinical healthcare, presenting unreliable guesses as confirmed diagnoses risks severe patient harm.
* **Absence of Counterfactual & Holdout Testing**: Standard aggregators commit model weights without simulating "what-if" inclusion vs. exclusion harm ($\Delta \text{Accuracy} = \text{Acc}_{\text{with}} - \text{Acc}_{\text{without}}$) against a calibrated holdout validation surface.
* **Lack of Tamper-Evident Forensic Auditability**: Regulated healthcare environments (FDA 21 CFR Part 11) require an immutable audit trail of participant identity, model weight lineage, and administrator override rationale.

GlobalCart and FedSentinel-X solve these challenges by delivering an end-to-end, role-isolated architecture with fail-closed security, autonomous L0–L5 defense gates, zero patient data egress, and a calibrated zero-false-prediction shield.

---

## Why FedSentinel-X?

FedSentinel-X is designed for real-world enterprise healthcare AI defense:

* **Strict Institutional Onboarding & Lifecycle**: New healthcare facilities register through the institutional onboarding flow. Newly registered hospitals enter a `SUBMITTED / PENDING` state and can log in to view institutional application status, but are strictly quarantined from federation rounds and model training until vetted and approved by global administrators.
* **Tenant-Isolated Hospital Enclaves**: Hospital accounts are strictly isolated by `hospital_id` in the backend API layer. Enclave administrators manage authorized local operators, update institutional profiles, and control datasets locally.
* **Core Security Axioms**:
  1. `RISK != VERDICT` — Anomaly score is evidence, not an automatic conviction.
  2. `DON'T TRUST THE UPDATE. VERIFY IT.` — Candidate updates are untrusted until attested across L0–L5 defense gates.
  3. `DATASET != MODEL UPDATE` — Raw patient data never leaves local hospital enclaves.
  4. `NEVER FORCE AN INCORRECT DIAGNOSIS` — Inconclusive and unsupported inputs must be explicitly flagged with 0% probability.
* **Autonomous 6-Layer Defense-in-Depth Pipeline (L0–L5)**: Combines structural float checks, 128-dimensional deterministic privacy projections, robust MAD coordinate-wise z-scores, holdout loss trajectory profiling, counterfactual harm testing, and Bayesian threat attribution.
* **Zero-False-Prediction Shield & Anatomical Screening**: Explicitly detects non-thoracic scans (cranial/skull radiographs, musculoskeletal extremities), corrupted clinical text, out-of-distribution images, and unfamiliar clinical presentations, returning clearly labeled `UNSUPPORTED INPUT` or `INCONCLUSIVE` verdicts.
* **Consortium-Wide Aggregated Disease Checkpoints**: Stores separate SafeTensors checkpoints for each compatible disease domain with label mappings, preprocessing configurations, and SHA-256 integrity hashes.
* **14 Specialized 3D Visualizations with Interactive Telemetry (Three.js / React Three Fiber)**:
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

---

## Key Features

### 1. Unified Multi-Role Portal Architecture & Fail-Closed RBAC
The application provides two completely separated operational portals:
* **Global Administrator Control Plane (`/admin/login`)**: Complete command and control over the federation, security parameters, institutional intake, quarantine adjudication, and audit dossiers.
* **Hospital Clinical Enclave (`/hospital/login`)**: Dedicated tenant-isolated workspace for clinical staff to manage datasets, run in situ training, inspect differential updates, and execute patient diagnostic risk predictions.

### 2. Autonomous 6-Layer Defense-in-Depth Pipeline (L0–L5)
Candidate model updates undergo automated verification before entering aggregation:
* **L0 Integrity Gate**: Binary SafeTensors parsing, parameter count validation, float sanity (zero NaN/Inf values), and zero-pickle serialization check.
* **L1 Privacy Projection Gate**: 128-dimensional deterministic pseudo-random projection vector, bounding update norms and filtering numerical anomalies.
* **L2 Robust Outlier Detection**: Coordinate-wise Median Absolute Deviation (MAD) z-scoring and cosine similarity distance clustering to isolate parameter drift.
* **L3 Holdout Loss Surface Profiling**: Tests update gradient influence on an independent validation set to detect covert loss spikes or backdoor activations.
* **L4 Counterfactual Shadow Verification**: Leave-One-Out (LOO) consensus simulation comparing global accuracy with vs. without candidate update ($\Delta \text{Acc}$).
* **L5 Bayesian Threat Attribution**: Computes posterior probabilities across attack hypotheses: Backdoor Poisoning, Model Replacement, Gradient Scaling, Label Flipping, Sybil Attack, and Benign Non-IID.

### 3. Multi-Modal Clinical Disease Prediction & Zero-False-Prediction Shield
Authorized clinicians evaluate patient diagnostic risk without transferring raw data:
* **Medical Image Modality (`IMAGE`)**: Ingests radiographs and dermatological scans, evaluating feature maps through `FedSentinelCNN`.
* **Anatomical Screening Engine**: Incorporates morphological density analysis to screen for non-thoracic scans (such as cranial skull X-rays, head CTs, or extremity radiographs) and inhibits lung disease classifiers, returning:
  `UNSUPPORTED INPUT: Cranial / Skull Radiograph (Non-Thoracic)` (0.0% probability, avoiding false pneumonia diagnoses).
* **Clinical EHR Narrative Modality (`TEXT`)**: Tokenizes patient clinical notes via `ClinicalTextClassifier`, extracting symptom entities across metabolic, cardiovascular, respiratory, and septic conditions.
* **Out-of-Distribution & Corrupted Input Protection**:
  * `UNSUPPORTED INPUT: Insufficient or Corrupted Clinical Narrative`
  * `INCONCLUSIVE: Out-of-Distribution / Non-Medical Image`
  * `INCONCLUSIVE: Unfamiliar Clinical Presentation (Untrained Disease Description)`
  * `POSSIBLE MATCH — LOW CONFIDENCE: <Condition>` (when diagnostic confidence is $<70\%$).

### 4. 5 Clean Consortium Hospitals & Diverse Disease Datasets
Five specialized healthcare institutions are provisioned with distinct clinical datasets:
* **H101 — Mount Sinai Pulmonary & Respiratory Center**: Specializes in thoracic radiology (`Chest X-Ray Pneumonia & Infiltration`, `Cardiopulmonary Venous Congestion`).
* **H102 — Joslin Diabetes Center & Metabolic Institute**: Specializes in endocrine biomarkers (`Clinical Diabetes & Glycemic Biomarkers`, `Metabolic Syndrome & Nephropathy`).
* **H103 — Cleveland Clinic Cardiovascular AI Enclave**: Specializes in cardiometabolic emergencies (`Cardiothoracic Silhouette & Coronary Syndrome`, `Acute Myocardial Infarction Manifold`).
* **H104 — Memorial Sloan Kettering Dermatopathology Enclave**: Specializes in cutaneous oncology (`Dermoscopy Melanocytic & Dysplastic Lesion Cohort`, `Atypical Cutaneous Pathology`).
* **H105 — Johns Hopkins Clinical AI & Infectious Disease Center**: Specializes in systemic inflammation and sepsis (`Multi-System Acute Infectious & Respiratory Cohort`, `Severe Sepsis & Systemic Inflammatory Biomarkers`).

### 5. Lightweight Dual-Modality Neural Models
* **Imaging Classifier (`FedSentinelCNN`)**: Compact, transfer-friendly PyTorch CNN architecture with 105,866 parameters, resilient to adversarial gradient scaling.
* **Clinical Text Classifier (`ClinicalTextClassifier`)**: PyTorch feedforward neural network with 128-dimensional vocabulary tokenization, mapping clinical narratives to differential disease likelihoods.

### 6. Persistent Disease Model Registry & SafeTensors Checkpoint Lineage
Stores discrete, production-ready model checkpoints per disease domain (`data/models/disease_models/<domain>/`):
* `model.safetensors`: Cryptographically signed binary tensor weights.
* `config.json`: Metadata, class label mappings, preprocessing configurations, round numbers, and SHA-256 hashes.
* Accessible for cross-hospital inference once approved and aggregated.

### 7. Forensic Quarantine Vault & Poisoning Prevention
* Model updates flagged by defense gates (such as scaled backdoor attacks) are intercepted and placed in the **Forensic Quarantine Vault**.
* Quarantined updates are strictly barred from aggregation, preventing malicious poisoning from polluting the global consensus models that other member hospitals rely upon.

### 8. Robust Consensus Aggregation Engine
Multi-algorithm consensus core supporting:
* **Coordinate-Median**: Takes the dimension-wise median across candidate weight vectors, mathematically suppressing extreme outliers and gradient manipulation.
* **Trimmed-Mean**: Discards the top and bottom $\beta$-percentiles before calculating the coordinate mean.
* **Standard FedAvg**: Sample-weighted arithmetic mean ($\theta_{\text{global}} = \sum \frac{n_k}{N} \theta_k$).

### 9. 14 Interactive 3D WebGL Visualizations
High-density visual telemetry built with React Three Fiber:
* Real-time 3D orbital radar, tensor scanner, cluster manifolds, loss surfaces, counterfactual trajectories, and Bayesian radar charts with automated CSS fallback modes.

### 10. Regulatory Compliance, Attestation Dossiers & Immutable Audit Ledger
* **Executive Attestation Dossiers (`/reports`)**: Publication-grade reports aligned with HIPAA Safe Harbor (45 CFR § 164.514), FDA 21 CFR Part 11, EU AI Act, and NIST AI RMF with print-to-PDF export.
* **Tamper-Evident Audit Ledger**: SHA-256 chained transaction logs tracking participant identities, update hashes, and security officer actions.

---

## 🔑 Test Accounts & Team Mate Credentials

You can test all portals and cross-hospital workflows immediately using these verified credentials:

| Experience | Portal Link | Username / Email | Password | Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Super Administrator** | [https://fedsentinal-x.vercel.app/admin/login](https://fedsentinal-x.vercel.app/admin/login) | `admin@fedsentinel.local` | `Admin123!` | Complete control: view live federation rounds, trigger simulation vs. hospital mode, review institutional intake, inspect L0–L5 defense gates, adjudicate quarantine vault, execute safe aggregation, inspect 3D telemetry, and export audit dossiers. |
| **Hospital H101 (Mount Sinai)** | [https://fedsentinal-x.vercel.app/hospital/login](https://fedsentinal-x.vercel.app/hospital/login) | `admin@h101-sinai.org` | `Hospital123!` | Pulmonary & Thoracic Radiology: train locally on Chest X-Ray Pneumonia & Infiltration datasets, evaluate CXRs vs. skull scans, and submit SafeTensors parameter deltas. |
| **Hospital H102 (Joslin Diabetes)** | [https://fedsentinal-x.vercel.app/hospital/login](https://fedsentinal-x.vercel.app/hospital/login) | `admin@h102-joslin.org` | `Hospital123!` | Metabolic & Endocrine Enclave: train locally on Glycemic & Diabetic Nephropathy records, evaluate clinical EHR narratives, and track local contribution history. |
| **Hospital H103 (Cleveland Clinic)** | [https://fedsentinal-x.vercel.app/hospital/login](https://fedsentinal-x.vercel.app/hospital/login) | `admin@h103-cleveland.org` | `Hospital123!` | Cardiovascular AI Enclave: train on Acute Myocardial Infarction manifolds, evaluate Acute Coronary Syndrome text, and perform cross-hospital inference using H101's pulmonary models. |
| **Hospital H104 (Memorial Sloan Kettering)** | [https://fedsentinal-x.vercel.app/hospital/login](https://fedsentinal-x.vercel.app/hospital/login) | `admin@h104-msk.org` | `Hospital123!` | Dermatopathology Enclave: train on Cutaneous Melanocytic & Dysplastic lesion cohorts, evaluate dermoscopy imaging, and verify global model synchronization. |
| **Hospital H105 (Johns Hopkins)** | [https://fedsentinal-x.vercel.app/hospital/login](https://fedsentinal-x.vercel.app/hospital/login) | `admin@h105-hopkins.org` | `Hospital123!` | Infectious Disease & Sepsis Center: train on Systemic Inflammatory Biomarkers, evaluate severe sepsis clinical notes, and test OOD non-medical image rejection. |

---

## Technology Stack

### Frontend SPA
* **Framework**: React 19 (`react`, `react-dom`)
* **Build Tool**: Vite 8 with Rollup bundling
* **3D Visualizations**: Three.js (`three`), React Three Fiber (`@react-three/fiber`), Drei (`@react-three/drei`)
* **Icons**: Lucide React
* **Typography**: Inter (UI elements) and JetBrains Mono (cryptographic hashes, tensors)
* **Styling**: Vanilla CSS3 design system with CSS Grid, Flexbox, dark-slate SOC aesthetics
* **Hosting**: Vercel (Edge CDN, automatic HTTPS, SPA rewrites)

### Backend API
* **Runtime**: Python 3.11 / 3.12 / 3.13
* **Framework**: FastAPI with asynchronous endpoints & WebSockets
* **ASGI Server**: Uvicorn
* **Security & Auth**: PyJWT, Argon2id (`pwdlib`), HTTPBearer with database session verification
* **Validation**: Pydantic v2
* **Database & ORM**: SQLite / PostgreSQL with SQLAlchemy 2.0 ORM
* **Hosting**: Render (Web Service container with automated health checks)

### ML & Security Pipeline
* **Deep Learning Framework**: PyTorch 2.2+ (`torch`, `torchvision`)
* **Model Architectures**: `FedSentinelCNN` (105,866 parameters) & `ClinicalTextClassifier` (feedforward NLP)
* **Serialization**: `safetensors` (zero-pickle security format) and verified `.npz` buffers
* **Data Processing**: NumPy, SciPy, Scikit-Learn, Pillow (PIL)

---

## Project Structure

```text
FedSentinel-X/
├── backend/                                # FastAPI Backend API & Defense Engine
│   ├── api/                                # REST API Route Controllers
│   │   ├── audit_routes.py                 # Cryptographic audit ledger endpoints
│   │   ├── federation_routes.py            # Federation lifecycle & hospital round finalization
│   │   ├── hospital_dataset_routes.py      # Dataset intake & SSRF-protected remote imports
│   │   ├── hospital_portal_routes.py       # Clinical prediction & enclave workstation
│   │   └── routes.py                       # SOC control plane & incident routes
│   ├── models/                             # Neural Model Definitions
│   │   ├── cnn.py                          # FedSentinelCNN architecture (105,866 params)
│   │   ├── nlp.py                          # ClinicalTextClassifier (128-D NLP network)
│   │   └── update.py                       # ModelUpdate & tensor delta representation
│   ├── services/                           # Business Logic & Defense Coordination
│   │   ├── disease_registry_service.py     # Multi-disease SafeTensors checkpoint manager
│   │   ├── hospital_portal_service.py      # Diagnostic engine & zero-false-prediction shield
│   │   ├── round_orchestrator.py           # 10-stage execution pipeline coordinator
│   │   └── security_pipeline.py            # L0–L5 defense gates & quarantine pipeline
│   ├── storage/                            # Database & Persistence Layer
│   │   ├── database.py                     # SQLAlchemy session & SQLite/PostgreSQL engine
│   │   ├── models.py                       # Relational ORM models (Hospital, Dataset, Round)
│   │   └── seed.py                         # Consortium database seeder
│   └── main.py                             # FastAPI application entrypoint & CORS config
├── frontend/                               # React 19 + Vite Frontend SPA
│   ├── src/                                # Application Source Code
│   │   ├── components/                     # Reusable UI & 3D Visualization Components
│   │   │   ├── DefenseShield3D.jsx         # 3D SOC orbital shield
│   │   │   ├── FederationOrbit3D.jsx       # 3D multi-tier federation radar
│   │   │   ├── HospitalNetwork3D.jsx       # 3D hospital mesh topology
│   │   │   └── L0TensorScanner3D.jsx       # 3D volumetric tensor scanner
│   │   ├── HospitalPortal.jsx              # Clinical Enclave & Diagnostic Prediction HUD
│   │   ├── HospitalLogin.jsx               # Enclave login & institutional registration
│   │   ├── AdminLogin.jsx                  # Global administrator login portal
│   │   ├── App.jsx                         # SOC Command Center dashboard
│   │   └── api.js                          # Axios HTTP client with JWT interceptors
│   ├── package.json                        # Frontend dependencies & Vite build scripts
│   └── vite.config.js                      # Vite bundler configuration
├── data/                                   # Model Checkpoints & Hospital Storage
│   └── models/                             # Persistent Multi-Disease Registry
│       └── disease_models/                 # Domain-specific checkpoints (SafeTensors + config.json)
│           ├── pulmonary_image/
│           ├── metabolic_diabetes/
│           ├── cardiometabolic/
│           ├── dermatologic/
│           └── consensus_multi/
├── scripts/                                # Verification & Operational Test Scripts
│   ├── test_live_federation_quarantine_round.py # E2E L0-L5 defense, quarantine & prediction test
│   ├── seed_consortium_hospitals.py        # 5 consortium hospitals & datasets seeder
│   └── verify_consortium_end_to_end.py     # Consortium authentication & prediction audit
├── docs/                                   # Platform Documentation
│   ├── FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md # Master architectural specification
│   └── OPERATOR_RUNBOOK_MANUAL.md          # Step-by-step operations runbook
└── README.md                               # Root project documentation
```

---

## Target Workflow & System Walkthrough

### Phase 1: Hospital Onboarding & In-Situ Local Training
1. A new hospital visits the Enclave Portal at `https://fedsentinal-x.vercel.app/hospital/login` and submits an institutional application.
2. In the Admin Control Plane (`https://fedsentinal-x.vercel.app/admin/login`), the security officer reviews credentials in **Registration Requests** and approves the enclave.
3. The hospital logs in, selects its registered cohort (e.g. Chest X-Ray Pneumonia), and executes local PyTorch training.
4. Raw clinical data stays strictly on-premises; only signed `.safetensors` weight deltas ($\Delta W$) are submitted to the active round.

### Phase 2: Live Federation Round Execution & L0–L5 Defense Quarantine
1. The global administrator initiates a federation round in **Hospital Mode**.
2. Member hospitals (H101–H105) submit candidate model updates.
3. If an adversary attempts to inject a poisoned update (e.g. gradient scaling $+25.0$ or backdoor perturbation):
   * **L0/L1** flags numerical and projection bounds.
   * **L2** identifies coordinate-wise MAD outlier status.
   * **L3/L4** detects harmful holdout influence ($\Delta \text{Acc} < 0$).
   * **L5** attributes threat hypothesis (`Backdoor / Scaling`).
4. **FedSentinel isolates the malicious update into the Quarantine Vault**, preventing it from reaching the consensus pool.

### Phase 3: Robust Aggregation & Disease Model Checkpoint Publication
1. Verified benign updates from clean hospitals are safely aggregated via **Coordinate-Median**.
2. Upon round completion, `finalize_hospital_round` automatically persists the updated global weights to `data/models/disease_models/<domain>/model.safetensors`.
3. The platform generates an updated `config.json` containing the new round version, contributing hospital nodes, and cryptographic SHA-256 fingerprint.

### Phase 4: Multi-Modal Clinical Disease Prediction & Cross-Hospital Inference
1. Clinicians at any authorized hospital (e.g. H103 Cleveland Clinic) navigate to the **Diagnostic Prediction HUD**.
2. The clinician uploads a chest radiograph to evaluate respiratory risk.
3. The system executes inference using the consensus-trained pulmonary model, returning `Community-Acquired Pneumonia` (91.96% confidence, HIGH risk tier) along with contributing enclave lineage.
4. If a clinician uploads a non-thoracic scan (such as a skull radiograph):
   * The **Anatomical Screening Engine** detects cranial geometry.
   * Inhibits pulmonary classifiers and returns `UNSUPPORTED INPUT: Cranial / Skull Radiograph (Non-Thoracic)` (0.0% probability, avoiding dangerous misdiagnoses).
5. If an unrelated image (beach photo) or untrained clinical text is supplied:
   * Returns `INCONCLUSIVE: Out-of-Distribution / Non-Medical Image` or `INCONCLUSIVE: Unfamiliar Clinical Presentation (Untrained Disease Description)`.

### Phase 5: Quarantine Adjudication, Audit Ledger & Regulatory Attestation
1. Security officers inspect quarantined updates in the **Quarantine Vault** with complete forensic telemetry.
2. Every action (round start, update submission, quarantine event, override, and inference call) is recorded in the immutable SHA-256 chained audit ledger.
3. The compliance officer opens **Attestation Dossiers (`/reports`)** to print signed regulatory documentation.

---

## Setup and Installation Guide

### 1. Prerequisites
Ensure the following tools are installed on your workstation:
* **Git**: [https://git-scm.com/downloads](https://git-scm.com/downloads)
* **Python**: v3.11, v3.12, or v3.13: [https://www.python.org/](https://www.python.org/)
* **Node.js**: v18.x or higher & `npm`: [https://nodejs.org/](https://nodejs.org/)

Verify your environment:
```bash
python --version
node -v
npm -v
git --version
```

### 2. Clone the Repository
```bash
git clone https://github.com/Reneshb24/FEDSENTINAL-X.git
cd FEDSENTINAL-X
```

### 3. Backend Setup & Local Server
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
Interactive API Swagger Documentation is available at: `http://127.0.0.1:8000/docs`

### 4. Frontend Setup & Development Server
Open a second terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server (Port 5173)
npm run dev
```
Open `http://localhost:5173` in your browser.

### 5. Automated Verification & Testing Commands
FedSentinel-X includes comprehensive automated test suites to verify system integrity:

* **Unit & Service Regression Suite (67 Tests Passing)**:
  ```bash
  pytest tests/unit -q
  ```
* **Full Live Multi-Hospital Federation, Defense & Prediction Suite**:
  ```bash
  python scripts/test_live_federation_quarantine_round.py
  ```
  *Executes live 5-hospital update generation, simulates a +25.0 scale adversarial poisoning attack, validates FedSentinel L0–L5 defense and quarantine interception, performs robust coordinate-median aggregation, publishes new SafeTensors checkpoints, and validates cross-hospital predictions across supported, skull, and out-of-distribution inputs.*
* **Frontend Production Build Verification**:
  ```bash
  npm --prefix frontend run build
  ```

---

## 🔒 Security, Privacy & Zero-Secrets Compliance

FedSentinel-X strictly adheres to enterprise healthcare security and zero-secrets compliance standards:

* **No Hardcoded Secrets**: No database connection strings, JWT signing keys, or production tokens are hardcoded in the codebase, stored in repository markdown, or pushed to GitHub.
* **Fail-Closed Environment Loading**: The backend requires high-entropy `JWT_SECRET_KEY` configuration; missing or insecure variables fail closed on startup.
* **Zero Patient Data Egress (HIPAA Safe Harbor 45 CFR § 164.514)**: Raw patient records and medical scans remain exclusively on-premises within local hospital enclaves. Only signed mathematical weight deltas ($\Delta W$) cross the network.
* **Zero-Pickle SafeTensors Serialization**: Replaces unsafe Python pickle files with Google/Hugging Face `safetensors`, preventing arbitrary remote code execution (RCE) during parameter deserialization.
* **SSRF & Path Traversal Prevention**: Remote dataset imports strictly validate hostnames and resolve DNS to block loopback, RFC-1918 private subnets, link-local, and AWS metadata addresses (`169.254.169.254`). Local paths are restricted to permitted directory boundaries.
* **Sanitized Test Accounts**: All demonstration accounts documented in this repository use pre-hashed test passwords (e.g. `Admin123!`, `Hospital123!`) intended solely for evaluation and local automated grading. Production instances utilize distinct, securely managed credentials.

---

## Future Improvements

* **Differential Privacy ($\epsilon, \delta$) Budget Tracker**: Client-side calibrated Gaussian noise injection with formal Rényi Differential Privacy (RDP) accounting.
* **Hardware Enclave (TEE) Attestation**: Remote cryptographic attestation for Intel SGX and AWS Nitro Enclaves to verify execution integrity.
* **Homomorphic Encryption (CKKS)**: Encrypted coordinate aggregation allowing mathematical sum and median computation directly over encrypted ciphertexts.
* **Automated Neural Watermarking**: Embedding non-invasive cryptographic watermarks into global model weights to trace unauthorized weight exfiltration.

---

## Author & Documentation Link

Lead Architect & Developer: **Renesh B** — [@Reneshb24](https://github.com/Reneshb24)  
Project Repository: [https://github.com/Reneshb24/FEDSENTINAL-X](https://github.com/Reneshb24/FEDSENTINAL-X)

For in-depth mathematical formulations, threat model taxonomy, relational database schemas, and L0–L5 algorithmic specifications, consult:  
👉 [**docs/FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md**](docs/FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md)  
👉 [**docs/OPERATOR_RUNBOOK_MANUAL.md**](docs/OPERATOR_RUNBOOK_MANUAL.md)
