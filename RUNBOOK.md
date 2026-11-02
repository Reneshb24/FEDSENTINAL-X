# FEDSENTINEL-X — MASTER OPERATOR RUNBOOK & BUTTON-BY-BUTTON SPECIFICATION MANUAL
## Complete Operational Guide for Global Administrator Security Control Plane & Hospital Clinical Enclave Portals

---

## 1. Executive Architecture & Core Security Axioms

FedSentinel-X is an enterprise-grade cybersecurity control plane and distributed cluster operations platform engineered for **Federated Machine Learning (FL)** within healthcare AI consortiums. The platform bridges mathematical zero-trust security with clinical operational workflows, strictly isolating raw patient health records (EHR, DICOM radiology, laboratory values) inside on-premise hospital enclaves while coordinating global diagnostic consensus models.

### Core Security Axioms
1. **`RISK != VERDICT`**: An algorithmic or statistical anomaly score represents forensic evidence for evaluation, never an automatic conviction. Non-IID variance from specialized clinics (e.g., pediatric pathology or tertiary oncology) is systematically distinguished from malicious poisoning.
2. **`DON'T TRUST THE UPDATE. VERIFY IT.`**: Every incoming candidate model update is treated as untrusted and potentially adversarial until cryptographically verified across the 6-layer defense pipeline (L0 through L5).
3. **`DATASET != MODEL UPDATE`**: Raw clinical data **never** leaves the local hospital perimeter. Enclave training computes local weight adjustments ($\Delta W$), packages them into zero-pickle `.safetensors` files, and dispatches only encrypted differential parameter tensors.

---

## 2. Environment Setup, Daemons & Credentials Reference

### 2.1 Starting Local Development Daemons

| Component | Technology | Default Port | Health Probe | Start Command |
| :--- | :--- | :--- | :--- | :--- |
| **API Backend Server** | FastAPI / Uvicorn | `8000` | `http://127.0.0.1:8000/api/v1/health` | `uvicorn backend.main:app --host 127.0.0.1 --port 8000` |
| **Frontend UI Client** | Vite / React 19 | `5173` | `http://localhost:5173` | `npm --prefix frontend run dev` |

### 2.2 Verified Access Accounts & Credentials

| Persona / Scope | Portal URL | Username / Email | Default Password | Role Authority |
| :--- | :--- | :--- | :--- | :--- |
| **Global Super Administrator** | `http://localhost:5173/admin/login` | `admin@fedsentinel.local` | `Admin123!` | Platform Super Admin (Full SOC & Federation Authority) |
| **Hospital Enclave Admin (H21)** | `http://localhost:5173/hospital/login` | `admin@h21.local` | `Hospital123!` | Enclave Administrator (Stanford Clinical AI Enclave) |
| **Hospital Enclave Admin (H01)** | `http://localhost:5173/hospital/login` | `admin@demohospital.local` | `Hospital123!` | Enclave Administrator (General Medical Center Enclave) |

---

## 3. Authentication & Account Lifecycle (Button-by-Button)

### 3.1 Global Administrator Login (`/admin/login`)

```
+-------------------------------------------------------+
|  FEDSENTINEL-X :: SECURITY CONTROL PLANE LOGIN         |
|  [ Email Address Input ]                              |
|  [ Password Input ] [Show/Hide Password Toggle]       |
|  [ ENTER SECURITY CONTROL PLANE (Button) ]            |
|  Switch to Hospital Enclave Portal (Link)             |
+-------------------------------------------------------+
```

* **`Email Address` field**: Enter administrator email (e.g. `admin@fedsentinel.local`). Validated with regex format.
* **`Password` field**: Enter administrator password (e.g. `Admin123!`). Argon2id hash verified server-side.
* **`Eye / EyeOff` toggle button**: Reveals or obscures entered password text.
* **`ENTER SECURITY CONTROL PLANE` button**: Submits credentials via `POST /api/v1/auth/login`. On HTTP 200, saves 256-bit JWT token to `localStorage.fedsentinel_token` and redirects to `/`. On failure, displays red alert badge with exact backend rejection detail.
* **`Switch to Hospital Enclave Portal` link**: Toggles view directly to `/hospital/login` without losing navigation state.

---

### 3.2 Hospital Clinical Enclave Self-Registration (`/hospital/login` $\to$ Registration Form)

```
+-------------------------------------------------------+
|  INSTITUTIONAL ENCLAVE ONBOARDING APPLICATION          |
|  Hospital Name:        [ Mayo Clinic AI Enclave      ] |
|  Enclave Code:         [ H25                         ] |
|  Country:              [ United States               ] |
|  City / State:         [ Rochester, MN               ] |
|  Official Email:       [ ai-director@mayo.org        ] |
|  Contact Phone:        [ +1 (507) 284-2511           ] |
|  Official Website:     [ https://www.mayoclinic.org  ] |
|  Clinical Focus:       [ Oncology & Radiology AI     ] |
|  Admin Contact Name:   [ Dr. Sarah Lin               ] |
|  Admin Password:       [ ********                    ] |
|  Confirm Password:     [ ********                    ] |
|  [ SUBMIT INSTITUTIONAL APPLICATION (Button) ]        |
|  [ Cancel & Back to Login (Button) ]                  |
+-------------------------------------------------------+
```

* **`Hospital Name` input**: Legal institutional name of the healthcare organization.
* **`Enclave Code` input**: 3 to 6 character alphanumeric enclave callsign (e.g. `H25`, `JHU01`).
* **`Country` input**: Sovereign jurisdiction of the hospital facility (for regulatory attestation compliance).
* **`City / State` input**: Physical geographic coordinates / municipal location of the primary datacenter enclave.
* **`Official Email` input**: Verified administrative domain contact email.
* **`Contact Phone` input**: Institutional emergency contact phone number.
* **`Official Website` input**: Organization URL.
* **`Clinical Focus` input**: Medical specialization description (e.g., Pneumology, MedMNIST, Neuro-imaging).
* **`Admin Contact Name` input**: Designated Enclave Security Officer name.
* **`Admin Password` & `Confirm Password` inputs**: Enclave account password (minimum 8 characters).
* **`SUBMIT INSTITUTIONAL APPLICATION` button**: Dispatches `POST /api/v1/auth/register-hospital`. Creates hospital entry in `SUBMITTED / PENDING` status. Logs audit event and transitions user to the Pending Institutional Review view.
* **`Cancel & Back to Login` button**: Discards input form and returns to Hospital Enclave login screen.

---

### 3.3 Unapproved Institutional Enclave Status View

When an institution registers, it is placed in cryptographic isolation until approved by a Super Administrator.

* **Application Status Banner**: Visual status badge (`SUBMITTED`, `UNDER_REVIEW`, or `REJECTED`).
* **`REFRESH APPLICATION STATUS` button**: Queries `GET /api/v1/hospital/status` to check whether the control plane has approved the application.
* **`EDIT SUBMITTED CONTACT INFO` button**: Opens modal allowing updates to contact phone, email, and description before formal review.
* **`SIGN OUT` button**: Clears temporary enclave token and returns to login.

---

### 3.4 Logout Operation (Both Portals)

* **`LOGOUT` button (Header Top-Right)**:
  1. Issues `POST /api/v1/auth/logout` to revoke current JWT session on the server.
  2. Purges `fedsentinel_token`, `fedsentinel_hospital_id`, and active telemetry subscriptions from browser `localStorage`.
  3. Closes any open WebSocket streams (`/ws/events`).
  4. Redirects to `/admin/login` or `/hospital/login`.

---

## 4. Global Administrator Security Control Plane (Every Feature & Button)

```
========================================================================================
ADMIN NAVIGATION GROUPS:
[COMMAND]       Command Center (/)
[FEDERATION]    Overview (/overview) | Registration Requests (/requests) |
                Hospital Control Center (/hospitals) | Federation Cohort (/cohort) |
                Synthetic Lab & Sandbox (/lab)
[SECURITY]      Round Configuration (/rounds/configure) | Live Round (/rounds/live) |
                Update Intake (/intake)
[ANALYSIS]      L0 Verify (/layers/l0-verify) | L1 Inspect (/layers/l1-inspect) |
                L2 Correlate (/layers/l2-correlate) | Quarantine (/quarantine) |
                L3 Influence (/layers/l3-influence) | L4 Simulate (/layers/l4-simulate) |
                L5 Attribute (/layers/l5-attribute)
[DECISION]      Trust Engine (/trust) | Incidents (/incidents) | Human Overrides (/overrides)
[MODEL]         Safe Aggregation (/aggregation) | Global Model (/model) |
                Model Lineage (/lineage)
[FORENSICS]     Audit Trail (/audit) | Round Replay (/replay) | Reports (/reports)
========================================================================================
```

---

### 4.1 Command Center (`/` or `command`)

The SOC mission control room providing a comprehensive real-time situational assessment of the entire federated network.

