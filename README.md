# FedSentinel

## The Security Control Plane for Federated AI

FedSentinel analyzes model updates submitted by distributed
federated-learning clients and detects poisoned, anomalous,
or potentially backdoored contributions.

## Core Principle

> DON'T TRUST THE UPDATE. VERIFY IT.

## Security Pipeline

20 Distributed Clients
        ↓
L0 Local Validation
        ↓
L1 Privacy-Safe Update Fingerprint
        ↓
L2 Robust Anomaly Detection
        ↓
Quarantine / Robust Aggregation
        ↓
L3 Influence Testing
        ↓
L4 Counterfactual Testing
        ↓
L5 Client Attribution
        ↓
Trust Engine
        ↓
Safe Global Model

## Demonstration Environment

- Dataset: MNIST
- Model: Lightweight CNN
- Clients: 20 simulated clients
- Distribution: Non-IID
- Benign clients: 19
- Compromised client: 1
- Attack: Targeted backdoor
- Detection: Independent multi-layer analysis

## Security Philosophy

RISK != VERDICT

FedSentinel separates:

1. Observations
2. Evidence
3. Risk
4. Confidence
5. Threat hypothesis
6. Recommended action
7. Final decision

## Development

The project is being developed from the backend foundation upward.

VS Code is the source of truth for implementation.

Visual exploration may use Stitch and Google AI Studio,
but generated code is reviewed and integrated manually.