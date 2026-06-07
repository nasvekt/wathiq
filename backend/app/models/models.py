"""
Wathiq — SQLAlchemy 2.0 async models.
Maps to the blueprint's database schema.
"""
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, Date, Numeric, Text, Enum as SAEnum, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum


class Base(DeclarativeBase):
    pass


# ── Enums ──

class ComplianceStatus(str, enum.Enum):
    READY = "ready"
    REVIEW = "review"
    BLOCKED = "blocked"
    AT_RISK = "at_risk"
    PENDING = "pending"

class AuditBatchStatus(str, enum.Enum):
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"

class GOSIScheme(str, enum.Enum):
    LEGACY = "legacy"
    PROGRESSIVE = "progressive"
    EXPAT = "expat"

class NitaqatBand(str, enum.Enum):
    PLATINUM = "platinum"
    HIGH_GREEN = "high_green"
    LOW_GREEN = "low_green"
    RED = "red"

class PlanTier(str, enum.Enum):
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    DEVELOPER = "developer"

class SIFStatus(str, enum.Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    EXPORTED = "exported"
    FAILED = "failed"


# ── Models ──

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_ar: Mapped[str | None] = mapped_column(String(255))
    commercial_registration: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    economic_sector_code: Mapped[str] = mapped_column(String(20), nullable=False)
    establishment_size_category: Mapped[str | None] = mapped_column(String(20))
    total_headcount: Mapped[int] = mapped_column(default=0)
    plan_tier: Mapped[str] = mapped_column(String(20), default="standard")
    plan_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(default=True)
    onboarding_complete: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow())


class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    rule_key: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_category: Mapped[str] = mapped_column(String(50), nullable=False)
    sector_code: Mapped[str | None] = mapped_column(String(20))
    size_category: Mapped[str | None] = mapped_column(String(20))
    parameter_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    parameter_text: Mapped[str | None] = mapped_column(Text)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_until: Mapped[date | None] = mapped_column(Date)
    source_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow())

    __table_args__ = (
        UniqueConstraint("rule_key", "sector_code", "size_category", "effective_from"),
    )


class PendingRuleUpdate(Base):
    __tablename__ = "pending_rule_updates"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    rule_key: Mapped[str] = mapped_column(String(100), nullable=False)
    detected_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    detected_text: Mapped[str | None] = mapped_column(Text)
    effective_from: Mapped[date | None] = mapped_column(Date)
    source_document_url: Mapped[str | None] = mapped_column(String(500))
    ai_confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    ai_justification: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    reviewed_by: Mapped[str | None] = mapped_column(String(100))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow())


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(10), nullable=False)
    is_sandbox: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow())


class AuditBatch(Base):
    __tablename__ = "audit_batches"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    batch_reference: Mapped[str] = mapped_column(String(100), nullable=False)
    payroll_period: Mapped[str] = mapped_column(String(10), nullable=False)
    source_filename: Mapped[str | None] = mapped_column(String(255))
    total_records: Mapped[int] = mapped_column(default=0)
    ready_count: Mapped[int] = mapped_column(default=0)
    review_count: Mapped[int] = mapped_column(default=0)
    blocked_count: Mapped[int] = mapped_column(default=0)
    saudization_ratio: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    nitaqat_band: Mapped[str | None] = mapped_column(String(20))
    total_gosi_liability: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    penalty_exposure: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    company_health_score: Mapped[int | None] = mapped_column()
    engine_version: Mapped[str | None] = mapped_column(String(20))
    rules_version: Mapped[str | None] = mapped_column(String(20))
    sif_file_url: Mapped[str | None] = mapped_column(String(500))
    passport_pdf_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="processing")
    file_content_hash: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    company: Mapped["Company"] = relationship()
    employees: Mapped[list["EmployeeRecord"]] = relationship(back_populates="batch", cascade="all, delete-orphan")