* **Header Controls**:
  * **System Posture Indicator**: Real-time badge (`OPTIMAL`, `ELEVATED RISK`, or `CRITICAL DEFENSE`).
  * **`3D VIEW` / `2D VIEW` toggle buttons**: Switches between the interactive 3D Defense Shield canvas (`DefenseShield3D`) and a compact 2D metric grid.
  * **`REFRESH TELEMETRY` button**: Triggers instant synchronization of platform telemetry from `/api/v1/dashboard/stats`.
* **Interactive 3D Defense Shield Canvas (`DefenseShield3D`)**:
  * Multi-layer reactive 3D sphere with orbital particle rings representing active hospitals.
  * Green particles: Trusted hospitals with passing health pings.
  * Amber particles: Hospitals under probation or elevated anomaly scores.
  * Red particles: Quarantined hospitals or active incident targets.
  * **Hover over node**: Displays HTML HUD tooltip showing Hospital Code, Current Round Delta Norm, and Latency.
* **Executive Metric Cards**:
  * *Federation Rounds*: Total rounds completed, current round status (`RUNNING` / `IDLE`).
  * *Enrolled Hospitals*: Active participants vs total registered. Click opens `/hospitals`.
  * *Anomaly Index*: Running MAD z-score across candidate submissions.
  * *Quarantine Vault*: Total updates sequestered in quarantine. Click opens `/quarantine`.
  * *Global Model Accuracy*: Top-1 validation accuracy against consensus benchmark dataset.
* **Active Threat & Incident Panel**:
  * Real-time list of detected security incidents with severity tags (`CRITICAL`, `HIGH`, `MEDIUM`).
  * **`VIEW INCIDENT DETAILS` button**: Jumps directly to `/incidents` filtered to that incident ID.
* **Quick Action Buttons**:
  * **`NEW FEDERATION ROUND` button**: Navigates directly to `/rounds/configure`.
  * **`OPEN QUARANTINE VAULT` button**: Navigates directly to `/quarantine`.
  * **`AUDIT LEDGER` button**: Navigates directly to `/audit`.

---

### 4.2 Federation Overview (`/overview`)

Visualizes global consortium topology, geographic cluster distribution, and institutional tiering.

* **`3D ORBIT` / `2D MATRIX` toggle buttons**: Switches between `FederationOrbit3D` visualizer and tabular cluster view.
* **3D Orbital Manifold (`FederationOrbit3D`)**:
  * Visualizes concentric orbital rings based on security posture:
    * Inner Core Orbit: Tier 1 Trusted institutions ($T_i \ge 0.85$).
    * Middle Orbit: Tier 2 Probation institutions ($0.50 \le T_i < 0.85$).
    * Outer Orbit: Tier 3 Quarantined or New institutions ($T_i < 0.50$).
  * Interactive click on any node selects that institution and opens the **Node Telemetry Drawer**.
* **Node Telemetry Drawer**:
  * Displays: Institutional legal name, contact email, network endpoint, trust score progress bar, and accepted update count.
  * **`INSPECT HOSPITAL DOSSIER` button**: Navigates to `/hospitals` with this node focused.
  * **`CLOSE DRAWER (X)` button**: Dismisses node inspection drawer.
* **Consortium Filtering Controls**:
  * **Search Input**: Filters institutions by name or code.
  * **Tier Filter Dropdown**: `All Tiers`, `Tier 1 (Trusted)`, `Tier 2 (Probation)`, `Tier 3 (Quarantine)`.

---

### 4.3 Registration Requests (`/requests`)

The gatekeeper workflow for vetting incoming healthcare facility applications before admission to the training cluster.

* **Tab Filters**:
  * **`PENDING` tab**: Applications awaiting initial administrative triage.
  * **`UNDER REVIEW` tab**: Applications currently assigned to a security auditor.
  * **`APPROVED` tab**: Successfully enrolled and active member facilities.
  * **`REJECTED` tab**: Denied applications with documented reasons.
* **Application Card / Row**:
  * Displays: Legal Hospital Name, Enclave Code, Location, Contact Email, Clinical Specialization, Submission Date.
  * **`REVIEW APPLICATION` button**: Transitions status from `PENDING` to `UNDER_REVIEW`. Logs administrative review timestamp.
  * **`APPROVE & ONBOARD` button**:
    1. Validates institution records.
    2. Enrolls institution into the active federation cohort (`status = ACTIVE`).
    3. Generates cryptographic enclave access credentials.
    4. Records immutable entry in platform audit ledger.
  * **`REJECT WITH REASON` button**:
    * Opens modal with mandatory **Rejection Justification** textarea.
    * **`CONFIRM REJECTION` button**: Records denial reason and sets status to `REJECTED`.
    * **`CANCEL` button**: Closes modal without rejecting.

---

### 4.4 Hospital Control Center (`/hospitals`)

Consolidated command desk for the entire fleet of healthcare enclaves.

* **Top Summary Metric Cards**:
  * *Total Enclaves*: Total registered facilities.
  * *Active Enclaves*: Facilities eligible for round training.
  * *Quarantined Enclaves*: Facilities temporarily blocked from training.
  * *Consensus Trust Mean*: Average Bayesian reputation score across all nodes.
* **3D Hospital Topology Radar (`HospitalNetwork3D`)**:
  * R3F mesh rendering active hospital nodes with dynamic ping rings and status beams.
  * Click on 3D node triggers card selection in the grid below.
* **Filter & Search Bar**:
  * **Search input (`Search by name or code...`)**: Real-time filtering.
  * **Status Filter dropdown**: `All Statuses`, `ACTIVE`, `PENDING`, `SUSPENDED`, `QUARANTINED`.
  * **Security Tier dropdown**: `All Tiers`, `TRUSTED`, `PROBATION`, `HIGH_RISK`.
* **Hospital Enclave Cards Grid**:
  * Displays: Enclave Code badge, Institution Name, Trust Score bar ($0.00 - 1.00$), Active Datasets count, Last Round Participation status.
  * **`ChevronRight` Card Click / Inspect button**: Opens the **Enclave Management Drawer**.
* **Enclave Management Drawer (Slide-out Panel)**:
  * Comprehensive institutional dossier (Endpoint, join date, contact info, recent updates).
  * **Action Controls**:
    * **`ACTIVATE / APPROVE` button**: Activates pending or restored enclaves.
    * **`SUSPEND ENCLAVE` button**: Temporarily halts round participation. Prompts for reason.
    * **`QUARANTINE ENCLAVE` button**: Immediately blocks updates from consensus aggregation.
    * **`RELEASE FROM QUARANTINE` button**: Restores quarantined enclave back to active standing.
    * **`REVOKE CREDENTIALS` button**: High-risk permanent credential invalidation (prompts for double-confirmation).
    * **`CLOSE DRAWER (X)` button**: Closes drawer.

---

### 4.5 Federation Cohort (`/cohort` or `federation-membership`)

Controls cohort grouping, eligibility gating, and round inclusion rosters.

* **Cohort Configuration Panel**:
  * **Minimum Participant Quorum input**: Sets required client threshold (default: 2).
  * **Maximum Round Capacity input**: Upper bound of concurrent training enclaves.
* **Hospital Cohort Table**:
  * Columns: Hospital Name, Code, Security Tier, Trust Score, Eligibility Status, Round Inclusion Toggle.
  * **`INCLUDE IN NEXT ROUND` switch / toggle**: Toggles participation flag for the upcoming round.
  * **`SELECT ALL ELIGIBLE` button**: Selects all verified active hospitals.
  * **`DESELECT ALL` button**: Clears all participant selections.

---

### 4.6 Synthetic Lab & Attack Sandbox (`/lab` or `synthetic`)

An isolated testing laboratory designed for running stress tests and adversarial simulation experiments without impacting production clinical enclaves.

* **3D Synthetic Distribution Manifold (`SyntheticLab3D`)**:
  * Visualizes synthetic client nodes, distribution curves, and class partitions in 3D space.
* **Scenario Presets**:
  * **`Clean IID` button**: Uniform Gaussian class distribution across all synthetic nodes.
  * **`Non-IID Dirichlet` button**: Synthesizes statistical distribution skew ($\alpha$ controlled).
  * **`Extreme Label Skew` button**: Pathological partition where clients only hold 1 or 2 specific classes.
  * **`Backdoor Trigger` button**: Injects a synthetic pixel trigger pattern into designated client updates.
  * **`Sybil Replacement` button**: Simulates a coordinated multi-agent model replacement attack (+25.0 scale).
* **Interactive Parameter Controls**:
  * **Client Count slider / input**: Select 2 to 20 synthetic simulation nodes.
  * **Dirichlet Concentration ($\alpha$) slider**: Range `0.05` (extreme non-IID) to `10.0` (nearly IID).
  * **Poison Ratio slider**: Fraction of training samples containing adversarial triggers (0% to 100%).
  * **Target Label selector**: Class index targeted by backdoor attack (0 through 9).
