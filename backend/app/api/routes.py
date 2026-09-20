from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.app.agents.coordinator import eco_graph
from backend.app.schemas import EnvironmentalRequest
from backend.app.services.image_analysis import (
    MAX_IMAGE_BYTES,
    ImageAnalysisError,
    analyze_image_bytes,
)


router = APIRouter()


@router.get("/demo")
def demo():
    result = eco_graph.invoke(
        {
            "area": "Demo Area",
            "air_input": {
                "aqi": 187,
            },
            "water_input": {
                "ph": 6.2,
                "dissolved_oxygen": 3.5,
                "turbidity": 12,
            },
            "waste_input": {
                "litter_count": 25,
                "severe_litter": True,
            },
        }
    )

    return result["final_report"]


@router.post("/analyze")
def analyze_environment(request: EnvironmentalRequest):

    result = eco_graph.invoke(
        {
            "area": request.area,
            "air_input": {
                "aqi": request.air.aqi,
            },
            "water_input": {
                "ph": request.water.ph,
                "dissolved_oxygen": request.water.dissolved_oxygen,
                "turbidity": request.water.turbidity,
            },
            "waste_input": {
                "litter_count": request.waste.litter_count,
                "severe_litter": request.waste.severe_litter,
            },
        }
    )

    return result["final_report"]


@router.post("/analyze-image")
async def analyze_environment_image(
    area: str = Form(...),
    aqi: float = Form(..., ge=0),
    ph: float = Form(...),
    dissolved_oxygen: float = Form(..., ge=0),
    turbidity: float = Form(..., ge=0),
    litter_count: int = Form(..., ge=0),
    severe_litter: bool = Form(False),
    image: UploadFile = File(...),
):
    if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail="Use a JPEG, PNG, or WEBP image.")

    image_bytes = await image.read(MAX_IMAGE_BYTES + 1)
    try:
        image_analysis = analyze_image_bytes(image_bytes, image.filename)
    except ImageAnalysisError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = eco_graph.invoke(
        {
            "area": area,
            "air_input": {"aqi": aqi},
            "water_input": {
                "ph": ph,
                "dissolved_oxygen": dissolved_oxygen,
                "turbidity": turbidity,
            },
            "waste_input": {
                "litter_count": litter_count,
                "severe_litter": severe_litter,
                "image_analysis": image_analysis,
            },
        }
    )

    return result["final_report"]
