"""
Wathiq — SIF file generation endpoint.
POST /api/v1/export/sif
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from app.outputs.sif_builder import build_sif_file, validate_sif

router = APIRouter()


class SIFEmployee(BaseModel):
    national_id: str
    employee_name: str
    employee_iban: str
    basic_salary: Decimal = Field(..., ge=0)
    housing_allowance: Decimal = Field(default=Decimal("0"), ge=0)
    other_allowances: Decimal = Field(default=Decimal("0"), ge=0)
    gosi_deduction: Decimal = Field(default=Decimal("0"), ge=0)


class SIFExportRequest(BaseModel):
    establishment_id: str
    payer_iban: str
    payroll_period: str
    bank_code: str
    employees: list[SIFEmployee]


@router.post("/export/sif")
async def export_sif(request: SIFExportRequest):
    """Generate a bank-ready Mudad WPS SIF file."""
    try:
        if not request.employees:
            raise HTTPException(status_code=400, detail="No employees in request")

        employees_dict = [emp.model_dump() for emp in request.employees]
        sif_content, sha256_hash = build_sif_file(
            establishment_id=request.establishment_id,
            payer_iban=request.payer_iban,
            payroll_period=request.payroll_period,
            bank_code=request.bank_code,
            employees=employees_dict,
        )

        validation = validate_sif(sif_content)

        return {
            "success": len(validation) == 0,
            "sif_content": sif_content,
            "sha256_hash": sha256_hash,
            "row_count": len(request.employees),
            "validation_issues": validation if validation else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SIF export error: {str(e)}")