* **Action Buttons**:
  * **`GENERATE SYNTHETIC COHORT` button**: Synthesizes data shards and generates client data distributions.
  * **`RUN DEFENSE BENCHMARK SIMULATION` button**: Executes candidate updates through L0–L5 defense gates and reports detection accuracy.
  * **`RESET LAB PARAMETERS` button**: Restores default simulation configuration.

---

### 4.7 Round Configuration (`/rounds/configure` or `round-config`)

The operational control desk for launching federated training rounds.

* **Execution Mode Selector**:
  * **`SIMULATION MODE` button (Amber Theme)**:
    * Uses isolated synthetic clients.
    * Enables adversarial attack injection controls (Backdoor, Scaling, Sign-flip).
    * Safe for security experimentation and automated regression runs.
  * **`HOSPITAL MODE` button (Cyan Theme)**:
    * Coordinates authenticated, approved clinical enclaves.
    * Attack injection controls are strictly disabled.
    * Requires enrolled hospital enclaves to execute PyTorch training locally.
* **Participant Selection Controls**:
  * **Client Count slider**: Select participant count between 2 and maximum available enclaves.
  * **Preset buttons (`3 Clients`, `5 Clients`, `10 Clients`, `All Available`)**: Instantly snaps slider to preset values.
  * **Enclave Selection Checkboxes (Hospital Mode)**: Allows cherry-picking specific healthcare institutions.
* **Hyperparameter Configuration Inputs**:
  * **Local Epochs input**: Number of local PyTorch epochs per enclave (default: `1`, range: 1–10).
  * **Batch Size dropdown**: `16`, `32`, `64`, `128` samples per training batch.
  * **Learning Rate input**: Local optimizer learning rate (e.g., `0.001`).
  * **Optimizer dropdown**: `SGD`, `Adam`.
  * **Aggregation Strategy dropdown**: `FedAvg (Standard)`, `Coordinate Median (Robust Byzantine)`, `Trimmed Mean (Robust Outlier)`.
* **Adversarial Injection Controls (Simulation Mode Only)**:
  * **Attack Type dropdown**: `None`, `Model Replacement (+25.0x)`, `Sign-Flipping`, `Gaussian Noise Injection`, `Backdoor Trigger`.
  * **Attacking Nodes count input**: Number of compromised clients (e.g., 1 or 2).
  * **Attack Magnitude scalar input**: Adversarial scaling factor (default: `25.0`).
* **Execution Action Buttons**:
  * **`CREATE NEW FEDERATION ROUND` button**: Dispatches `POST /api/v1/federations/{id}/rounds`. Creates round in `CREATED` status.
  * **`START ROUND EXECUTION` button**: Transitions round from `CREATED` to `RUNNING` and broadcasts start signal to enclaves.
  * **`FAIL / CANCEL STALE ROUND` button**: Visible only when an active round is in `RUNNING` state without recent heartbeat. Prompts for cancellation reason and cleans up orphaned round state.

---

### 4.8 Live Round Operations (`/rounds/live` or `live-round`)

Real-time telemetry monitor tracking active round execution step-by-step across all participating client nodes.

* **Round Header Banner**: Displays Round Number (`R-X`), Execution Mode (`SIMULATION` / `HOSPITAL`), Status (`RUNNING`, `AGGREGATING`, `COMPLETED`), and Elapsed Time.
* **10-Stage Visual Execution Pipeline**:
  * `01 Initialization` → `02 Weight Dispatch` → `03 Local Training` → `04 Update Intake` → `05 L0 Verify` → `06 L1 Inspect` → `07 L2 Correlate` → `08 L3/L4 Simulate` → `09 Safe Aggregation` → `10 Lineage Commit`.
* **Enclave Telemetry Table & Topologies**:
  * Shows active channels for all configured participant nodes (e.g., H51 Clinical Diabetes Cohort, H21 Stanford Clinical Enclave).
  * Real-time participant state: `TRAINING`, `SUBMITTED`, `PENDING_ANALYSIS`, `QUARANTINED`, `AGGREGATED`.
* **Operational Control Buttons**:
  * **`AUTO-INGEST ENCLAVES (X/Y)` button**:
    * Displayed when the round is `RUNNING` and fewer updates have been received than configured nodes (`updates.length < participating`).
    * **Action**: Automatically executes local training across all unsubmitted participating hospital enclaves on their active local datasets, signs zero-pickle SafeTensors update packages, and dispatches them to the round intake queue with one click.
  * **`FINALIZE ROUND` / `FINALIZE WITH X NODE(S)` button**:
    * Enabled whenever at least 1 update has been received (`updates.length >= 1`).
    * If 0 updates are present, clicking it automatically triggers auto-ingestion for all configured nodes first, then executes finalization.
    * **Action**: Executes the full defense-in-depth pipeline (L0 Verify → L1 Inspect → L2 Correlate → L3 Influence → L4 Simulate → L5 Attribute → Trust Engine → Safe Aggregation) layer by layer, broadcasting real-time SSE WebSocket events and rendering live stage progress.
  * **`ABORT ROUND` button**: Emergency containment stop. Halts current training and logs containment audit record.

---

### 4.9 Update Intake Ledger (`/intake`)

The ingestion registry recording every candidate differential update received from participants.

* **Intake Metrics**: Total updates received, Accepted count, Quarantined count, Mean file size.
* **Update Intake Ledger Table**:
  * Columns: Update ID, Hospital Name, SafeTensors SHA-256 Digest, File Size, Ingested Timestamp, Signature Validated, Disposition (`ACCEPTED` / `QUARANTINED` / `PENDING`).
* **Row Action Buttons**:
  * **`INSPECT PAYLOAD` button**: Opens modal displaying raw tensor headers, parameter keys, min/max values, and metadata.
  * **`DOWNLOAD SAFETENSORS` button**: Downloads candidate update file for local forensic inspection.
  * **`TRIGGER DEFENSE GATES` button**: Dispatches update to the analytical security pipeline.

---

### 4.10 L0 Verify (`/layers/l0-verify` or `l0`)

Structural and cryptographic integrity gate for incoming model updates.

* **3D Volumetric Tensor Scanner (`L0TensorScanner3D`)**:
  * 3D wireframe lattice representing candidate tensor geometry with an animated scanning laser plane verifying SafeTensors headers.
  * Hover displays: Magic header string, parameter count, byte offset.
* **Verification Checklist Cards**:
  1. *SafeTensors Format Compliance*: Verified zero-pickle serialization format.
  2. *Header JSON Security Bounds*: Validated header byte length $< 1 \text{MB}$ preventing deserialization DOS.
  3. *Exact Tensor Geometry*: Validated tensor shapes match `FedSentinelCNN` (105,866 parameters).
  4. *Cryptographic Digest Integrity*: SHA-256 hash match against enclave submission signature.
* **Candidate Updates Verification Table**:
  * Displays pass/fail status for each client update across L0 criteria.
  * **`RE-SCAN ALL UPDATES` button**: Reruns structural checks across all candidate files.

---

### 4.11 L1 Inspect (`/layers/l1-inspect` or `l1`)

Spectral and statistical numerical sanity verification gate.

* **3D Norm Distribution Manifold (`L1NormDistribution3D`)**:
  * 3D scatter plot of candidate update L2 norms against the consensus norm envelope.
  * Outlier updates are highlighted with amber/red warning halos.
* **Inspection Metrics**:
  * *Global Norm Threshold ($\gamma$)*: Maximum permitted gradient norm.
  * *NaN/Inf Count*: Number of non-finite floating point elements detected (must be 0).
  * *128-D Privacy Projection*: Deterministic Johnson-Lindenstrauss random projection preserving distance without exposing raw weights.
* **Interactive Controls**:
  * **Clipping Threshold Slider**: Adjusts maximum permitted L2 norm envelope.
  * **`EXPORT NORM TELEMETRY (CSV)` button**: Exports norm distribution dataset for offline statistical analysis.

---

### 4.12 L2 Correlate (`/layers/l2-correlate` or `l2`)

Directional consensus and angular correlation gate identifying Byzantine trajectory drift.

* **3D Cosine Cluster Manifold (`L2CosineCluster3D`)**:
  * 3D node cluster showing angular cosine distance between participant update vectors and the consensus centroid.
  * Clusters tightly grouped around the centroid represent consensus updates; divergent outliers represent anomalous trajectories.
* **Analytical Metrics**:
  * *Pairwise Cosine Similarity Heatmap*: Matrix of angular similarities between all enrolled enclaves.
  * *Robust Coordinate-Wise Z-Score*: Median Absolute Deviation (MAD) metric resistant to up to 50% Byzantine poisoning.
* **Controls**:
  * **Outlier Cutoff Z-Score slider**: Adjusts sensitivity threshold ($z_{\text{thresh}} = 2.5 - 3.5\sigma$).
  * **`FLAG COORDINATED BYZANTINE GROUP` button**: Triggers multi-client sybil correlation analysis.

---

### 4.13 Forensic Quarantine Vault (`/quarantine`)

