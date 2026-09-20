from typing import Any


def analyze_waste(
    litter_count: int,
    severe_litter: bool = False,
    image_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Analyze litter/waste detection results.

    The litter_count and severe_litter values represent the
    output of an image-based detection model such as YOLO.
    """

    image_count = 0
    if image_analysis:
        image_count = int(image_analysis.get("approximate_detected_litter_count", 0))

    effective_litter_count = max(litter_count, image_count)

    if severe_litter or effective_litter_count >= 20:
        risk_level = "HIGH"
        score = 90
        recommended_action = "Prioritize waste cleanup and inspection."

    elif effective_litter_count >= 5:
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
                "effective_litter_count": effective_litter_count,
                "image_analysis": image_analysis,
            }
        ],
        "confidence": 1.0,
        "recommended_action": recommended_action,
        "image_analysis": image_analysis,
    }
