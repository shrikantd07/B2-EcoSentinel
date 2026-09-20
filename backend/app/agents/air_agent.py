def analyze_air(aqi: float) -> dict:
    """
    Analyze air quality using AQI.

    Returns a standardized specialist-agent report.
    """

    if aqi <= 50:
        risk_level = "LOW"
    elif aqi <= 100:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    if risk_level == "LOW":
        score = 20
        action = "Continue routine environmental monitoring."
    elif risk_level == "MEDIUM":
        score = 50
        action = "Increase air-quality monitoring."
    else:
        score = 90
        action = "Prioritize air-quality inspection."

    return {
        "agent": "air",
        "risk_level": risk_level,
        "score": score,
        "finding": "Air quality analysis completed.",
        "evidence": [
            {
                "type": "aqi_measurement",
                "value": aqi,
            }
        ],
        "confidence": 1.0,
        "recommended_action": action,
    }