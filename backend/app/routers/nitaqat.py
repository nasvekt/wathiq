"""
Wathiq — Nitaqat simulation endpoint.
POST /api/v1/simulate/nitaqat
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from app.engines.nitaqat_engine import calculate_saudization_ratio, classify_nitaqat_band

router = APIRouter()


class NitaqatSimulationRequest(BaseModel):
    current_saudi_weight: Decimal = Field(..., ge=0)
    current_total_employees: int = Field(..., ge=1)
    add_saudi: int = Field(default=0, ge=0)
    add_part_time_saudi_hours: Optional[int] = None
    remove_expat: int = Field(default=0, ge=0)
    sector_code: str = Field(..., min_length=1)
    size_category: str = Field(..., min_length=1)


@router.post("/simulate/nitaqat")
async def simulate_nitaqat(request: NitaqatSimulationRequest):
    """
    Simulate workforce changes and see projected Nitaqat band impact.
    Returns current/projected ratio, band, and warning if band drop occurs.
    """
    try:
        # Current state
        current_ratio = calculate_saudization_ratio(
            total_employees=request.current_total_employees,
            saudi_weights_sum=request.current_saudi_weight,
        )

        # Projected state
        add_saudi_weight = Decimal(str(request.add_saudi))
        new_total = request.current_total_employees + request.add_saudi - request.remove_expat
        new_saudi_weight = request.current_saudi_weight + add_saudi_weight

        # Add part-time Saudi if 160+ hours
        if request.add_part_time_saudi_hours and request.add_part_time_saudi_hours >= 160:
            new_saudi_weight += Decimal(str(request.add_saudi or 0))

        if new_total <= 0:
            raise HTTPException(status_code=400, detail="Projected workforce would be empty")

        projected_ratio = calculate_saudization_ratio(
            total_employees=new_total,
            saudi_weights_sum=new_saudi_weight,
        )

        # Classify bands using sector x size matrix from engine
        current_band = classify_nitaqat_band(
            current_ratio, request.sector_code, request.size_category
        )
        projected_band = classify_nitaqat_band(
            projected_ratio, request.sector_code, request.size_category
        )

        band_priority = {"red": 0, "yellow": 1, "low_green": 2, "high_green": 3, "platinum": 4}
        band_drop = band_priority.get(projected_band, 0) < band_priority.get(current_band, 0)

        return {
            "current_ratio": float(current_ratio),
            "current_band": current_band,
            "projected_ratio": float(projected_ratio),
            "projected_band": projected_band,
            "band_drop_warning": band_drop,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")
