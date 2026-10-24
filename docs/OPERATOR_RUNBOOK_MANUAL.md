# FEDSENTINEL-X: COMPLETE OPERATOR RUNBOOK & SYSTEM WORKFLOW MANUAL
**Document Version:** 2.4.0  
**Classification:** Enterprise Healthcare AI / Operational Runbook  
**Target Audience:** Super Administrators, SOC Security Engineers, Hospital Clinical IT Officers, Regulatory Auditors  
**Live Production Environments:**  
- **Vercel Frontend:** [https://fedsentinal-x.vercel.app/](https://fedsentinal-x.vercel.app/)  
- **Render Backend API:** [https://fedsentinel-api.onrender.com/](https://fedsentinel-api.onrender.com/)  
- **API Swagger Documentation:** [https://fedsentinel-api.onrender.com/docs](https://fedsentinel-api.onrender.com/docs)  
- **Master Architecture Specification:** [docs/FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md](FEDSENTINEL_COMPREHENSIVE_SYSTEM_REPORT.md)

---

## TABLE OF CONTENTS
1. [Security Foundation & Architecture Model](#1-security-foundation--architecture-model)
2. [Role Boundaries & Portal Access Model](#2-role-boundaries--portal-access-model)
3. [Super Admin SOC Control Plane: Operations from A to Z](#3-super-admin-soc-control-plane-operations-from-a-to-z)
   - 3.1 Authentication & SOC Session Management
   - 3.2 Command Center Telemetry & Network Topology Radar
   - 3.3 Federation Cohort Overview & Hospital Governance
   - 3.4 Orchestrating a Federated Learning Round
   - 3.5 Autonomous 6-Layer Security Engine (L0 to L5)
   - 3.6 Multi-Signal Bayesian Trust Engine & Quarantine Containment
   - 3.7 Interactive 10-Stage Visual Round Replay Forensics
   - 3.8 Append-Only Forensic Audit Trail & Regulatory Ledger
   - 3.9 Executive Attestation Dossier Generation & Export
4. [Hospital Clinical Enclave Portal: Operations from A to Z](#4-hospital-clinical-enclave-portal-operations-from-a-to-z)
   - 4.1 Hospital Self-Registration & Automated Cohort Provisioning
   - 4.2 Enclave Authentication & Credential Management
   - 4.3 Hospital-Local Dataset Management & Isolation Boundary
   - 4.4 Method 1: Uploading Custom Local Datasets (.NPZ)
   - 4.5 Method 2: Ingesting Records via Remote EHR Link / Cloud URL
   - 4.6 Dataset Version Activation & Structural Integrity
   - 4.7 Enclave-Bound PyTorch Model Training Execution
   - 4.8 Cryptographic Checksumming & Privacy-Safe Delta Submission
5. [End-to-End Operational Playbooks & Incident Response](#5-end-to-end-operational-playbooks--incident-response)
   - Playbook Alpha: Standard Federated Training & Global Model Advancement
   - Playbook Bravo: Real-Time Mitigation of a Byzantine Gradient Poisoning Attack
   - Playbook Charlie: Neutralizing a Backdoor Trojan via L3/L4 Simulation
   - Playbook Delta: Hospital Node Onboarding with Isolated EHR Link Ingestion
   - Playbook Echo: Regulatory Compliance Audit & Dossier Extraction
6. [Cloud Deployment, Health Verification & Troubleshooting](#6-cloud-deployment-health-verification--troubleshooting)

---

## 1. SECURITY FOUNDATION & ARCHITECTURE MODEL

FedSentinel-X operates under a strict **Zero-Trust Healthcare Perimeter**:

```
+---------------------------------------------------------------------------------+
|                                 ZERO-TRUST BOUNDARY                             |
|                                                                                 |
|   +------------------------------------+   +--------------------------------+   |
|   |      HOSPITAL CLINICAL ENCLAVE     |   |   SUPER ADMIN SECURITY PLANE   |   |
|   |  - Private Patient Records / EHR   |   |  - Central Model Aggregator    |   |
|   |  - Isolated .NPZ Storage Directory |   |  - 6-Layer Defense Pipeline    |   |
|   |  - Local PyTorch Training Engine   |   |  - Bayesian Trust Engine       |   |
|   |  - Delta Parameter Extraction      |   |  - Forensic Replay Scrubber    |   |
|   +-----------------+------------------+   +----------------+---------------+   |
|                     |                                       ^                   |
|                     |  Zero-Knowledge Weight Delta Only     |                   |
|                     +---------------------------------------+                   |
|                        NO RAW PATIENT DATA EVER TRANSMITTED                     |
+---------------------------------------------------------------------------------+
```

### Core Axioms
1. **Zero-Knowledge Privacy:** Raw clinical data, MRI scans, CT volumes, and electronic health records (EHR) NEVER leave the physical or cloud VPC perimeter of the participating hospital node.
2. **Mathematical Verification:** Central servers accept only mathematical parameter deltas ($\Delta W_i = W_{local} - W_{global}$) serialized via SafeTensors with SHA-256 integrity hashes.
3. **Autonomous Defense-in-Depth:** Every gradient delta must pass through six sequential verification gates (L0 to L5) prior to FedAvg/FedProx aggregation.
4. **Bayesian Node Attribution:** A continuous trust score $T_i \in [0.0, 1.0]$ tracks node behavioral integrity across rounds. Malicious or noisy updates trigger automatic quarantine and exclude the node from the aggregated global model.

---

## 2. ROLE BOUNDARIES & PORTAL ACCESS MODEL

The application provides two completely separated, role-enforced operational portals accessible via clean routing:

| Feature / Capability | Super Admin SOC (`/admin/login` or `/`) | Hospital Clinical Enclave (`/hospital/login`) |
| :--- | :--- | :--- |
| **Primary Route** | `https://fedsentinal-x.vercel.app/admin/login` | `https://fedsentinal-x.vercel.app/hospital/login` |
| **Allowed Roles** | `SUPER_ADMIN`, `ADMIN` | `HOSPITAL_ADMIN`, `HOSPITAL_OPERATOR` |
| **Public Registration** | Closed (Requires system bootstrap seed) | Open (Direct self-service enclave registration) |
| **Dataset Storage** | System Metadata & Global Model Lineage | Private per-hospital enclave directory |
| **Model Operations** | Round initiation, Defense gating, Aggregation | In-situ local PyTorch training on private records |
| **Forensic Tools** | 10-Stage Scrubber, Gate Inspectors, Dossiers | Local accuracy telemetry, update logs |

---

## 3. SUPER ADMIN SOC CONTROL PLANE: OPERATIONS FROM A TO Z

### 3.1 Authentication & SOC Session Management
1. Navigate to `https://fedsentinal-x.vercel.app/admin/login`.
2. Enter the root credentials:
   - **Email:** `admin@fedsentinel.local`
   - **Access Key:** `Admin123!`
   *(Alternatively, click the **Super Admin** quick-fill chip).*
3. Click **ENTER CONTROL PLANE**.
4. The system validates the credentials against the Argon2id hash repository, issues an RS256/HS256 JWT bearer token, and immediately directs you to the Command Center (`/admin`).

### 3.2 Command Center Telemetry & Network Topology Radar
Upon login, the SOC Command Center renders real-time federation health:
- **Topology Radar:** Interactive orbital map displaying active nodes (e.g. H01 through H24). Nodes flagged by threat intelligence glow amber (elevated risk) or red (quarantined).
- **Core Defense Pipeline Banner:** Displays processed updates, accepted safe updates, and quarantined Byzantine submissions.
- **Model Lineage:** Displays the cryptographic progression from Base Model to the latest verified global checkpoint (e.g., `R1 -> R2 -> R3`).
- **Threat Intelligence Panel:** Surfaces real-time hypothesis generation, risk score calculation (0.00 to 100.00), and recommended operational containment actions.

### 3.3 Federation Cohort Overview & Hospital Governance
1. Click **Federation Overview** or **Hospitals** in the left navigation sidebar.
2. Review the registered healthcare institutions:
   - **Institution Code:** Unique identifier (e.g., `H01`, `H21`, `H30`).
   - **Public Key:** Cryptographic identity used for verifying parameter delta digital signatures.
   - **Security Status:** `TRUSTED`, `UNDER_EVALUATION`, `QUARANTINED`, or `REVOKED`.
   - **Cohort Eligibility:** Boolean toggle governing whether the hospital can receive global model weights for the next round.
3. To approve a newly onboarded hospital node:
   - Click the node card -> Click **Approve Node for Cohort Participation**.
   - The status updates immediately to `ACTIVE` and `TRUSTED`.

### 3.4 Orchestrating a Federated Learning Round
1. In the sidebar, select **Round Config**.
2. Configure the orchestration parameters:
   - **Target Aggregation Round:** Number of rounds to execute (e.g. `5`).
   - **Client Quorum Threshold:** Minimum active nodes required to execute aggregation (default: `2`).
   - **Local Learning Rate ($\eta$):** Gradient step size used during local hospital training (default: `0.01`).
   - **Local Epochs:** Number of training epochs per enclave iteration (default: `3`).
   - **Defense Sensitivity:** Toggle between `STRICT` (all 6 gates active), `BALANCED`, and `PERMISSIVE`.
3. Click **Initialize & Open Round Intake**.
4. The round transition state changes from `CONFIGURED` to `IN_PROGRESS`, opening the intake gate for hospital update submissions.

### 3.5 Autonomous 6-Layer Security Engine (L0 to L5)
As hospital updates stream into the control plane, they pass through six inspection layers:
1. **L0 - Structural Verification:**
   - Validates tensor dimensionality against canonical model shape (e.g., Conv2D weight matrices $[32, 1, 3, 3]$).
   - Scans for `NaN`, `Inf`, or unrepresentable floating-point entries.
   - Verifies SHA-256 parameter checksum.
2. **L1 - Statistical Norm Inspection:**
   - Computes Frobenius norm $||\Delta W_i||_F$ and parameter clipping bounds.
   - Detects gradient explosion attacks and sudden weight scaling.
3. **L2 - Spectral Correlation & Divergence:**
   - Measures pairwise cosine similarity and Mahalanobis distance relative to cohort median.
   - Identifies orthogonal or adversarial directional shifts.
4. **L3 - Influence Tracking & Trajectory Drift:**
   - Analyzes historical node update trajectories over previous 3+ rounds.
   - Detects slow-poisoning / stealth sleep-mode attacks.
5. **L4 - Sandboxed Loss Simulation:**
   - Ingests proposed weight updates into an isolated, sterile validation environment.
   - Evaluates performance against reference validation set to detect intentional degradation.
6. **L5 - Bayesian Attribution:**
   - Synthesizes risk scores from L0-L4 using Bayesian belief networks.
   - Produces threat classification (`BENIGN`, `NOISY`, `ADVERSARIAL_LABEL_FLIP`, `BACKDOOR_TRIGGER`).

### 3.6 Multi-Signal Bayesian Trust Engine & Quarantine Containment
- Each hospital node maintains a continuous trust metric $T_i \in [0.0, 1.0]$.
- **Trust Increment:** Consistent submission of clean, verified updates increments trust:
  $$T_i^{(t+1)} = \min(1.0, T_i^{(t)} + \alpha \cdot \text{AcceptanceFactor})$$
- **Trust Penalty:** Gating failures rapidly decay trust:
  $$T_i^{(t+1)} = \max(0.0, T_i^{(t)} \cdot (1 - \beta \cdot \text{RiskScore}))$$
- **Automatic Quarantine:** If $T_i < 0.40$ or an update fails critical gates (L0, L1, or L4), the update is marked `QUARANTINED`, discarded from aggregation, and an incident ticket is generated.
- **Manual Quarantine Override:**
  1. Open **Quarantine Panel** from the sidebar.
  2. Select any suspicious node -> Click **Contain & Quarantine Node**.
  3. Enter the justification reason -> Confirm. The node is blocked from current and future aggregation rounds until re-certified.

### 3.7 Interactive 10-Stage Visual Round Replay Forensics
1. In the sidebar, select **Round Replay**.
2. Select any completed or active federation round (e.g., `Round 1`).
3. Use the **10-Stage Interactive Scrubber** to inspect round execution step-by-step:
   - Stage 1: Round Configuration Broadcast
   - Stage 2: Hospital Client Intake & Quorum Check
   - Stage 3: Ingress Signature Verification
   - Stage 4: L0 Tensor Structural Screening
   - Stage 5: L1 Gradient Norm Verification
   - Stage 6: L2 Cosine Divergence Clustering
   - Stage 7: L3 Historical Influence Evaluation
   - Stage 8: L4 Sandboxed Loss Simulation
   - Stage 9: L5 Bayesian Risk Synthesis & Quarantine Action
   - Stage 10: FedAvg Aggregation & Global Model Lineage Commit
4. Review the gate inspector cards at each stage to observe exact mathematical metrics, outlier distances, and forensic proof.

### 3.8 Append-Only Forensic Audit Trail & Regulatory Ledger
1. In the sidebar, select **Audit Trail**.
2. Inspect the immutable log of operational events:
   - Each event contains an ISO timestamp, actor identity, action code (e.g. `ROUND_INITIALIZED`, `UPDATE_QUARANTINED`, `TRUST_DECAYED`), IP hash, and cryptographic hash chain link.
   - Filter events by severity (`INFO`, `WARNING`, `SECURITY_ALERT`, `CRITICAL`).
   - Export audit records for compliance records.

### 3.9 Executive Attestation Dossier Generation & Export
1. In the sidebar, select **Executive Reports**.
2. Choose the completed round for audit certification.
3. Review the generated publication-grade dossier:
   - Formal Compliance Statement (HIPAA Privacy Rule §164.514, EU AI Act High-Risk AI System conformity, FDA Artificial Intelligence/Machine Learning Action Plan).
   - Global Model Convergence Graphs (Training loss curve vs. Validation accuracy).
   - Node Participation Matrix & Quarantined Adversary Breakdown.
   - SHA-256 Model Checksum Attestation.
4. Click **Print / Export PDF** to generate an official cryptographic certificate.

---

## 4. HOSPITAL CLINICAL ENCLAVE PORTAL: OPERATIONS FROM A TO Z

### 4.1 Hospital Self-Registration & Automated Cohort Provisioning
1. Navigate to `https://fedsentinal-x.vercel.app/hospital/login`.
2. Click **Register new hospital** at the bottom of the card.
3. Fill in the institutional registration form:
   - **Hospital Code:** Unique short identifier (e.g., `H40`, `MAYO-01`, `KIMS-PEDS`).
   - **Hospital Name:** Full legal institution name (e.g., *Metropolitan Medical Research Center*).
   - **Contact Email:** Official department contact (e.g., `ai-ops@hospital.org`).
   - **Location:** Geographic facility identifier (e.g., `Boston, USA`).
   - **Hospital Admin Email:** Account for portal authentication (e.g., `admin@metrohealth.org`).
   - **Password:** Minimum 8 characters.
4. Click **REGISTER & ENTER PORTAL**.
5. The system performs instant enclave provisioning:
   - Registers the hospital entity in the database.
   - Creates the administrative credentials.
   - Enrolls the institution in the active federation cohort.
   - Provisions an isolated private dataset storage enclave directory (`data/hospital_datasets/{hospital_id}/`).
   - Immediately signs the user in and loads the Hospital Portal.

### 4.2 Enclave Authentication & Credential Management
1. To sign into an existing hospital enclave:
   - Navigate to `https://fedsentinal-x.vercel.app/hospital/login`.
   - Enter your hospital administrator email and password.
   *(Demo credentials: click **H21 Demo**, **H01 General**, or **H30 Apollo** quick-fill buttons).*
2. Click **ENTER HOSPITAL PORTAL**.
3. You are directed to your enclave dashboard (`/hospital`).

### 4.3 Hospital-Local Dataset Management & Isolation Boundary
FedSentinel-X enforces physical and logical dataset boundary isolation:
- Datasets created by Hospital A are stored exclusively under `data/hospital_datasets/{hospital_A_id}/`.
- Hospital B CANNOT view, list, read, or train against Hospital A's datasets.
- Each hospital has complete autonomy over their data formats, revisions, and annotations.

### 4.4 Method 1: Uploading Custom Local Datasets (.NPZ)
Hospitals can upload proprietary clinical datasets directly from their workstation:
1. In the hospital portal navigation, click **Datasets**.
2. Click **CREATE DATASET**.
   - **Dataset Name:** Enter a clinical label (e.g., `Chest_XRay_Pneumonia_2026`).
   - **Dataset Type:** Select `IMAGE_CLASSIFICATION` or `TABULAR_EHR`.
   - **Expected Classes:** Default `10` (compatible with CNN global model).
   - Click **Create Dataset**.
3. In the Datasets list, click on your newly created dataset row to open **Version Management**.
4. Select the **UPLOAD FILE (.NPZ)** tab.
5. Enter the Version tag (e.g., `v1-clean`).
6. Click **Choose File** and select your local `.npz` file.
   > **Dataset File Structure Specification:**
   > The uploaded `.npz` archive must contain two compressed arrays:
   > - `images`: Float32 array of shape $[N, 1, 28, 28]$ (normalized between $0.0$ and $1.0$).
   > - `labels`: Int64 array of shape $[N]$ with class indices between $0$ and $9$.
7. Click **UPLOAD & VALIDATE**.
8. The server performs real-time validation:
   - Computes SHA-256 binary hash.
   - Verifies tensor shapes and label bounds.
   - Stores the verified artifact securely in the hospital enclave.
   - Displays success message and sample count.

### 4.5 Method 2: Ingesting Records via Remote EHR Link / Cloud URL
For enterprise environments where datasets are stored in internal hospital S3/GCS buckets, PACS imaging servers, or hospital filesystem paths:
1. In the dataset **Version Management** view, select **LINK RECORD URL / PATH**.
2. Enter the Version tag (e.g., `v2-ehr-stream`).
3. Enter the **Record Link / Path / URL**:
   - Supported schemes:
     - `https://intranet.hospital.org/pacs/cohort_2026.npz`
     - `s3://internal-clinical-bucket/imaging/brain_mri.npz`
     - Local filesystem path: `/mnt/secure_ehr/radiology/october_batch.npz`
4. Select Format: `AUTO`, `NPZ_STREAM`, or `EHR_RECORD_INDEX`.
5. Click **INGEST & REGISTER RECORD LINK**.
6. The enclave ingests the record data, validates tensor structural constraints, calculates the cryptographic fingerprint, and stores the artifact within the hospital boundary.

### 4.6 Dataset Version Activation & Structural Integrity
- A hospital can maintain multiple versions (e.g. `v1-raw`, `v2-augmented`, `v3-expert-reviewed`).
- Click **Activate** on the target version. Only active, verified dataset versions can be selected during local PyTorch training.

### 4.7 Enclave-Bound PyTorch Model Training Execution
1. In the hospital portal sidebar, click **Local Training**.
2. Review the active federation configuration:
   - **Global Model Version:** The current certified model weights retrieved from the control plane (e.g., `R1-FedAvg-Global`).
   - **Quorum Status:** Active round ID.
3. Select your training parameters:
   - **Dataset:** Choose your custom uploaded or linked dataset (e.g., `Chest_XRay_Pneumonia_2026`).
   - **Dataset Version:** Choose your verified version (e.g., `v1-clean`).
4. Click **EXECUTE LOCAL ENCLAVE TRAINING**.
5. The enclave executes PyTorch training:
   - Initializes model with latest global weights.
   - Runs local SGD optimization over the selected dataset for the specified epochs.
   - Computes local training loss, validation accuracy, and gradient deltas.
   - Displays real-time training telemetry.

### 4.8 Cryptographic Checksumming & Privacy-Safe Delta Submission
1. Upon training completion, the enclave calculates the parameter update:
   $$\Delta W_i = W_i^{(local)} - W^{(global)}$$
2. Serializes the delta into SafeTensors format.
3. Generates a cryptographic SHA-256 fingerprint:
   $$\text{Fingerprint} = \text{SHA256}(\text{SafeTensorsBytes})$$
4. Click **SUBMIT WEIGHT DELTA TO FEDERATION**.
5. The weight delta and cryptographic attestation are dispatched to the central control plane.
   > **Privacy Guarantee:** The raw training images and patient labels NEVER leave the hospital. Only the mathematical delta vector is transmitted.

---

## 5. END-TO-END OPERATIONAL PLAYBOOKS & INCIDENT RESPONSE

### Playbook Alpha: Standard Federated Training & Global Model Advancement
1. **Admin:** Authenticates to `/admin/login` -> Opens **Round Config** -> Sets Target Round `1` -> Clicks **Initialize & Open Round Intake**.
2. **Hospital H01:** Signs into `/hospital/login` -> Navigates to **Local Training** -> Selects active dataset -> Clicks **Execute Local Training** -> Clicks **Submit Weight Delta**.
3. **Hospital H21:** Signs into `/hospital/login` -> Navigates to **Local Training** -> Selects active dataset -> Clicks **Execute Local Training** -> Clicks **Submit Weight Delta**.
4. **Admin:** Navigates to **Live Round** -> Observes both submissions pass L0 through L5 gates -> Status shows `SAFE_FOR_AGGREGATION`.
5. **Admin:** Clicks **Execute Safe Aggregation (FedAvg)**.
6. **Result:** Global model increments to `R2`, global model lineage is updated, and an immutable audit record is committed.

### Playbook Bravo: Real-Time Mitigation of a Byzantine Gradient Poisoning Attack
1. **Adversary (Compromised Node):** Submits scaled/flipped gradient deltas designed to steer the global classifier away from convergence.
2. **Autonomous Defense Execution:**
   - **L0:** Update passes structural shape validation.
   - **L1:** Frobenius norm $||\Delta W||_F = 84.2$ exceeds threshold $\theta_{norm} = 25.0$. Gate trips: `L1_NORM_OUTLIER`.
   - **L2:** Cosine similarity with cohort median evaluates to $-0.73$. Gate trips: `L2_SPECTRAL_INVERSION`.
   - **L5:** Bayesian risk score calculated at $96.8 / 100$. Classification: `ADVERSARIAL_POISONING`.
3. **Automatic Containment:**
   - Update is automatically placed in `QUARANTINED` status.
   - Node trust score $T_i$ decays from $0.92 \to 0.15$.
   - The rogue update is excluded from FedAvg aggregation.
4. **Admin Investigation:**
   - Admin opens **Incidents Panel** -> Inspects Incident `#INC-BYZ-POISON`.
   - Confirms threat hypothesis -> Clicks **Acknowledge & Confirm Quarantine**.

### Playbook Charlie: Neutralizing a Backdoor Trojan via L3/L4 Simulation
1. **Adversary (Trojaned Node):** Submits stealth update with normal norm ($||\Delta W||_F = 8.1$) that injects a backdoor trigger for class 7.
2. **Autonomous Defense Execution:**
   - **L1/L2:** Passes norm and cosine checks due to stealth scaling.
   - **L3:** Trajectory analysis detects unusual parameter divergence in final dense layers.
   - **L4:** Sandboxed loss simulation executes reference classification; accuracy on reference test set drops by $14.2\%$.
   - Gate trips: `L4_LOSS_DEGRADATION`.
3. **Automatic Containment:** Update is quarantined; the global model is protected from backdoor contamination.

### Playbook Delta: Hospital Node Onboarding with Isolated EHR Link Ingestion
1. **Clinic IT Officer:** Visits `https://fedsentinal-x.vercel.app/hospital/login`.
2. Clicks **Register new hospital** -> Enters Code `H55`, Name `St. Jude Clinical Lab`, Admin credentials -> Submits.
3. Once in portal -> Visits **Datasets** -> Clicks **CREATE DATASET** (`Pediatric_Oncology_2026`).
4. In Version Management -> Selects **LINK RECORD URL / PATH**.
5. Enters intranet URL: `https://clinical-archive.stjude.org/data/batch_01.npz` -> Clicks **Ingest & Register**.
6. The enclave ingests the record, validates dimensions, and computes SHA-256 checksum.
7. Clinic executes local training on this isolated dataset and submits delta to Federation.

### Playbook Echo: Regulatory Compliance Audit & Dossier Extraction
1. **Auditor / CMIO:** Requires documentation for HIPAA / FDA audit.
2. **Admin:** Authenticates to `/admin/login` -> Navigates to **Audit Trail** -> Exports signed event log.
3. **Admin:** Navigates to **Executive Reports** -> Selects latest validated round -> Reviews mathematical convergence proofs, gate rejection statistics, and SHA-256 model checksum.
4. Clicks **Print / Export PDF Dossier** -> Delivers cryptographically signed compliance document.

---

## 6. CLOUD DEPLOYMENT, HEALTH VERIFICATION & TROUBLESHOOTING

### 6.1 Live Production Endpoints
- **Frontend (Vercel):** `https://fedsentinal-x.vercel.app/`
- **Backend API (Render):** `https://fedsentinel-api.onrender.com/`
- **API Health Endpoint:** `https://fedsentinel-api.onrender.com/api/v1/health`
- **Interactive Swagger:** `https://fedsentinel-api.onrender.com/docs`

### 6.2 Render Free-Tier Cold-Start Handling
- Render's free tier places backend containers into deep sleep after 15 minutes of inactivity.
- On the first request, Render spins up the container within 30 to 45 seconds.
- The frontend includes built-in retry logic and connection indicators to inform the operator while the backend warms up.
- To wake up the backend manually before a demonstration:
  ```powershell
  curl https://fedsentinel-api.onrender.com/
  ```

### 6.3 Automated Database Seeding & Recovery
- Git does not persist local `.db` SQLite files to public repositories for security.
- On Render startup, `backend/storage/seed.py` automatically checks for the existence of `admin@fedsentinel.local` and initial cohort nodes (`H01`, `H21`, `H30`, `H02`–`H20`).
- If missing, the database automatically self-seeds with default credentials and active federation models.
- If credentials ever fail, the `/api/auth/login` endpoint includes a fallback auto-seeder that initializes missing accounts before authentication.

### 6.4 Troubleshooting Common Issues
| Issue | Root Cause | Resolution |
| :--- | :--- | :--- |
| **Blank screen after login** | Missing React component definitions in JSX tree | Verify `Sidebar`, `Pipeline`, `HospitalTopology`, `IncidentPanel`, `ModelLineage` are defined in `App.jsx`. Run `npm run build`. |
| **401 Unauthorized on login** | Fresh Render container without seeded admin | Ensure `seed_default_data()` ran. The login route now automatically auto-seeds if admin is missing. |
| **Failed to fetch / Network error** | Render cold start or API URL trailing slash mismatch | Verify base URL has trailing slashes stripped (`rawApi.replace(/\/+$/, '')`). Allow 40s for Render spin-up. |
| **Dataset Upload: 422 Unprocessable Entity** | `.npz` archive does not contain `images` or `labels` keys | Verify `.npz` format contains `images` (float32 $[N, 1, 28, 28]$) and `labels` (int64 $[N]$). |
| **Unknown character / broken symbol** | Raw non-ASCII character or 4-byte emoji in source | Replace with standard HTML entities (`&larr;`, `&rarr;`) or plain ASCII text. |

---
**Document Maintained by:** FedSentinel-X Engineering & Cybersecurity Team  
**Master Repository:** [https://github.com/Reneshb24/FEDSENTINAL-X](https://github.com/Reneshb24/FEDSENTINAL-X)
