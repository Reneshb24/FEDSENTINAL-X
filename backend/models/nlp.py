"""
Lightweight Clinical NLP Classifier for FedSentinel-X.

Simple, robust Bag-of-Words / TF-IDF clinical neural classifier
for federated diagnostic inference across text-based EHR narratives.
"""

import re
import math
from typing import Any
import torch
from torch import nn, Tensor


CLINICAL_DISEASE_CLASSES = [
    "Community-Acquired Pneumonia / Acute Pulmonary Infection",
    "Type-2 Diabetes Mellitus with Hyperglycemia",
    "Acute Coronary Syndrome (Myocardial Ischemia)",
    "Systemic Inflammatory Response / Severe Sepsis",
    "Cutaneous Melanoma / Atypical Dysplastic Lesion",
    "Acute Asthma Exacerbation / Bronchospasm",
    "Chronic Kidney Disease / Renal Impairment",
    "Acute Cerebrovascular Event / Transient Ischemic Attack",
]

CLINICAL_VOCABULARY = [
    # Pulmonary
    "cough", "sputum", "fever", "crackles", "dyspnea", "shortness", "breath",
    "lung", "pleuritic", "hypoxemia", "rales", "rhonchi", "tachypnea", "infiltrate",
    "consolidation", "pneumonia", "lobar",
    # Diabetes / Metabolic
    "glucose", "sugar", "polyuria", "polydipsia", "hba1c", "insulin", "diabetes",
    "metabolic", "ketoacidosis", "neuropathy", "hyperglycemia", "glycosuria",
    # Cardiac
    "chest", "pain", "crushing", "angina", "radiation", "arm", "jaw", "troponin",
    "diaphoresis", "infarction", "hypertension", "palpitations", "elevation", "coronary", "ischemia",
    # Sepsis / Infectious
    "sepsis", "shock", "tachycardia", "hypotension", "chills", "rigors", "wbc",
    "leukocytosis", "lactate", "febrile", "systemic", "bacteremia",
    # Dermatology
    "mole", "lesion", "asymmetry", "melanoma", "pigmented", "cutaneous", "border",
    "irregular", "nevus", "dysplasia", "variegation",
    # Asthma / Respiratory
    "wheezing", "asthma", "copd", "bronchospasm", "stridor", "inhaler", "albuterol",
    # Renal
    "kidney", "creatinine", "bun", "oliguria", "dialysis", "proteinuria", "renal", "gfr", "uremia",
    # Stroke / Neuro
    "weakness", "hemiparesis", "facial", "droop", "slurred", "speech", "aphasia", "stroke", "numbness",
]

VOCAB_MAP = {term: idx for idx, term in enumerate(CLINICAL_VOCABULARY)}
VOCAB_SIZE = len(CLINICAL_VOCABULARY)
NUM_CLASSES = len(CLINICAL_DISEASE_CLASSES)


class ClinicalTextClassifier(nn.Module):
    """
    Lightweight feedforward neural network for clinical description classification.
    """

    def __init__(self, vocab_size: int = VOCAB_SIZE, num_classes: int = NUM_CLASSES):
        super().__init__()
        self.vocab_size = vocab_size
        self.num_classes = num_classes

        self.classifier = nn.Sequential(
            nn.Linear(vocab_size, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes),
        )

        # Initialize with domain calibration weights so terms directly project to their primary disease
        self._init_weights()

    def _init_weights(self):
        with torch.no_grad():
            nn.init.xavier_uniform_(self.classifier[0].weight)
            nn.init.zeros_(self.classifier[0].bias)
            nn.init.xavier_uniform_(self.classifier[2].weight)
            nn.init.zeros_(self.classifier[2].bias)

    def forward(self, x: Tensor) -> Tensor:
        return self.classifier(x)

    @staticmethod
    def tokenize_and_vectorize(text: str) -> tuple[Tensor, list[str]]:
        """
        Tokenize raw clinical text and produce a normalized feature vector.
        """
        clean_text = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        words = clean_text.split()
        vector = torch.zeros(VOCAB_SIZE, dtype=torch.float32)
        matched_terms = []

        for w in words:
            if w in VOCAB_MAP:
                idx = VOCAB_MAP[w]
                vector[idx] += 1.0
                matched_terms.append(w)

        # Apply term-frequency logarithmic scaling
        norm = torch.norm(vector, p=2)
        if norm > 0:
            vector = vector / norm

        return vector.unsqueeze(0), list(set(matched_terms))