Forensic isolation chamber where candidate updates failing any defense gate are quarantined.

* **Quarantine Vault Header**:
  * Vault Status badge, total updates quarantined, high-risk threat count.
* **Sequestered Updates Table**:
  * Columns: Quarantine ID, Enclave Code, Failed Gate (L0–L5), Risk Score, Anomaly Vector, Sequester Timestamp.
* **Forensic Adjudication Action Buttons**:
  * **`INSPECT FORENSIC TELEMETRY` button**: Opens modal detailing the exact trigger evidence (e.g., Norm $18.4 > 4.2$, Cosine $0.12 < 0.65$).
  * **`RELEASE FROM QUARANTINE` button**:
    * Authoritative human-in-the-loop override.
    * Opens modal with mandatory **Clinical Rationale Textarea**.
    * **`CONFIRM OVERRIDE & ADMIT` button**: Releases update back into the aggregation pool and records permanent entry in Human Overrides ledger.
  * **`PERMANENTLY DISCARD` button**:
    * Destroys candidate update weights from the round consensus pool.
    * Records permanent audit entry and updates institution Bayesian reputation score downwards.

---

### 4.14 L3 Influence (`/layers/l3-influence` or `l3`)

Gradient influence and validation surface trajectory gate.

* **3D Loss Surface Landscape (`L3LossSurface3D`)**:
  * 3D wireframe loss landscape representing the holdout validation surface.
  * Shows candidate update gradient trajectory vectors pointing towards or away from the empirical loss minimum.
* **Metrics Table**:
  * *Directional Alignment ($\cos \theta_{\text{holdout}}$)*: Alignment of candidate step with the true validation gradient.
  * *Loss Delta ($\Delta \mathcal{L}$)*: Simulated change in validation cross-entropy if this update were applied.
* **Controls**:
  * **`RE-EVALUATE ON HOLDOUT SURFACE` button**: Reruns forward pass evaluation on the calibrated holdout dataset.

---

### 4.15 L4 Simulate (`/layers/l4-simulate` or `l4`)

Counterfactual shadow consensus simulation gate evaluating "what-if" inclusion harm.

* **3D Counterfactual Trajectory Visualizer (`L4Counterfactual3D`)**:
  * Dual-path 3D trajectory comparing the projected global model consensus **with** the candidate update versus **without** the candidate update (Leave-One-Out / LOO).
* **Counterfactual Comparison Deck**:
  * *Inclusion Accuracy vs Exclusion Accuracy*: Exact delta ($\Delta \text{Acc} = \text{Acc}_{\text{with}} - \text{Acc}_{\text{without}}$).
  * *Class-Wise Degradation Cards*: Highlights whether specific medical diagnosis classes suffer targeted drop in recall.
* **Action Buttons**:
  * **`RUN COUNTERFACTUAL SIMULATION` button**: Triggers Leave-One-Out validation pass across all candidate updates.

---

### 4.16 L5 Attribute (`/layers/l5-attribute` or `l5`)

Bayesian dynamic threat attribution and root-cause hypothesis profiling.

* **3D Attribution Radar (`L5AttributionRadar3D`)**:
  * Multi-axis 3D radar chart projecting posterior probabilities across 6 threat hypotheses:
    1. *Backdoor Trigger Injection*
    2. *Gradient Scaling Attack*
    3. *Free-Rider Zero Gradient*
    4. *Label-Flipping Distortion*
    5. *Coordinated Sybil Replacement*
    6. *Benign Clinical Non-IID Variance*
* **Attribution Breakdown Cards**:
  * Displays Bayesian posterior likelihood $P(H_k \mid E)$ with confidence intervals and suggested containment actions.
* **Controls**:
  * **`UPDATE BAYESIAN PRIORS` button**: Adjusts prior beliefs based on historical consortium threat frequency.

---

### 4.17 Trust Engine (`/trust`)

The long-term institutional reputation management and dynamic weighting system.

* **3D Trust Matrix Manifold (`TrustMatrix3D`)**:
  * 3D matrix where nodes represent enrolled healthcare institutions, color-coded by dynamic trust score ($T_i \in [0.00, 1.00]$).
* **Consortium Reputation Leaderboard**:
  * Table: Rank, Hospital Name, Enclave Code, Trust Score, Security Tier (`TRUSTED`, `PROBATION`, `HIGH_RISK`), Historical Rounds, Penalty Count.
* **Bayesian Hyperparameter Configuration**:
  * **Beta Prior $\alpha$ input**: Positive reinforcement weighting (default: `10.0`).
  * **Beta Prior $\beta$ input**: Negative penalty weighting (default: `1.0`).
  * **Attenuation Decay ($\lambda$) slider**: Memory retention factor per round (default: `0.98`).
  * **Non-Punitive Tolerance ($\sigma$) slider**: Safe variance buffer protecting benign clinical non-IID data from unwarranted penalties (default: `2.5\sigma`).
* **Action Buttons**:
  * **`RE-CALCULATE ALL TRUST SCORES` button**: Recomputes posterior trust scores across all institutions.
  * **`RESET TO CLINICAL BASELINE` button**: Restores all institutions to neutral initial trust ($0.85$).

---

### 4.18 Incident Management (`/incidents`)

Centralized Security Operations Center (SOC) incident response and containment feed.

* **Severity Filter Pills**:
  * **`ALL`**, **`CRITICAL`**, **`HIGH`**, **`MEDIUM`**, **`LOW`**.
* **Status Filter Tabs**:
  * **`OPEN`**, **`IN PROGRESS`**, **`RESOLVED`**.
* **Incident Card**:
  * Displays: Incident ID, Severity badge, Title, Forensic Description, Detected Timestamp, Affected Enclave, Recommended Containment Action.
  * **`ACKNOWLEDGE INCIDENT` button**: Marks incident as `IN_PROGRESS` and assigns current administrator.
  * **`RESOLVE INCIDENT` button**:
    * Opens resolution modal with mandatory **Resolution Summary** textarea.
    * **`CONFIRM RESOLUTION` button**: Sets status to `RESOLVED` and archives incident.
* **Global Actions**:
  * **`EXPORT INCIDENT AUDIT LOG (JSON)` button**: Downloads complete forensic log for regulatory reporting.

---

### 4.19 Human Overrides (`/overrides` or `human-overrides`)

Immutable ledger recording every human intervention and override decision.

* **Summary Metrics**: Total overrides executed, Quarantine releases, Forced discards, Most active officer.
* **Override Ledger Table**:
  * Columns: Override ID, Timestamp, Officer Name, Enclave Code, Update ID, Original Verdict, Overridden Verdict, Mandatory Clinical Justification.
* **Action Buttons**:
  * **`EXPORT OVERRIDE HISTORY (CSV)` button**: Exports CSV ledger for external compliance auditors.
  * **`NEW EMERGENCY OVERRIDE` button**: Opens manual adjudication modal for emergency administrative interventions.

---

### 4.20 Safe Aggregation Core (`/aggregation`)

The consensus model fusion engine responsible for computing new global model weights.

* **3D Particle Fusion Vortex (`SafeAggregationVortex3D`)**:
  * 3D visualization showing accepted candidate updates spiraling into a central vortex to fuse into the new global consensus model.
* **Aggregator Selector Buttons**:
  * **`FedAvg (Sample Weighted)` button**: Traditional Federated Averaging ($\theta = \sum \frac{n_k}{N} \theta_k$).
  * **`Coordinate Median` button**: Robust against up to 50% Byzantine poisoning; computes coordinate-wise medians across updates.
  * **`Trimmed Mean` button**: Trims top and bottom $\beta$ quantiles to eliminate extreme gradient outliers.
* **Participant Weighting Table**:
  * Lists participating enclaves, local sample sizes ($n_k$), normalized aggregation weights ($w_k$), and L0–L5 pass verification stamps.
* **Execution Action Buttons**:
  * **`EXECUTE SAFE AGGREGATION` button**: Computes consensus weights, writes new `FedSentinelCNN` SafeTensors file, updates global model version, and logs audit hash.

---

### 4.21 Global Model Explorer (`/model`)

Comprehensive neural architecture and parameter inspection desk.

* **3D Neural Architecture Visualizer (`NeuralModel3D`)**:
  * Interactive 3D visualization of `FedSentinelCNN` layers:
    * `Conv1`: 16 filters, $3 \times 3$ kernel, ReLU activation.
    * `Conv2`: 32 filters, $3 \times 3$ kernel, ReLU activation.
    * `FC1`: Fully connected layer (512 units).
    * `FC2 / Output`: Classification head (10 classes).
  * Interactive click on layer displays parameter tensor dimensions, weight histograms, and activation maps.
* **Global Model Metrics**:
  * *Version*: Current model version string (e.g., `v3.0`).
  * *Total Parameters*: Exact `105,866` float32 parameters.
  * *Validation Accuracy*: Top-1 accuracy percentage on holdout benchmark.
  * *Cryptographic SHA-256 Digest*: Hash of current SafeTensors file.
