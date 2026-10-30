import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from services.risk_engine import assess_risk


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml-model",
    "model"
)


tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

model.eval()


INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"forget\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(me\s+)?(the\s+)?system\s+prompt",
    r"print\s+(the\s+)?system\s+prompt",
    r"override\s+(the\s+)?system",
    r"bypass\s+(the\s+)?security",
    r"disable\s+(the\s+)?security"
]


def preprocess_prompt(prompt):
    normalized = prompt.lower()
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def detect_prompt_injection(prompt):

    normalized_prompt = preprocess_prompt(prompt)

    matched_patterns = []

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, normalized_prompt):
            matched_patterns.append(pattern)

    rule_matches = len(matched_patterns)

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)

        probabilities = torch.softmax(
            outputs.logits,
            dim=1
        )

        prediction = torch.argmax(
            probabilities,
            dim=1
        ).item()

        ml_confidence = probabilities[0][prediction].item()

    if prediction == 1:
        ml_detected = True
    else:
        ml_detected = False

    rule_detected = rule_matches > 0

    if rule_detected and ml_detected:
        detected_by = "hybrid_detector"

    elif ml_detected:
        detected_by = "ml_detector"

    elif rule_detected:
        detected_by = "rule_based_detector"

    else:
        detected_by = "none"

    if rule_detected or ml_detected:

        classification = "malicious"

        if rule_matches >= 2:
            risk_score = 95

        elif rule_matches == 1:
            risk_score = 75

        else:
            risk_score = 80

    else:

        classification = "benign"
        risk_score = 5

    risk_result = assess_risk(risk_score)

    return {
        "classification": classification,
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "decision": risk_result["decision"],
        "matched_rules": rule_matches,
        "detected_by": detected_by,
        "ml_confidence": round(ml_confidence, 4)
    }