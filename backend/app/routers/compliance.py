"""
Compliance validation endpoints.
POST /api/v1/validate/compliance — Main validation endpoint.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.compliance import (
    ComplianceValidationRequest,
    ComplianceValidationResponse,
)
from app.engines.compliance_engine import validate_batch

router = APIRouter()


@router.post("/validate/compliance", response_model=ComplianceValidationResponse)
async def validate_compliance(request: ComplianceValidationRequest):
    """
    Validate a batch of employee records against all Saudi compliance rules.

    Runs all 10 compliance engines:
    1. Iqama/National ID format validation
    2. Nitaqat weight calculation
    3. Nitaqat target matrix (sector × size)
    4. WPS salary floor & variance
    5. Housing allowance parity
    6. GOSI pension contribution
    7. Expatriate diversity cap
    8. Saudi engineer wage floor
    9. Qiwa contract window
    10. Iqama expiry monitoring

    Returns per-employee status (ready/review/blocked) and company-wide analytics.
    """
    try:
        result = validate_batch(
            employees=request.records,
            sector_code=request.company_sector_code,
            size_category=request.company_size_category,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")
