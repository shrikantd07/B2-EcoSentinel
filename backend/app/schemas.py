from pydantic import BaseModel, Field


class AirInput(BaseModel):
    aqi: float = Field(..., ge=0)


class WaterInput(BaseModel):
    ph: float
    dissolved_oxygen: float = Field(..., ge=0)
    turbidity: float = Field(..., ge=0)


class WasteInput(BaseModel):
    litter_count: int = Field(..., ge=0)
    severe_litter: bool = False


class EnvironmentalRequest(BaseModel):
    area: str
    air: AirInput
    water: WaterInput
    waste: WasteInput