class EmployeeRecord(Base):
    __tablename__ = "employee_records"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    batch_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("audit_batches.id", ondelete="CASCADE"), nullable=False)
    ref_id: Mapped[str | None] = mapped_column(String(100))
    employee_name: Mapped[str] = mapped_column(String(200), nullable=False)
    iqama_number: Mapped[str | None] = mapped_column(String(20))
    iqama_expiry_date: Mapped[date | None] = mapped_column(Date)
    nationality: Mapped[str | None] = mapped_column(String(100))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gosi_enrollment_date: Mapped[date | None] = mapped_column(Date)
    hire_date: Mapped[date | None] = mapped_column(Date)
    raw_job_title: Mapped[str | None] = mapped_column(String(200))
    ssco_code: Mapped[str | None] = mapped_column(String(10))
    ssco_title_en: Mapped[str | None] = mapped_column(String(200))
    ssco_title_ar: Mapped[str | None] = mapped_column(String(200))
    ssco_confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    is_engineer: Mapped[bool] = mapped_column(default=False)
    basic_salary: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    housing_allowance: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    transport_allowance: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    other_allowances: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    monthly_hours: Mapped[int | None] = mapped_column()
    total_gross_wage: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    gosi_base: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    gosi_scheme: Mapped[str | None] = mapped_column(String(20))
    gosi_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    gosi_deduction: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    employer_gosi: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    employee_gosi: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    nitaqat_weight: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    wage_floor_applied: Mapped[str | None] = mapped_column(String(30))
    qiwa_contract_days_elapsed: Mapped[int | None] = mapped_column()
    qiwa_contract_flag: Mapped[str] = mapped_column(String(20), default="unknown")
    compliance_status: Mapped[str] = mapped_column(String(20), default="pending")
    flags: Mapped[dict] = mapped_column(JSON, default=list)
    corrections: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow())

    batch: Mapped["AuditBatch"] = relationship(back_populates="employees")


class SSCODictionary(Base):
    __tablename__ = "ssco_dictionary"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    raw_title: Mapped[str] = mapped_column(String(200), nullable=False)
    raw_title_normalized: Mapped[str] = mapped_column(String(200), nullable=False)
    ssco_code: Mapped[str] = mapped_column(String(10), nullable=False)
    title_en: Mapped[str] = mapped_column(String(200), nullable=False)
    title_ar: Mapped[str] = mapped_column(String(200), nullable=False)
    is_engineering_code: Mapped[bool] = mapped_column(default=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    approved: Mapped[bool] = mapped_column(default=True)
    usage_count: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow())

    __table_args__ = (
        UniqueConstraint("raw_title_normalized", "ssco_code"),
    )


class IqamaTracker(Base):
    __tablename__ = "iqama_tracker"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    employee_name: Mapped[str] = mapped_column(String(200), nullable=False)
    iqama_number: Mapped[str] = mapped_column(String(20), nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    alert_sent_90: Mapped[bool] = mapped_column(default=False)
    alert_sent_60: Mapped[bool] = mapped_column(default=False)
    alert_sent_30: Mapped[bool] = mapped_column(default=False)
    alert_sent_7: Mapped[bool] = mapped_column(default=False)
    renewed: Mapped[bool] = mapped_column(default=False)
    renewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow())


class ContractTracker(Base):
    __tablename__ = "contract_tracker"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    employee_name: Mapped[str] = mapped_column(String(200), nullable=False)
    iqama_number: Mapped[str] = mapped_column(String(20), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    deadline_date: Mapped[date] = mapped_column(Date, nullable=False)
    alert_sent_day_25: Mapped[bool] = mapped_column(default=False)
    alert_sent_day_30: Mapped[bool] = mapped_column(default=False)
    contract_published: Mapped[bool] = mapped_column(default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow())


class AuditTrail(Base):
    __tablename__ = "audit_trail"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=False)
    actor_email: Mapped[str | None] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    input_data_hash: Mapped[str | None] = mapped_column(String(64))
    rules_version_applied: Mapped[str | None] = mapped_column(String(20))
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow())
