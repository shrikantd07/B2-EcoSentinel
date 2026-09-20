from typing import Any


def analyze_waste(
    litter_count: int,
    severe_litter: bool = False,
) -> dict[str, Any]:
    """
    Analyze litter/waste detection results.

    The litter_count and severe_litter values represent the
    output of an image-based detection model such as YOLO.
    """

    if severe_litter or litter_count >= 20:
        risk_level = "HIGH"
        score = 90
        recommended_action = "Prioritize waste cleanup and inspection."

    elif litter_count >= 5:
        risk_level = "MEDIUM"
        score = 50
        recommended_action = "Schedule waste cleanup and continue monitoring."

    else:
        risk_level = "LOW"
        score = 10
        recommended_action = "Continue routine waste monitoring."

    return {
        "agent": "waste",
        "risk_level": risk_level,
        "score": score,
        "finding": "Waste/litter image analysis completed.",
        "evidence": [
            {
                "type": "litter_detection",
                "litter_count": litter_count,
                "severe_litter": severe_litter,
            }
        ],
        "confidence": 1.0,
        "recommended_action": recommended_action,
    }