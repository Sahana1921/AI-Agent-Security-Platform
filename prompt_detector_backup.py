import re


# Common prompt-injection patterns
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
    r"disable\s+(the\s+)?security",
]


def preprocess_prompt(prompt):
    """
    Basic prompt normalization.
    """

    # Convert to lowercase
    normalized = prompt.lower()

    # Remove extra spaces
    normalized = re.sub(r"\s+", " ", normalized).strip()

    return normalized


def detect_prompt_injection(prompt):
    """
    Rule-based prompt injection detector.
    """

    normalized_prompt = preprocess_prompt(prompt)

    matched_patterns = []

    for pattern in INJECTION_PATTERNS:

        if re.search(pattern, normalized_prompt):
            matched_patterns.append(pattern)

    # Calculate risk
    number_of_matches = len(matched_patterns)

    if number_of_matches >= 2:
        classification = "malicious"
        risk_score = 95
        risk_level = "HIGH"

    elif number_of_matches == 1:
        classification = "suspicious"
        risk_score = 75
        risk_level = "MEDIUM"

    else:
        classification = "benign"
        risk_score = 5
        risk_level = "LOW"

    return {
        "classification": classification,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "matched_rules": len(matched_patterns),
        "detected_by": "rule_based_detector"
    }