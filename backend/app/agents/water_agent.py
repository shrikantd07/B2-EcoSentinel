from typing import Any


def analyze_water(
    ph: float,
    dissolved_oxygen: float,
    turbidity: float,
) -> dict[str, Any]:
    """
    Analyze basic water-quality indicators and return
    a standardized specialist-agent report.
    """

    findings = []
    score = 0

    # pH
    if ph < 6.5 or ph > 8.5:
        score += 40
        findings.append(f"pH is outside the normal range: {ph}")
    else:
        findings.append(f"pH is within the normal range: {ph}")

    # Dissolved oxygen
    if dissolved_oxygen < 5:
        score += 35
        findings.append(
            f"Dissolved oxygen is low: {dissolved_oxygen} mg/L"
        )
    else:
        findings.append(
            f"Dissolved oxygen is acceptable: {dissolved_oxygen} mg/L"
        )

    # Turbidity
    if turbidity > 5:
        score += 25
        findings.append(f"Turbidity is high: {turbidity} NTU")
    else:
        findings.append(f"Turbidity is acceptable: {turbidity} NTU")

    # Risk classification
    if score >= 70:
        risk_level = "HIGH"
    elif score >= 35:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "agent": "water",
        "risk_level": risk_level,
        "score": score,
        "finding": "Water quality analysis completed.",
        "evidence": [
            {
                "type": "water_measurements",
                "ph": ph,
                "dissolved_oxygen": dissolved_oxygen,
                "turbidity": turbidity,
            }
        ],
        "details": findings,
        "confidence": 1.0,
        "recommended_action": (
            "Prioritize water-quality inspection."
            if risk_level == "HIGH"
            else "Continue water-quality monitoring."
        ),
    }