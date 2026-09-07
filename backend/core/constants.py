"""
FedSentinel system-wide constants.

Keep security-sensitive thresholds and operational limits centralized here.
Detection algorithms may override these through configuration, but should
not scatter magic numbers throughout the codebase.
"""

# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------

APP_NAME = "FedSentinel"
APP_VERSION = "0.1.0"
API_PREFIX = "/api"

# ---------------------------------------------------------------------------
# Federation
# ---------------------------------------------------------------------------

DEFAULT_CLIENT_COUNT = 20
DEFAULT_MIN_CLIENTS_FOR_ROUND = 5

DEFAULT_LOCAL_EPOCHS = 1
DEFAULT_BATCH_SIZE = 32
DEFAULT_LEARNING_RATE = 0.001

# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

# Risk score is normalized to [0, 100].
RISK_SCORE_MIN = 0.0
RISK_SCORE_MAX = 100.0

# Confidence is normalized to [0, 1].
CONFIDENCE_MIN = 0.0
CONFIDENCE_MAX = 1.0

# Default operational thresholds.
DEFAULT_REVIEW_THRESHOLD = 40.0
DEFAULT_SUSPICIOUS_THRESHOLD = 65.0
DEFAULT_QUARANTINE_THRESHOLD = 80.0

# ---------------------------------------------------------------------------
# Layer 0 — Local Validation
# ---------------------------------------------------------------------------

DEFAULT_MAX_UPDATE_NORM = 100.0
DEFAULT_MAX_PARAMETER_COUNT = 10_000_000

# ---------------------------------------------------------------------------
# Layer 1 — Fingerprinting
# ---------------------------------------------------------------------------

DEFAULT_FINGERPRINT_DIMENSION = 128
DEFAULT_RANDOM_PROJECTION_SEED = 42

# ---------------------------------------------------------------------------
# Layer 2 — Anomaly Detection
# ---------------------------------------------------------------------------

DEFAULT_ANOMALY_Z_SCORE = 3.0
DEFAULT_MIN_PEER_COUNT = 3

# ---------------------------------------------------------------------------
# Layer 3 — Influence
# ---------------------------------------------------------------------------

DEFAULT_INFLUENCE_SAMPLE_SIZE = 5
DEFAULT_INFLUENCE_MAX_CLIENTS = 20

# ---------------------------------------------------------------------------
# Layer 4 — Counterfactual
# ---------------------------------------------------------------------------

DEFAULT_COUNTERFACTUAL_TRIALS = 5
DEFAULT_COUNTERFACTUAL_PERTURBATION = 0.05

# ---------------------------------------------------------------------------
# Layer 5 — Attribution
# ---------------------------------------------------------------------------

DEFAULT_HISTORY_WINDOW = 10

# ---------------------------------------------------------------------------
# Trust Engine
# ---------------------------------------------------------------------------

# Evidence weights.
TRUST_ANOMALY_WEIGHT = 0.30
TRUST_INFLUENCE_WEIGHT = 0.20
TRUST_ROBUSTNESS_WEIGHT = 0.15
TRUST_HISTORY_WEIGHT = 0.15
TRUST_INTEGRITY_WEIGHT = 0.20

# ---------------------------------------------------------------------------
# Storage / Artifacts
# ---------------------------------------------------------------------------

ALLOWED_ARTIFACT_EXTENSIONS = {
    ".safetensors",
    ".npz",
}

BLOCKED_ARTIFACT_EXTENSIONS = {
    ".pt",
    ".pth",
    ".pkl",
    ".pickle",
}

# Maximum artifact size accepted by the prototype.
MAX_ARTIFACT_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB

# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

WEBSOCKET_HEARTBEAT_SECONDS = 30

# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

DEMO_CLIENT_COUNT = 20
DEMO_COMPROMISED_CLIENT_ID = "H3"

DEMO_DATASET = "MNIST"

# Important:
# This identifies the intended compromised client in the demo scenario.
# Detection logic MUST NOT use this value to automatically classify a client.