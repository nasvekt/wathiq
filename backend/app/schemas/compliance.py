"""
Pydantic v2 schemas for Wathiq API request/response validation.
Stage 2 deterministic guardrail — catches any data anomalies before
they reach the compliance engines.
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator


# ── Enums ──

class ComplianceStatus(str, Enum):
    READY = "ready"
    REVIEW = "review"
    BLOCKED = "blocked"
    AT_RISK = "at_risk"
    PENDING = "pending"

class GOSIScheme(str, Enum):
    LEGACY = "legacy"
    PROGRESSIVE = "progressive"
    EXPAT = "expat"

class NitaqatBand(str, Enum):
    PLATINUM = "platinum"
    HIGH_GREEN = "high_green"
    LOW_GREEN = "low_green"
    RED = "red"


# ── Input Schemas ──

class EmployeeInput(BaseModel):
    """Single employee record for compliance validation."""
    ref_id: str = Field(..., min_length=1, max_length=100, description="Employee reference ID")
    employee_name: str = Field(..., min_length=1, max_length=200)
    iqama_number: str = Field(..., min_length=1, max_length=20)
    iqama_expiry_date: Optional[date] = None
    nationality: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gosi_enrollment_date: Optional[date] = None
    hire_date: Optional[date] = None
    raw_job_title: Optional[str] = Field(None, max_length=200)
    ssco_code: Optional[str] = Field(None, max_length=10)
    basic_salary: Decimal = Field(..., ge=0, decimal_places=2)
    housing_allowance: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    transport_allowance: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    other_allowances: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    monthly_hours: Optional[int] = Field(None, ge=0, le=744)
    registered_gosi_contract_salary: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    contract_published: bool = False

    @field_validator("iqama_number")
    @classmethod
    def validate_iqama_format(cls, v: str) -> str:
        """Strip non-numeric characters and validate."""
        cleaned = "".join(c for c in v if c.isdigit())
        if len(cleaned) != 10:
            raise ValueError(f"Iqama/National ID must be exactly 10 digits, got {len(cleaned)}")
        if cleaned[0] not in ("1", "2"):
            raise ValueError(f"Iqama/National ID must start with 1 (Saudi) or 2 (Expat), got {cleaned[0]}")
        return cleaned

    @field_validator("employee_name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        """Strip commas (SIF requirement) and extra whitespace."""
        return v.replace(",", "").strip()

    @model_validator(mode="after")
    def validate_salary_positive(self):
        if self.basic_salary <= 0:
            raise ValueError("Basic salary must be greater than zero")
        return self


class ComplianceValidationRequest(BaseModel):
    """Request body for POST /api/v1/validate/compliance"""
    payroll_period: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="YYYY-MM format")
    company_sector_code: str = Field(default="technology", description="MHRSD Economic Activity Sector Code")
    company_size_category: str = Field(default="medium_a", description="Size category for Nitaqat matrix")
    strict_mode: bool = True
    records: list[EmployeeInput] = Field(..., min_length=1, max_length=10000)


# ── Output Schemas ──

class GOSIResult(BaseModel):
    gosi_wage_base: Decimal
    gosi_scheme: GOSIScheme
    gosi_rate: Decimal
    total_contribution: Decimal
    employer_contribution: Decimal
    employee_deduction: Decimal


class NitaqatResult(BaseModel):
    nitaqat_weight: Decimal
    wage_floor_applied: str


class ContractStatus(BaseModel):
    qiwa_days_elapsed: Optional[int]
    qiwa_contract_flag: str


class EmployeeResult(BaseModel):
    ref_id: str
    employee_name: str
    iqama_number: str
    status: ComplianceStatus
    ssco_classification: Optional[dict] = None
    financials: dict
    nationalization: NitaqatResult
    contract_status: ContractStatus
    flags: list[str]
    gosi: GOSIResult


class WorkforceAnalytics(BaseModel):
    saudization_ratio: Decimal
    nitaqat_band: NitaqatBand
    total_gosi_liability: Decimal
    expat_diversity: dict


class ComplianceSummary(BaseModel):
    total_processed: int
    ready_count: int
    review_count: int
    blocked_count: int
    company_health_score: int
    penalty_exposure: Decimal


class ComplianceValidationResponse(BaseModel):
    """Response body for POST /api/v1/validate/compliance"""
    success: bool
    transaction_id: str
    processed_at: str
    engine_version: str = "0.1.0"
    rules_version: str = "2026-05-01"
    summary: ComplianceSummary
    workforce_analytics: WorkforceAnalytics
    records: list[EmployeeResult]
