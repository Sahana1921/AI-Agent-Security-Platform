from flask import Blueprint, request, jsonify

from services.prompt_detector import detect_prompt_injection
from database import save_security_event


prompt_bp = Blueprint("prompt", __name__)


@prompt_bp.route("/analyze", methods=["POST"])
def analyze_prompt():

    data = request.get_json()

    prompt = data.get("prompt", "").strip()

    if not prompt:

        return jsonify({
            "status": "error",
            "message": "Prompt is required"
        }), 400


    result = detect_prompt_injection(prompt)


    save_security_event(
        prompt=prompt,
        classification=result["classification"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        decision=result["decision"],
        matched_rules=result["matched_rules"],
        detected_by=result["detected_by"],
        ml_confidence=result["ml_confidence"]
    )


    return jsonify({

        "status": "success",

        "prompt": prompt,

        "classification": result["classification"],

        "risk_score": result["risk_score"],

        "risk_level": result["risk_level"],

        "decision": result["decision"],

        "matched_rules": result["matched_rules"],

        "detected_by": result["detected_by"],

        "ml_confidence": result["ml_confidence"]

    })