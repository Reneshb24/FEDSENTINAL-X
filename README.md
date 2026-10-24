# FedSentinel-X

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

### The Enterprise Security Control Plane for Federated AI & Collaborative Healthcare ML

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8+-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Zero--Trust](https://img.shields.io/badge/Security-Zero--Trust%20L0--L5-00e5ff?style=for-the-badge)](https://fedsentinel.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

[Live Demo](#cloud-deployment-guide) • [Architecture](#system-architecture) • [Security Layers](#defense-in-depth-pipeline-l0---l5) • [Quickstart](#local-development-quickstart) • [Deployment](#cloud-deployment-guide) • [Default Credentials](#default-credentials)

</div>

---

## Executive Summary

**FedSentinel-X** is an institutional-grade, zero-trust **Security Control Plane for Federated Machine Learning**. Designed for high-assurance environments such as distributed healthcare networks and consortiums, FedSentinel enforces mathematical defense-in-depth against poisoned model updates, Byzantine adversaries, Sybil collusion, and targeted neural backdoors.

In traditional federated learning architectures, central aggregation servers blindly average client model weights (e.g., via standard FedAvg), creating massive vulnerabilities to adversarial model poisoning and data pollution. **FedSentinel replaces blind trust with continuous cryptographic, statistical, and counterfactual attestation.**

---

## Core Security Axioms

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 1. RISK != VERDICT                                                               │
│    Never automatically equate an outlier or anomaly score with maliciousness.    │
│    Benign non-IID demographic shifts must not trigger automated disqualification.│
│                                                                                  │
│ 2. DON'T TRUST THE UPDATE. VERIFY IT.                                            │
│    Every neural weight matrix is untrusted until proven sound across L0-L5 gates.│
│                                                                                  │
│ 3. DATASET != MODEL UPDATE                                                       │
│    Patient EHR/imaging records NEVER leave local hospital enclaves.              │
│    Only serialized parameter gradients and privacy-preserving hashes cross       │
│    the federation boundary.                                                      │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## System Architecture

```text
 ┌───────────────────────────────────────────────────────────────────────────────────┐
 │                            HOSPITAL CLINICAL ENCLAVES                             │
 │  ┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐  │
 │  │      HOSPITAL H01     │  │      HOSPITAL H21     │  │      HOSPITAL H30     │  │
 │  │ ┌───────────────────┐ │  │ ┌───────────────────┐ │  │ ┌───────────────────┐ │  │
 │  │ │ Private Patient   │ │  │ │ Private Patient   │ │  │ │ Remote Linked Rec. │ │  │
 │  │ │ Data (EHR/Imaging)│ │  │ │ Data (EHR/Imaging)│ │  │ │ (HTTP/Local NPZ)   │ │  │
 │  │ └─────────┬─────────┘ │  │ └─────────┬─────────┘ │  │ └─────────┬─────────┘ │  │
 │  │           ▼           │  │           ▼           │  │           ▼           │  │
 │  │   Local CNN Training  │  │   Local CNN Training  │  │   Local CNN Training  │  │
 │  │           ▼           │  │           ▼           │  │           ▼           │  │
 │  │  Param Fingerprinting │  │  Param Fingerprinting │  │  Param Fingerprinting │  │
 │  └───────────┬───────────┘  └───────────┬───────────┘  └───────────┬───────────┘  │
 └──────────────┼──────────────────────────┼──────────────────────────┼──────────────┘
                │                          │                          │
════════════════╪══════════════════════════╪══════════════════════════╪═══════════════
           PRIVACY FIREWALL: No Raw Patient Data Transmitted Across Boundary
════════════════╪══════════════════════════╪══════════════════════════╪═══════════════
                │ (Weight Tensors Only)    │ (Weight Tensors Only)    │
                ▼                          ▼                          ▼
 ┌───────────────────────────────────────────────────────────────────────────────────┐
 │                   FEDSENTINEL-X SECURITY CONTROL PLANE (ADMIN SOC)                │
 │                                                                                   │
 │  [L0: VERIFY]       Artifact Integrity, Finite Floats, Parameter Shape (105,866)  │
 │         ↓                                                                         │
 │  [L1: INSPECT]      128-Dim Deterministic Privacy-Preserving Cosine Fingerprint   │
 │         ↓                                                                         │
 │  [L2: CORRELATE]    Robust Anomaly Detection (Median Baseline + MAD Z-Score > 3.0)│
 │         ↓                                                                         │
 │  [L3: INFLUENCE]    Holdout Validation Trajectory & Gradient Alignment            │
 │         ↓                                                                         │
 │  [L4: SIMULATE]     Counterfactual Inclusion vs. Exclusion ΔAccuracy / ΔLoss      │
 │         ↓                                                                         │
 │  [L5: ATTRIBUTE]    Bayesian Evidence Fusion & Threat Scoring Matrix              │
 │         ↓                                                                         │
 │  [TRUST ENGINE]     Multi-Signal Quarantine / Review / Trust Gate                 │
 │         ↓                                                                         │
 │  [ROBUST AGG.]      Trimmed-Mean / Coordinate-Wise Median / Trust-Weighted Avg    │
 │         ↓                                                                         │
 │  [GLOBAL MODEL]     Cryptographically Signed Global Model Deployment (.safetensors)│
 └───────────────────────────────────────────────────────────────────────────────────┘
```

---

## Defense-in-Depth Pipeline (L0 - L5)

| Layer | Stage | Primary Objective | Mathematical / Algorithmic Mechanism | Action on Failure |
| :--- | :--- | :--- | :--- | :--- |
| **L0** | **VERIFY** | Artifact & Structural Soundness | Finite value check (`isnan`, `isinf`), parameter tensor length verification (105,866 parameters for `FedSentinelCNN`), duplicate payload detection, SHA-256 fingerprint matching | **Immediate Rejection** |
| **L1** | **INSPECT** | Privacy-Safe Representation | 128-dimensional deterministic pseudo-random projection ($seed=42$) creating an immutable low-dimensional representation without exposing raw gradients | **Flag Format Anomaly** |
| **L2** | **CORRELATE**| Robust Outlier Detection | Median Absolute Deviation ($\text{MAD}$) z-score analysis across all cohort participants in round. Robust against up to 50% Byzantine collusion | **Quarantine Update** |
| **L3** | **INFLUENCE**| Global Impact Profiling | Measures directional gradient alignment and holdout validation loss impact of candidate update against consensus trajectory | **Evidence Synthesis** |
| **L4** | **SIMULATE** | Counterfactual Harm Analysis | Calculates differential accuracy $\Delta \text{Acc} = \text{Acc}_{\text{with}} - \text{Acc}_{\text{without}}$ on calibrated held-out benchmarks | **Threat Attribution** |
| **L5** | **ATTRIBUTE**| Multi-Signal Hypothesis | Bayesian fusion: Anomaly ($0.30$), Influence ($0.25$), Counterfactual ($0.30$), Integrity ($0.10$), History ($0.05$) | **Security Hypothesis** |

### Multi-Dimensional Trust Matrix

The autonomous **Trust Engine** synthesizes all five analytical layers into an actionable operational posture:

* **QUARANTINE**: Triggered by $\ge 3$ strong adverse security signals OR any structural integrity failure.
* **SUSPICIOUS**: Triggered by exactly $2$ strong adverse security signals. Held for human analyst review.
* **REVIEW**: Triggered by $1$ warning signal (e.g., severe non-IID benign shift).
* **TRUSTED**: Normal, validated, cohort-conforming gradient update accepted into the global model aggregation.

---

## Platform Features

### 1. Dual Operational Ecosystem
* **Super Admin SOC Control Plane**:
  * Real-time Command Center with global health telemetry, active incidents, and node status.
  * Deep-dive investigative pages for every defense layer (`L0 Verify`, `L1 Inspect`, `L2 Correlate`, `L3 Influence`, `L4 Simulate`, `L5 Attribute`).
  * **Interactive Round Replay**: 10-stage timeline scrubber, live enclave node topology with animated orbital telemetry, Gate Inspector drawer, and real-time execution logs.
  * **Executive Attestation Dossier**: Publication-grade compliance reports with double security borders (`border: 4px double #00e5ff`), cryptographic SHA-256 seal, tripartite signature blocks, and print-ready CSS layout.
* **Hospital Clinical Enclave**:
  * Self-registration on signup page with instant auto-enrollment into active cohorts.
  * Dynamic Dataset Ingestion: Upload local `.npz` files OR link external record URLs/paths (`http://`, `file://`, local disk).
  * Local CNN model training with real PyTorch execution directly on local patient data.
  * Cryptographic parameter signing and update submission with zero raw-data leakage.

### 2. High-Performance ML Engine
* **Model**: `FedSentinelCNN` (Conv2D $\to$ ReLU $\to$ MaxPool $\to$ Conv2D $\to$ Flatten $\to$ FC $\to$ Output).
* **Parameter Count**: Exact 105,866 parameters.
* **Safe Serialization**: Zero-pickle architecture using `.safetensors` and verified `.npz` buffers.
* **Heterogeneous Client Support**: Non-IID Dirichlet distribution ($\alpha = 0.5$) simulation across 20+ healthcare participants.

---

## 100% Free Cloud Deployment Guide

FedSentinel-X is fully configured for deployment on **free-tier cloud infrastructure**:
- **Frontend SPA**: Hosted on [Vercel](https://vercel.com) (Global CDN, 100% Free Tier).
- **Backend API & ML Service**: Hosted on [Render](https://render.com) (Free Web Service).

### Step 1: Deploy Backend to Render (Free)

1. Create a free account at [render.com](https://render.com).
2. Click **New +** $\to$ **Web Service**.
3. Connect your GitHub repository: `https://github.com/Reneshb24/FEDSENTINAL-X`.
4. Render will auto-detect the configuration via `render.yaml`, or configure manually:
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   * **Plan**: `Free`
5. Under **Environment Variables**, add:
   * `PYTHON_VERSION`: `3.11.9`
   * `ENVIRONMENT`: `production`
   * `JWT_SECRET_KEY`: *(Generate a random 32-character hex key)*
   * `CORS_ORIGINS`: `https://fedsentinel-x.vercel.app,http://localhost:5173`
   * `DATABASE_URL`: `sqlite:///./fedsentinel.db`
6. Click **Create Web Service**. Once deployed, copy your backend URL (e.g., `https://fedsentinel-api.onrender.com`).

### Step 2: Deploy Frontend to Vercel (Free)

1. Create a free account at [vercel.com](https://vercel.com).
2. Click **Add New...** $\to$ **Project** and select `FEDSENTINAL-X`.
3. In the project configuration:
   * **Framework Preset**: `Vite`
   * **Root Directory**: `frontend` *(or leave blank; root `vercel.json` will auto-route)*
   * **Build Command**: `npm run build`
   * **Output Directory**: `dist`
4. In **Environment Variables**, add:
   * `VITE_API_BASE_URL`: Your Render backend URL (e.g., `https://fedsentinel-api.onrender.com`)
   * `VITE_FEDERATION_ID`: `413ef0b3-a947-4a02-a652-d963ef14b8da`
5. Click **Deploy**. Your enterprise security portal is live!

---

## Local Development Quickstart

### Prerequisites
* **Python**: 3.11, 3.12, or 3.13
* **Node.js**: v18.0.0+ and `npm`
* **Git**

### 1. Clone Repository
```bash
git clone https://github.com/Reneshb24/FEDSENTINAL-X.git
cd FEDSENTINAL-X
```

### 2. Backend Setup
```bash
# Create and activate Python virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed initial Super Admin and Hospital cohort
python scripts/create_admin.py

# Start FastAPI backend server
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup
```bash
# Open a new terminal in the frontend directory
cd frontend

# Install npm packages
npm install

# Start Vite dev server
npm run dev
```
Open your browser at: `http://127.0.0.1:5173`

---

## Verification & Testing Suite

FedSentinel-X includes a comprehensive suite of unit tests, integration contracts, and end-to-end simulation scripts:

```bash
# Run 84-item pytest test suite
pytest tests/ -v

# Run End-to-End Complete Lifecycle Simulation:
# (Registers H30, links remote dataset, runs Round 10 with 3 clients, aggregates, & finalizes)
python scripts/test_complete_lifecycle.py

# Verify Authentication Matrix
python scripts/test_logins.py

# Verify Hospital Training API
python scripts/test_hospital_api.py
```

---

## Default Credentials

### Super Admin Control Plane
| Role | Email | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@fedsentinel.local` | `Admin123!` | Complete Control Plane, L0-L5 Forensic Gates, Containment Overrides |

### Pre-Configured Hospital Enclaves
| Hospital ID | Facility Name | Email | Password | Node Status |
| :--- | :--- | :--- | :--- | :--- |
| **H21** | Demo Research Hospital | `admin@h21.local` | `Hospital123!` | ACTIVE / ENROLLED |
| **H01** | Demo General Hospital | `admin@demohospital.local` | `Hospital123!` | ACTIVE / ENROLLED |
| **H30** | Apollo Health Network | `admin@apollo.local` | `Hospital123!` | ACTIVE / ENROLLED |

> **Note**: Any healthcare facility can self-register directly via the **Register Hospital** tab on the login screen with instant automated enclave provisioning.

---

## Regulatory & Compliance Attestation

FedSentinel-X is architected to fulfill the strictest healthcare and cybersecurity compliance frameworks:

* **HIPAA Safe Harbor (45 CFR § 164.514)**: Zero patient-level data, identifiers, or EHR records cross the perimeter. Only neural parameter gradients and 128-dimensional deterministic projections are shared.
* **GDPR Article 25 (Data Protection by Design and by Default)**: Client updates are ephemeral and used solely for robust coordinate aggregation.
* **FDA 21 CFR Part 11**: All aggregation rounds, containment actions, trust overrides, and security hypotheses are recorded in an append-only, tamper-evident audit ledger.

---

## Repository Structure

```text
FedSentinel-X/
├── backend/                        # FastAPI High-Performance Backend
│   ├── api/                        # REST & WebSocket API Endpoints
│   │   ├── audit_routes.py         # Forensic Audit Trail Routes
│   │   ├── federation_routes.py    # Federation Cohort & Round Routes
│   │   ├── hospital_dataset_routes.py # Ingestion & Link Import Routes
│   │   ├── hospital_portal_routes.py  # Hospital Enclave Local Training Routes
│   │   ├── hospital_routes.py      # Node Lifecycle Management
│   │   ├── routes.py               # Core Routes Index
│   │   ├── security_routes.py      # L0-L5 Evidence & Investigation Routes
│   │   └── websocket.py            # Live Telemetry Stream
│   ├── auth/                       # JWT, PBKDF2/Argon2 & RBAC Auth Engine
│   ├── core/                       # Configurations, Constants, & Enums
│   ├── schemas/                    # Pydantic Schemas for Strict Typing
│   ├── services/                   # Business Logic & Security Engine
│   │   ├── dataset_service.py      # File & URL Record Ingestion Engine
│   │   ├── federation_service.py   # Multi-Hospital Round Coordination
│   │   ├── hospital_service.py     # Self-Registration & Enclave Provisioning
│   │   ├── hospital_training_service.py # Enclave CNN PyTorch Execution
│   │   ├── round_orchestrator.py   # Multi-Round Orchestration Pipeline
│   │   └── security_pipeline.py    # L0-L5 Analytical Defense Engine
│   └── storage/                    # SQLAlchemy ORM Models & SQLite DB
├── frontend/                       # React 18 + Vite Web Application
│   ├── src/
│   │   ├── assets/                 # SVGs, Branding & Hero Illustrations
│   │   ├── pages/                  # SOC Control Plane Subsystems
│   │   │   ├── AuditTrailPage.jsx  # Tamper-Evident Security Log
│   │   │   ├── GlobalModelPage.jsx # SafeTensors Model Lineage
│   │   │   ├── IncidentsPage.jsx   # Active Threat Containment
│   │   │   ├── L0VerifyPage.jsx    # Structural Integrity Gate
│   │   │   ├── L1InspectPage.jsx   # 128-Dim Privacy Fingerprint Gate
│   │   │   ├── L2CorrelatePage.jsx # Robust MAD Outlier Gate
│   │   │   ├── L3InfluencePage.jsx # Validation Loss Influence Gate
│   │   │   ├── L4SimulatePage.jsx  # Counterfactual Impact Gate
│   │   │   ├── L5AttributePage.jsx # Bayesian Threat Attribution Gate
│   │   │   ├── QuarantinePage.jsx  # Node Isolation & Quarantine Gate
│   │   │   ├── ReportsPage.jsx     # Executive Attestation Dossier
│   │   │   ├── RoundReplayPage.jsx # Visual 10-Stage Scrubber & Inspector
│   │   │   └── SafeAggregationPage.jsx # Robust Byzantine-Safe Aggregator
│   │   ├── App.jsx                 # Super Admin SOC Application Root
│   │   ├── HospitalPortal.jsx      # Clinical Enclave Application Root
│   │   ├── index.css               # Core Styles & Typography
│   │   └── main.jsx                # React DOM Mount Entry
│   └── vercel.json                 # Vercel SPA Routing Configuration
├── scripts/                        # Automation, Seeding & Lifecycle Scripts
│   ├── create_admin.py             # Initial Admin & Cohort Seeder
│   ├── simulate_full_flow.py       # Full Non-IID FL Simulation
│   ├── simulate_hospital_training.py # Local Enclave Trainer
│   ├── test_complete_lifecycle.py  # E2E Complete Round Lifecycle Test
│   ├── test_hospital_api.py        # API Verification Script
│   └── test_logins.py              # Credential & RBAC Verification
├── tests/                          # 84-Item Pytest Verification Suite
│   ├── integration/                # FastAPI & WebSocket Integration Tests
│   └── unit/                       # Schema, Ingestion & Security Tests
├── Dockerfile                      # Container Image for Production Hosting
├── Procfile                        # Cloud Process Definition
├── render.yaml                     # Render Infrastructure as Code (Free Tier)
├── vercel.json                     # Root Vercel SPA Fallback Configuration
├── requirements.txt                # Production Python Dependencies
└── README.md                       # Comprehensive Technical Documentation
```

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
<b>FedSentinel-X — Transforming Federated Machine Learning into a High-Assurance Security Plane</b>
<br>
<sub>Designed with Zero-Trust Principles for Healthcare, Financial, and Defense AI Consortiums.</sub>
</div>
