"""
Qiwa Shield — Pydantic request/response schemas.
"""
from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class EmployeeUploadSchema(BaseModel):
    ref_id: str = ""
    employee_name: str = Field(..., min_length=1, max_length=200)
    employee_name_ar: str = ""
    iqama_number: str = ""
    nationality: str = "Saudi Arabia"
    is_saudi: bool = True
    basic_salary: float = 0
    total_gross_wage: float = 0
    job_title: str = ""
    ssco_code: str = ""
    hire_date: Optional[str] = None
    contract_end_date: Optional[str] = None
    contract_documented_in_qiwa: bool = False
    gosi_enrolled: bool = False
    monthly_hours: int = 0
    housing_allowance: float = 0


class BatchUploadRequest(BaseModel):
    company_name: str = ""
    employees: list[EmployeeUploadSchema]


class SimulateRequest(BaseModel):
    scan_id: str = ""
    add_saudi: int = Field(default=0, ge=0)
    add_saudi_documented: bool = True
    increase_salaries_for: list[str] = []


class ReportRequest(BaseModel):
    scan_id: str = ""
    company_name: str = ""
    company_logo_url: Optional[str] = None