* **Model Export Action Buttons**:
  * **`DOWNLOAD SAFETENSORS (.safetensors)` button**: Downloads current global model weights.
  * **`EXPORT ONNX FORMAT` button**: Generates ONNX export for inference deployment in clinical workstations.

---

### 4.22 Model Lineage DAG (`/lineage` or `model-lineage`)

Cryptographic provenance tracking every iteration of the global consensus model.

* **3D Lineage Tree Visualizer (`ModelLineageTree3D`)**:
  * 3D Directed Acyclic Graph (DAG) connecting model versions from genesis ($v0$) through sequential rounds.
  * Nodes are color-coded by validation accuracy; edges represent training rounds.
* **Checkpoint Inspector Panel**:
  * Displays: Model Version, Round Number, Aggregation Algorithm, Participant Count, Validation Loss, Accuracy Delta, Parent Hash.
* **Lineage Action Buttons**:
  * **`ROLLBACK TO THIS VERSION` button**:
    * High-assurance safeguard for restoring prior model checkpoints if an undetected poisoning attack is discovered post-aggregation.
    * Prompts for mandatory **Rollback Rationale**.
    * **`CONFIRM CRYPTOGRAPHIC ROLLBACK` button**: Restores selected version weights as active global model and logs rollback event.

---

### 4.23 Cryptographic Audit Trail (`/audit`)

Append-only tamper-evident event log satisfying regulatory compliance standards.

* **Filter & Search Controls**:
  * **Actor Filter dropdown**: `All Actors`, `Super Admin`, `System Automated`, `Hospital Enclave`.
  * **Action Filter dropdown**: `All Actions`, `LOGIN`, `ROUND_CREATE`, `UPDATE_INTAKE`, `QUARANTINE`, `OVERRIDE`, `AGGREGATION`, `ROLLBACK`.
  * **Date Range Pickers**: Filter by start and end timestamps.
* **Audit Ledger Table**:
  * Columns: Event ID, Timestamp, Actor ID, Client IP Address, Action Performed, Resource Target, Cryptographic HMAC-SHA256 Seal.
* **Audit Action Buttons**:
  * **`VERIFY AUDIT CHAIN INTEGRITY` button**: Validates sequential HMAC chain hashes to mathematically prove zero log tampering.
  * **`EXPORT AUDIT LEDGER (JSON)` button**: Downloads complete verifiable audit ledger in JSON format.
  * **`EXPORT AUDIT LEDGER (CSV)` button**: Downloads tabular audit report for compliance officers.

---

### 4.24 Round Replay (`/replay`)

Forensic time-travel interface for scrubbing through historical rounds.

* **Interactive Timeline Scrubber Bar**:
  * 10-stage sequential scrubber allowing step-by-step forensic reconstruction.
* **Playback Controls**:
  * **`PLAY` / `PAUSE` button**: Starts or pauses automated timeline playback.
  * **`STEP BACKWARD (<)` button**: Moves back one execution stage.
  * **`STEP FORWARD (>)` button**: Advances one execution stage.
  * **Playback Speed buttons (`0.5x`, `1x`, `2x`, `4x`)**: Adjusts playback animation speed.
* **Stage Inspection Window**:
  * Displays exact network state, candidate update arrivals, gate verdicts, and loss telemetry at the selected historical moment.

---

### 4.25 Executive Attestation Reports (`/reports`)

Publication-grade regulatory compliance dossier generator.

* **Regulatory Framework Checkboxes**:
  * **`HIPAA Security Rule (45 CFR § 164.312)`**: Focuses on access controls, encryption, and zero patient data egress.
  * **`FDA 21 CFR Part 11`**: Focuses on tamper-evident audit trails, electronic signatures, and model lineage.
  * **`EU AI Act (High-Risk AI Standards)`**: Focuses on risk management, data governance, and human oversight.
  * **`NIST AI RMF 1.0`**: Focuses on AI safety, robustness against adversarial attacks, and explainability.
* **Dossier Generation Buttons**:
  * **`GENERATE COMPLIANCE DOSSIER` button**: Compiles live telemetry, audit signatures, and lineage records into an executive report.
  * **`PRINT / SAVE AS PDF` button**: Triggers browser print dialog with print-optimized CSS layout.
  * **`DOWNLOAD SIGNED JSON ATTESTATION` button**: Exports cryptographically signed attestation certificate.

---

## 5. Hospital Clinical Enclave Portal (Every Feature & Button)

```
========================================================================================
HOSPITAL PORTAL NAVIGATION GROUPS:
[COMMAND]               Hospital Command (command)
[HOSPITAL]              My Hospital (hospital) | Federation (federation) |
                        Team & Access (team)
[DATA]                  Datasets (datasets) | Data Quality (quality)
[FEDERATED LEARNING]    Current Round (round) | Local Training (training) |
                        Model Updates (updates) | Global Model (global-model)
[SECURITY]              Security Status (security) | Incidents (incidents) |
                        Trust (trust)
[REPORTS]               Reports & Exports (reports)
[SYSTEM]                Audit Activity (audit) | Settings (settings)
========================================================================================
```

---

### 5.1 Hospital Command (`command`)

The primary executive dashboard for enclave clinical operators.

* **Enclave Health Indicators**:
  * Enclave Status: `ACTIVE` / `QUARANTINED` / `SUSPENDED`.
  * Security Posture: `TRUSTED` / `PROBATION`.
  * Federation Boundary: `ENCLAVE LOCKED (ZERO EGRESS)`.
* **Metric Cards**:
  * *Local Clinical Samples*: Total training records stored in enclave.
  * *Current Round Participation*: Round ID and participation eligibility.
  * *Bayesian Trust Rating*: Hospital reputation score ($0.00 - 1.00$).
  * *Update Acceptance Rate*: Percentage of local updates accepted by control plane.
* **Quick Navigation Buttons**:
  * **`START TRAINING PIPELINE` button**: Navigates directly to `training`.
  * **`MANAGE DATASETS` button**: Navigates directly to `datasets`.
  * **`VIEW SECURITY POSTURE` button**: Navigates directly to `security`.

---

### 5.2 My Hospital Identity & Profile (`hospital`)

Institutional profile management and enclave credential security.

* **Hospital Identity Card**:
  * Displays: Legal Name, Enclave Callsign, Joined Timestamp, Facility Address, Website, Primary Emergency Phone, Specialization.
* **Profile Management Buttons**:
  * **`EDIT PROFILE` button**:
    * Opens modal with inputs for Phone, Address, Official Website, and Specialization Description.
    * **`SAVE PROFILE CHANGES` button**: Dispatches `PATCH /api/v1/hospital/profile`. Updates records instantly.
    * **`CANCEL` button**: Discards edits.
  * **`CHANGE PASSWORD` button**:
    * Opens credential update modal with: Current Password, New Password, Confirm New Password.
    * **`UPDATE ENCLAVE PASSWORD` button**: Dispatches `POST /api/v1/hospital/change-password`. Verifies current password, writes Argon2id hash, records audit event.
    * **`CANCEL` button**: Closes modal.

---

### 5.3 Federation Consortium Membership (`federation`)

Consortium details and peer network status.

* **Federation Information Card**:
  * Consortium Name, Federation UUID (`413ef0b3-a947-4a02-a652-d963ef14b8da`), Governance Type, Consensus Strategy.
* **Peer Enclaves Roster**:
  * View participating peer healthcare centers without exposing any peer data or private endpoints.

---

### 5.4 Team & Enclave Access Management (`team`)

Enclave staff and operator account management.

* **Staff Directory Table**:
  * Columns: Staff Name, Email, Role (`HOSPITAL_ADMIN`, `ENCLAVE_OPERATOR`, `CLINICAL_AUDITOR`), Status (`ACTIVE` / `DISABLED`), Last Login.
* **Account Action Controls**:
  * **`INVITE / ADD STAFF MEMBER` button**:
    * Opens modal with: Full Name, Email Address, Assigned Role, Initial Password.
    * **`CREATE STAFF ACCOUNT` button**: Submits `POST /api/v1/hospital/staff`.
    * **`CANCEL` button**: Closes modal.
  * **`TOGGLE STATUS (Deactivate / Activate)` button**: Toggles staff member active flag (`PATCH /api/v1/hospital/staff/{id}`).

---

### 5.5 Clinical Dataset Management Hub (`datasets`)

Ingest, format, and manage local clinical datasets.

* **Dataset Inventory Table**:
  * Columns: Dataset Name, Modality, Total Records, Format (`SafeTensors`, `NPZ`, `CSV`), Verification Status, Active Flag.
