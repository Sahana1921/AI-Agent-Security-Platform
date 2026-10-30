def assess_risk(risk_score):
    if risk_score <= 30:
        risk_level = "LOW"
        decision = "ALLOW"

    elif risk_score <= 60:
        risk_level = "MEDIUM"
        decision = "WARN"

    elif risk_score <= 80:
        risk_level = "HIGH"
        decision = "REQUIRE VERIFICATION"

    else:
        risk_level = "CRITICAL"
        decision = "BLOCK"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision
    }