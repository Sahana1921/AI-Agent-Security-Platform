from flask import Blueprint, jsonify
from database import get_all_events

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/stats", methods=["GET"])
def dashboard_stats():

    events = get_all_events()

    total_prompts = len(events)

    malicious_detected = sum(
        1 for event in events
        if event["classification"].lower() == "malicious"
    )

    safe_prompts = sum(
        1 for event in events
        if event["classification"].lower() == "benign"
    )

    suspicious = sum(
        1 for event in events
        if 31 <= event["risk_score"] <= 80
    )

    return jsonify({
        "total_prompts": total_prompts,
        "malicious_detected": malicious_detected,
        "safe_prompts": safe_prompts,
        "suspicious": suspicious
    })


@dashboard_bp.route("/threats", methods=["GET"])
def threat_overview():

    events = get_all_events()

    safe = sum(
        1 for event in events
        if event["classification"].lower() == "benign"
    )

    malicious = sum(
        1 for event in events
        if event["classification"].lower() == "malicious"
    )

    suspicious = sum(
        1 for event in events
        if 31 <= event["risk_score"] <= 80
    )

    return jsonify({
        "safe": safe,
        "malicious": malicious,
        "suspicious": suspicious
    })


@dashboard_bp.route("/risk-distribution", methods=["GET"])
def risk_distribution():

    events = get_all_events()

    return jsonify({
        "0-30": sum(
            1 for event in events
            if 0 <= event["risk_score"] <= 30
        ),
        "31-60": sum(
            1 for event in events
            if 31 <= event["risk_score"] <= 60
        ),
        "61-80": sum(
            1 for event in events
            if 61 <= event["risk_score"] <= 80
        ),
        "81-100": sum(
            1 for event in events
            if 81 <= event["risk_score"] <= 100
        )
    })


@dashboard_bp.route("/recent-prompts", methods=["GET"])
def recent_prompts():

    events = get_all_events()

    result = []

    for event in events[:10]:

        result.append({
            "id": event["id"],
            "prompt": event["prompt"],
            "classification": event["classification"].upper(),
            "risk_score": event["risk_score"],
            "risk_level": event["risk_level"],
            "action": event["decision"],
            "time": event["created_at"]
        })

    return jsonify(result)


@dashboard_bp.route("/alerts", methods=["GET"])
def recent_alerts():

    events = get_all_events()

    alerts = []

    for event in events:

        if event["risk_score"] > 30:

            alerts.append({
                "title": "Security threat detected",
                "prompt": event["prompt"],
                "risk_score": event["risk_score"],
                "severity": event["risk_level"],
                "time": event["created_at"]
            })

    return jsonify(alerts[:10])


@dashboard_bp.route("/logs", methods=["GET"])
def system_logs():

    events = get_all_events()

    logs = []

    for event in events[:10]:

        logs.append({
            "time": event["created_at"],
            "message": (
                f"Prompt classified as "
                f"{event['classification'].upper()} | "
                f"Risk: {event['risk_score']} | "
                f"Action: {event['decision']}"
            )
        })

    return jsonify(logs)