* **`CREATE DATASET` button**:
  * Opens dataset initialization modal.
  * **Quick Clinical Template Presets**:
    * **`Chest X-Ray Pneumonia`**: Image classification, 2 classes (Normal vs Pneumonia), 100 samples.
    * **`Diabetic Retinopathy Screening`**: Fundus photography, 5 lesion grades, 200 samples.
    * **`Brain MRI Lesions`**: Neurological scans, 4 classes, 150 samples.
    * **`MedMNIST Pathology`**: Multi-tissue diagnostic benchmark, 10 classes, 250 samples.
  * **Custom Dataset Inputs**: Dataset Name, Modality, Class Count.
  * **`CREATE & INITIALIZE DATASET` button**: Registers dataset metadata in enclave.
* **Dataset Row Action: `VERSIONS & INGEST` button**:
  * Opens the multi-modal Ingestion Drawer with 3 specialized tabs:
  * **Tab 1: Direct File Upload (`Upload`)**:
    * Drag-and-drop file zone supporting `.zip`, `.tar.gz`, `.csv`, `.parquet`, `.npz`.
    * Automatically extracts multi-class image folder archives into normalized $(1, 28, 28)$ tensors.
    * **`UPLOAD & PARSE TENSORS` button**: Dispatches multipart form data to `/api/v1/hospital/datasets/{id}/upload`.
  * **Tab 2: Remote URL & Online Repositories (`Remote URL`)**:
    * Input field for direct HTTP/HTTPS URL or online dataset repository (Hugging Face, GitHub, Zenodo, Kaggle, Mendeley Data).
    * Enforces strict Server-Side Request Forgery (SSRF) filters blocking loopback (`127.0.0.1`), RFC-1918 subnets (`10.0.0.0/8`, `192.168.0.0/16`), and cloud metadata (`169.254.169.254`).
    * **`FETCH & INGEST REMOTE DATASET` button**: Dispatches `POST /api/v1/hospital/datasets/{id}/fetch-remote`.
  * **Tab 3: In Situ Clinical Benchmark Generator (`Sample Data`)**:
    * Generates authentic, zero-egress clinical synthetic records directly on enclave hardware.
    * Sample Count slider (10 to 500 samples).
    * **`GENERATE LOCAL CLINICAL BENCHMARK RECORDS` button**: Synthesizes records directly into local storage.
* **Other Dataset Actions**:
  * **`SET AS ACTIVE FEDERATION DATASET` button**: Marks selected dataset as the active training set for upcoming federation rounds.
  * **`DELETE DATASET` button**: Removes dataset from enclave (prompts for confirmation).

---

### 5.6 Clinical Data Quality Register (`quality`)

Verifies that local data passes strict pre-training quality gates before submission to the federation.

* **5-Point Pre-Flight Verification Checklist**:
  1. *Zero-Pickle Serialization*: Verifies files are stored in SafeTensors / NPZ format without executable Python pickles.
  2. *Normalized Tensor Dimensions*: Verifies image tensors conform to $(N, 1, 28, 28)$ dimension bounds.
  3. *Finite Value Bounds*: Verifies 0.0% NaN (Not-a-Number) and 0.0% Inf (Infinity) values.
  4. *Diagnostic Class Balance*: Verifies representation across all target diagnostic classes.
  5. *Sample Sufficiency Threshold*: Verifies cohort size meets minimum training batch ($N \ge 10$).
* **Quality Action Buttons**:
  * **`RUN COMPLETE QUALITY AUDIT` button**: Scans active dataset and updates quality status badges.
  * **`ACTIVATE FOR FEDERATION TRAINING` button**: Unlocks training pipeline for this dataset once all 5 gates pass.

---

### 5.7 Current Federation Round (`round`)

Live round inspection from the enclave's clinical perspective.

* **Round Information Cards**:
  * Current Round Number, Phase (`OPEN_FOR_TRAINING`, `AGGREGATING`, `SEALED`), Round Start Timestamp, Deadline.
* **Hyperparameter Specifications**:
  * Local Epochs, Batch Size, Learning Rate, Optimizer.
* **Enclave Eligibility Banner**:
  * Shows whether this enclave is approved and selected to participate in the current round.

---

### 5.8 In Situ Local Model Training Pipeline (`training`)

The core clinical training workstation where authentic PyTorch model training is executed directly on local hospital hardware.

* **Dual Operational Training Modes**:
  * **Mode A: Active Round Submission Mode**:
    * Active when the central federation has a round in status `RUNNING`.
    * Button: **`EXECUTE & SUBMIT TO ACTIVE ROUND R-X`** (Play icon).
    * Submits the resulting SafeTensors differential update into the active consensus round.
  * **Mode B: Enclave Pre-Flight Mode**:
    * Active when no round is currently running (`IDLE` / `COMPLETED`).
    * Banner: `Enclave Pre-Flight Mode: Run local training, compute loss & verify SafeTensors weights before admin starts round.`
    * Button: **`RUN LOCAL ENCLAVE TRAINING & PRE-FLIGHT AUDIT`** (Zap icon).
    * Pulls the latest verified global model checkpoint, trains on the active local dataset, computes loss and differential weights, and tests L0-L5 gate readiness without submitting to an open round.
* **Dynamic Classifier Dimension Alignment**:
  * Automatically detects global model class dimensions (e.g. 10 output classes) and harmonizes local dataset label counts (e.g., 2 classes for diabetes cohort), ensuring seamless PyTorch state loading and mathematical gradient compatibility.
* **12-Stage Visual Training Progression**:
  * `01 Global Model Ingestion` → `02 Local Dataset Partitioning` → `03 PyTorch SGD Training` → `04 Weight Delta Extraction` → `05 SafeTensors Serialization` → `06 SHA-256 Checksum` → `07-12 L0-L5 Gate Evaluation & Routing Verdict`.
* **Telemetry HUD**: Displays Local Training Loss, Processed Clinical Samples, Serialized Artifact Size (KB), SHA-256 Digest, and Security Routing Verdict (`AGGREGATION` vs `QUARANTINE`).

---

### 5.9 Model Updates & Contribution Value Register (`updates`)

Audit history and institutional contribution value ledger of all differential updates submitted by this enclave.

* **Institutional Value Summary Metrics**:
  * *TOTAL CONTRIBUTIONS*: Total round updates submitted by this hospital enclave.
  * *ACCEPTED INTO GLOBAL*: Count and percentage of updates that successfully passed L0-L5 gates and merged into the global model.
  * *PATIENT EXAMPLES CONTRIBUTED*: Total count of patient clinical records trained in-situ with zero data egress.
  * *SAFE DIFFERENTIAL WEIGHTS*: Total volume of zero-pickle SafeTensors gradient parameters securely transmitted.
* **Contribution Value Register Table**:
  * Columns:
    * **UPDATE ID & HASH**: Monospaced unique update identifier and SHA-256 fingerprint.
    * **ROUND**: Federation round callsign (`R-20`, `R-21`, etc.).
    * **CONTRIBUTION VALUE**: Patient sample count, round contribution percentage share ($w_k = \frac{n_k}{\sum n_i}$), and differential gradient norm ($\|\Delta W\|$).
    * **QUALITY TIER**: Automated data fidelity classification badge (`HIGH_FIDELITY` for $\ge 500$ records, or `STANDARD`).
    * **AGGREGATION IMPACT**: Clear status badge: `AGGREGATED TO GLOBAL` (emerald), `QUARANTINED` (amber/red), or `REVIEW`.
    * **L0 INTEGRITY**: Cryptographic zero-pickle check badge (`PASSED`).
    * **SUBMITTED**: Formatted UTC submission timestamp.
* **Action Buttons**:
  * **`REFRESH` button**: Re-synchronizes update telemetry from `/api/v1/hospital/updates`.
  * **`INSPECT` button**: Opens modal displaying full update metadata, cryptographic digest, parameter count, and audit trail.

---

### 5.10 Global Consensus Model Registry & Synchronization (`global-model`)

View and verify the central server-verified global consensus model checkpoint and enclave synchronization state.

* **Global Model Metric Cards**:
  * *ACTIVE MODEL VERSION*: Latest consensus version tag (e.g. `v21` / `round-10`).
  * *TOTAL TRAINABLE PARAMETERS*: 105,866 parameters across dual-layer Conv2D + Dense classifier.
  * *GLOBAL CONVERGENCE*: Real-time convergence status (`CONVERGED` / `ACTIVE_TRAINING`).
  * *ENCLAVE SYNCHRONIZATION*: Local alignment badge (`SYNCHRONIZED`).
* **Neural Architecture Specification Panel**:
  * Model Family: `FedSentinel-Clinical-CNN`.
  * Architecture Spec: `FedSentinelCNN (Conv2d 16 -> Conv2d 32 -> Dense 64 -> Multi-Class Head)`.
  * Input Dimensions: `[Batch, 1, 28, 28] / Clinical Biomarker Tensor`.
  * Output Dimensions: `[Batch, 10] Differential Logits`.
  * Weight Serialization: SafeTensors zero-pickle format.
* **Provenance & Cryptographic Integrity Panel**:
  * Active Federation Name and UUID.
  * Latest Round Completed, Cumulative Accepted Updates, and Quarantined Anomaly Updates.
  * SHA-256 Checkpoint Hash: Complete 64-character hexadecimal digest verifying model weights.
