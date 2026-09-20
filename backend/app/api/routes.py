from fastapi import APIRouter

from backend.app.agents.coordinator import eco_graph
from backend.app.schemas import EnvironmentalRequest


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