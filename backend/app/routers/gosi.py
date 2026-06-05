"""
Wathiq — GOSI calculation endpoint.
POST /api/v1/validate/gosi
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date
from typing import Optional
from app.engines.gosi_engine import calculate_gosi_contribution

router = APIRouter()


class GOSIRequest(BaseModel):
    nationality: str = Field(..., min_length=1)
    date_of_birth: Optional[date] = None
    gosi_enrollment_date: Optional[date] = None
    basic_salary: Decimal = Field(..., ge=0)
    housing_allowance: Decimal = Field(default=Decimal("0.00"), ge=0)


@router.post("/validate/gosi")
async def validate_gosi(request: GOSIRequest):
    """Standalone GOSI calculation. Returns scheme, rate, employer/employee contributions."""
    try:
        result = calculate_gosi_contribution(
            nationality=request.nationality,
            basic_salary=request.basic_salary,
            housing_allowance=request.housing_allowance,
            date_of_birth=request.date_of_birth,
            gosi_enrollment_date=request.gosi_enrollment_date,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GOSI calculation error: {str(e)}")