* **Action Buttons**:
  * **`VERIFY & SYNC GLOBAL MODEL` button**: Fetches live verified global model metadata from `/api/v1/hospital/global-model` and confirms local enclave synchronization.

---

### 5.11 Enclave Security Status & Self-Test (`security`)

Security health check and cryptographic boundary verification.

* **Enclave Hardware Isolation Card**:
  * Hardware Boundary status: `LOCKED`.
  * Patient Data Egress Filter: `ZERO EGRESS ENFORCED`.
  * Storage Encryption: `AES-256 GCM`.
* **6-Layer Security Gate Standards**:
  * Explanations of criteria evaluated by L0–L5 control plane gates.
* **Action Buttons**:
  * **`RUN ENCLAVE SECURITY SELF-TEST` button**:
    * Verifies local directory permissions.
    * Confirms zero unauthorized outbound network ports.
    * Tests SafeTensors serialization engine.
    * Displays green checkmarks on successful test.

---

### 5.12 Clinical Incidents Feed (`incidents`)

Security alerts and anomaly notifications involving this enclave.

* **Incident Feed Cards**:
  * Displays: Alert Title, Severity (`HIGH`, `MEDIUM`), Timestamp, Detected Anomaly (e.g., Gradient Norm Spike, Divergence Alert).
* **Action Buttons**:
  * **`REQUEST ADMINISTRATIVE REVIEW` button**:
    * Opens modal allowing the clinical operator to provide medical context for an anomaly (e.g., "Non-IID variance due to specialized rare disease pediatric patient population").
    * **`SUBMIT REVIEW REQUEST` button**: Sends explanation to the Super Admin Quarantine desk.
    * **`CANCEL` button**: Closes modal.

---

### 5.13 Visual Trust Engine (`trust`)

Enclave Bayesian reputation gauge and clinical good faith guarantee.

* **Circular SVG Reputation Gauge**:
  * Dynamic visual dial displaying the institution's trust score ($0.00$ to $1.00$).
  * Tier Badge: `TRUSTED STATUS` ($T \ge 0.85$) or `PROBATION STATUS`.
* **Bayesian Scoring Parameters**:
  * Beta Prior: $\text{Beta}(\alpha=10.0, \beta=1.0)$.
  * Attenuation Decay Factor: $\lambda = 0.98$.
  * Non-Punitive Tolerance Envelope: $2.5\sigma$.
* **Non-Punitive Clinical Guarantee Banner**:
  * Explicit legal and algorithmic assurance that genuine clinical outliers arising from rare patient conditions are not subjected to punitive permanent bans.
* **Sequential Trust Evaluation Ledger**:
  * Table of historical rounds, updates submitted, evaluated anomaly scores, and resulting posterior trust score adjustments.

---

### 5.14 Reports & Exports (`reports`)

Local compliance reporting and data exports.

* **Export Options**:
  * **`EXPORT LOCAL TRAINING LOG (CSV)` button**: Downloads CSV containing all epoch loss values and timestamps.
  * **`EXPORT UPDATE DIGEST REGISTRY (JSON)` button**: Downloads JSON list of submitted update hashes for auditing.
  * **`GENERATE ENCLAVE COMPLIANCE SUMMARY` button**: Generates printable institutional compliance certificate.

---

### 5.15 Enclave Audit Activity (`audit`)

Local enclave event log tracking actions performed by local operators.

* **Local Audit Table**:
  * Columns: Event Timestamp, Staff Member, Action (`DATASET_UPLOAD`, `TRAINING_START`, `UPDATE_SUBMIT`, `PASSWORD_CHANGE`), IP Address.
* **Action Buttons**:
  * **`DOWNLOAD LOCAL AUDIT LOG (JSON)` button**: Downloads enclave-specific audit trail.

---

### 5.16 Enclave Settings (`settings`)

Local configuration and preferences.

* **Configuration Inputs**:
  * **Local Storage Cache Limit input**: Maximum disk space allocated for local model weights and datasets.
  * **Telemetry Refresh Interval dropdown**: `5s`, `10s`, `30s`, `Manual`.
  * **Email Alert Notification toggle**: Enable or disable automated emails for round start and security alerts.
* **`SAVE ENCLAVE SETTINGS` button**: Saves local preferences.

---

---

### 5.17 Multi-Modal Disease Risk Prediction & Consortium Aggregated Updates (`prediction`)

In-situ clinical decision support, multi-disease identification, and **Consortium Aggregated Global Disease Updates** powered by verified federated consensus.

#### Consortium Aggregated Global Disease Updates & FedSentinel Prevention
The platform securely stores aggregated global model updates categorized across primary clinical domains:
* **`PULMONARY_IMAGE`** (*Pulmonary Pneumonia & Respiratory Infiltration*): Aggregated via Coordinate-Median from H21 and H01.
* **`METABOLIC_DIABETES`** (*Type-2 Diabetes & Endocrine Biomarkers*): Aggregated from H51 and H01. **Poisoning Prevented**: FedSentinel intercepted and quarantined 1 malicious scaling backdoor update (+25.0 scale gradient drift), preventing corrupted weights from compromising diabetes predictions across all other member hospitals.
* **`CARDIOMETABOLIC`** (*Cardiometabolic & Acute Coronary Syndrome*): Aggregated via Coordinate-Median from H21 and H25.
* **`DERMATOLOGIC`** (*Dermatologic Dysplastic & Melanoma Lesions*): Aggregated via Robust Trimmed-Mean from H95 and H21.
* **`CONSENSUS_MULTI`** (*Unified Multi-Disease Federated Consensus*): Consortium-wide consensus model spanning 17 verified hospital updates.

In-situ clinical decision support and disease identification powered by the consensus-trained federated global neural model. Member hospitals can diagnose conditions using **Medical Images (Radiology / Scans)**, **Clinical EHR Notes (Text / Symptoms)**, or **Biomarker Vitals (Lab values)**.

```
+-------------------------------------------------------------------------------------------------------+
| CLINICAL INTELLIGENCE / FEDERATED MULTI-MODAL IN SITU INFERENCE                                       |
| Disease Risk Prediction & Diagnostic Enclave                                                          |
|                                                                                                       |
| [ MODALITY SELECTOR TABS ]                                                                            |
| [ Medical Images (Radiology / Scans) ]  [ Clinical EHR Notes & Symptoms ]  [ Biomarkers & Vitals ]    |
|                                                                                                       |
| [ 1-CLICK MEDICAL SCAN PRESETS ]                                                                      |
| [Chest X-Ray: Infiltration/Pneumonia]  [Chest X-Ray: Cardiomegaly]  [Dermoscopy: Dysplastic] [Normal] |
|                                                                                                       |
| IN SITU DATA INPUT [IMAGE]                          DIAGNOSTIC OUTCOME & DIFFERENTIALS (HUD)          |
| Patient ID:        [ PT-CLINICAL-8821           ]   [ MODALITY: IMAGE  ·  RISK TIER: CRITICAL ] [92.5%|
| Diagnostic Target: [ Automated Multi-Disease    ]   Community-Acquired Pneumonia (Lobar Infiltration) |
| [ Medical Scan Image Dropzone / Preview        ]   OBJECTIVE CLINICAL FINDINGS:                       |
|   - Base64 Pixel Matrix · Tensor [1, 1, 28, 28]     Focal radiopaque consolidation in lower parenchyma|
|   - [Browse Local Files] / [Replace Medical Image]  DIFFERENTIAL DIAGNOSIS SPECTRUM:                  |
|                                                     #1 Community-Acquired Pneumonia       [====] 92.5%|
| [ RUN MULTI-MODAL FEDERATED INFERENCE (Button) ]    #2 Cardiomegaly / Cardiac Failure     [==  ] 18.2%|
|                                                     #3 Viral Interstitial Infiltrate      [=   ]  9.4%|
|                                                     DETECTED CLINICAL ENTITIES & METRICS:             |
|                                                     - optical_density: 0.42  - lower_opacity: 0.51    |
|                                                     CLINICAL ACTION PROTOCOL:                         |
|                                                     Initiate empiric antimicrobial therapy...         |
+-------------------------------------------------------------------------------------------------------+
```

#### Modality Selector Tabs
* **`Medical Images (Radiology / Scans)` tab**: Activates computer vision inference on radiographic or pathological scans using the federated convolutional neural network (`FedSentinelCNN`).
* **`Clinical EHR Notes & Symptoms` tab**: Activates natural language clinical ontology extraction on physician notes, nursing records, or symptom narratives.
* **`Biomarkers & Lab Indicators` tab**: Activates multidimensional clinical risk regression on patient lab values (glucose, BMI, blood pressure, insulin, pedigree).

#### 1-Click Diagnostic Presets
* **Image Scan Presets**:
  * **`Chest X-Ray: Infiltration / Pneumonia`**: Bilateral lung fields with right lower lobe focal consolidation opacity and air bronchograms.
  * **`Chest X-Ray: Cardiomegaly / Failure`**: Markedly enlarged transverse cardiac silhouette (>60% cardiothoracic ratio).
  * **`Dermoscopy: Dysplastic Lesion`**: Asymmetric pigmented cutaneous macule with border irregularity.
  * **`Normal Chest Radiograph`**: Clear bilateral lung fields with crisp cardiophrenic angles and normal silhouette.
  * **`Non-Medical / Out-of-Distribution Test`**: Multi-color non-clinical test pattern to demonstrate and verify automatic ML Out-of-Distribution (OOD) rejection.
* **Clinical Notes Narrative Presets**:
  * **`Acute Pulmonary Infection`**: Productive purulent rust-colored sputum, 39.2°C fever, chills, pleuritic chest pain, dyspnea, and SpO2 91%.
  * **`Severe Glycemic / Type-2 Diabetes`**: Persistent polydipsia, polyuria, nocturia x4, lethargy, fasting glucose 218 mg/dL, HbA1c 9.6%, and peripheral neuropathy.
  * **`Acute Coronary Syndrome / Angina`**: Retrosternal crushing chest pressure radiating into left arm and jaw, diaphoresis, dyspnea, and BP 168/102 mm Hg.
  * **`Severe Asthma / Bronchospasm`**: Refractory bronchospasm, bilateral expiratory wheezes, tachypnea at 28 breaths/min, and peak expiratory flow at 52%.
* **Biomarker Lab Presets**:
  * **`High-Risk Diabetic Patient`**: Glucose 168 mg/dL, BMI 36.2, Age 52, BP 82, Insulin 180.
  * **`Borderline / Pre-Diabetic`**: Glucose 128 mg/dL, BMI 28.4, Age 42, BP 74, Insulin 95.
  * **`Normal Healthy Control`**: Glucose 85 mg/dL, BMI 21.8, Age 26, BP 68, Insulin 60.

#### Input Fields & Controls
* **`Patient Identifier` input**: Clinical EHR patient tracking number (e.g. `PT-CLINICAL-8821`).
* **`Diagnostic Classifier Target` dropdown**:
  * `Automated Multi-Disease Consensus (Any Condition)`: System scans across pulmonary, metabolic, cardiovascular, respiratory, and dermatologic diagnostic spaces.
  * `Pulmonary Pneumonia & Respiratory Infiltration`
  * `Cardiometabolic & Acute Coronary Syndrome`
  * `Type-2 Diabetes & Endocrine Risk`
  * `Dermatologic Dysplastic Lesions`
* **Image Upload Dropzone / File Picker**: Supports direct upload of local medical image files (`PNG`, `JPEG`, `DICOM`-derived bitmaps) with live in-memory base64 thumbnail rendering.
* **Clinical Notes `<textarea>`**: Live text editor with character counter for inputting admission notes or physical exam findings.
* **Biomarker Interactive Range Sliders**: Real-time sliders for Glucose, BMI, Age, Blood Pressure, Insulin, and Diabetes Pedigree Function with clinical normal/impaired guideline thresholds.

#### Inference Execution & Diagnostic HUD
* **`RUN MULTI-MODAL FEDERATED INFERENCE` button**:
  * Dispatches multi-modal payload to `POST /api/v1/hospital/predict`.
  * Runs genuine PyTorch CNN feature map extraction or clinical NLP ontology parsing in-situ inside the hospital memory space.
  * Records tamper-evident audit trail `CLINICAL_INFERENCE_EXECUTED` with patient ID and condition.
* **Risk Tier Badge**: Color-coded risk tier (`CRITICAL` vibrant red, `HIGH` amber-red, `MODERATE` warning yellow, `LOW` verified green, `INCONCLUSIVE` neutral slate).
* **Primary Diagnostic Finding**: Concise clinical diagnosis or out-of-distribution verdict (e.g., `Community-Acquired Pneumonia (Lobar Pulmonary Infiltration)` or `Inconclusive / Out-of-Distribution Image (No Known Clinical Signature)`).
* **Primary Confidence Meter / Match Score**: High-precision statistical confidence percentage (e.g., `93.93%` for matched conditions, `< 25%` match score for out-of-distribution uploads).
* **Federated Consortium Learning Lineage Card**: Visual metadata pill cloud displaying all contributing member hospital enclaves whose accepted updates actively synthesized the consensus model checkpoint (e.g., `H51 Clinical Diabetes Cohort`, `H21 Stanford Clinical AI Enclave`), update counts, and checkpoint hash.
* **Objective Clinical Findings Summary**: Narrative synthesis of optical metrics (radiographic density, quadrant opacity ratios) or symptom entities extracted from the patient's records.
* **Differential Diagnosis Spectrum**: Ranked list of top candidate conditions with confidence tier badges and probability progress bars.
* **Detected Clinical Entities & Metrics**: Visual chip cloud displaying all extracted biomarkers, vitals, or optical metrics (e.g., `optical_density: 0.42`, `spo2: 91%`, `fever: 39.2C`).
* **Attribution & Feature Importance Impact**: Ranked horizontal bar breakdown displaying factor contributions.
* **Clinical Protocol & Recommendation**: Evidence-based medical directives (e.g., empiric antimicrobial coverage, urgent arterial blood gas, cardiology consult).
* **Enclave Isolation Guarantee**: Explicit zero-trust assurance card certifying that raw images, notes, and vitals never departed this hospital node's network boundary.

---

## 6. End-to-End Operational Lifecycle Walkthrough

To execute a complete operational federation cycle from start to finish:

```
[01 Super Admin Login] -> [02 Hospital Self-Registration] -> [03 Review & Approve] ->
[04 Hospital Login] -> [05 Ingest Dataset] -> [06 Verify Quality] ->
[07 Admin Round Config] -> [08 Enclave Local Training] -> [09 L0-L5 Gate Evaluation] ->
[10 Safe Aggregation] -> [11 Model Lineage] -> [12 Executive Attestation Dossier]
```

1. **Super Admin Setup**: Log in at `/admin/login` using `admin@fedsentinel.local` / `Admin123!`.
2. **Hospital Registration**: In a private/incognito window, open `/hospital/login`, click **Register New Institution**, fill in hospital details (e.g. `H25` Mayo Clinic), and submit.
3. **Approve Institution**: In the Admin portal, navigate to **Registration Requests** (`/requests`), find `H25`, click **REVIEW APPLICATION**, then click **APPROVE & ONBOARD**.
4. **Hospital Data Ingestion**: Sign in to Hospital Portal at `/hospital/login` with the newly approved credentials. Navigate to **Datasets** (`datasets`), click **CREATE DATASET**, select **Chest X-Ray Pneumonia**, and click **CREATE & INGEST**. In the dataset drawer, click **Sample Data** and click **GENERATE LOCAL CLINICAL BENCHMARK RECORDS**.
5. **Quality Verification**: Navigate to **Data Quality** (`quality`), click **RUN COMPLETE QUALITY AUDIT**, and click **ACTIVATE FOR FEDERATION TRAINING**.
6. **Round Configuration**: In Admin Portal, navigate to **Round Configuration** (`/rounds/configure`). Select **HOSPITAL MODE**, select participating clients, set epochs to `1`, and click **CREATE NEW FEDERATION ROUND**. Once created, click **START ROUND EXECUTION**.
7. **Local In Situ Training**: In Hospital Portal, navigate to **Local Training** (`training`). Notice the round is now `OPEN`. Click **START LOCAL TRAINING & SUBMIT UPDATE**. Observe the real-time epoch training progress, $\Delta W$ delta extraction, SafeTensors serialization, and dispatch to the control plane.
8. **Defense Evaluation**: In Admin Portal, watch candidate updates stream into **Update Intake** (`/intake`). Navigate through **L0 Verify**, **L1 Inspect**, **L2 Correlate**, **L3 Influence**, **L4 Simulate**, and **L5 Attribute** to observe real telemetry pass gates.
9. **Safe Aggregation**: Navigate to **Safe Aggregation** (`/aggregation`). Select **Coordinate Median** and click **EXECUTE SAFE AGGREGATION**.
10. **Lineage & Reports**: Navigate to **Model Lineage** (`/lineage`) to view the newly committed model version checkpoint in 3D. Navigate to **Reports** (`/reports`), select regulatory frameworks, and click **GENERATE COMPLIANCE DOSSIER** $\to$ **PRINT / SAVE AS PDF**.
11. **Logout**: Click **LOGOUT** in the top-right header of both portals to securely terminate sessions.

---

## 7. Verification & Production Build Commands

```powershell
# 1. Run full backend pytest test suite (67 unit tests)
.\.venv\Scripts\pytest.exe tests/unit -q

# 2. Compile and verify frontend production build (Vite 8)
npm --prefix frontend run build
```

Expected Output:
* Pytest: `67 passed in ~3s` (100% pass rate)
* Vite: `✓ built in ~2.5s` (0 errors, 0 broken imports)
