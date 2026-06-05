-- Wathiq Database Migration 001: Initial Schema
-- All tables, enums, indexes, and RLS policies
-- Matches blueprint Section 17 exactly

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Enums ──
CREATE TYPE compliance_status_enum AS ENUM ('ready', 'review', 'blocked', 'at_risk', 'pending');
CREATE TYPE audit_batch_status_enum AS ENUM ('processing', 'complete', 'failed');
CREATE TYPE gosi_scheme_enum AS ENUM ('legacy', 'progressive');
CREATE TYPE nitaqat_band_enum AS ENUM ('platinum', 'high_green', 'low_green', 'yellow', 'red');
CREATE TYPE plan_tier_enum AS ENUM ('standard', 'professional', 'enterprise', 'developer');
CREATE TYPE sif_status_enum AS ENUM ('pending', 'validated', 'exported', 'failed');

── Companies ──
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    name_ar TEXT,
    commercial_registration TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    economic_sector_code TEXT NOT NULL,
    establishment_size_category TEXT,
    total_headcount INTEGER DEFAULT 0,
    plan_tier TEXT DEFAULT 'standard',
    plan_expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    onboarding_complete BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

── Compliance Rules ──
CREATE TABLE compliance_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_key TEXT NOT NULL,
    rule_category TEXT NOT NULL,
    sector_code TEXT,
    size_category TEXT,
    parameter_value DECIMAL(12,4),
    parameter_text TEXT,
    effective_from DATE NOT NULL,
    effective_until DATE,
    bilingual_circular_citation TEXT,
    source_url TEXT,
    approved_by TEXT,
    approved_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(rule_key, sector_code, size_category, effective_from)
);

── Pending Rule Updates ──
CREATE TABLE pending_rule_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_key TEXT NOT NULL,
    detected_value DECIMAL(12,4),
    detected_text TEXT,
    effective_from DATE,
    source_document_url TEXT,
    ai_confidence DECIMAL(4,3),
    ai_justification TEXT,
    status TEXT DEFAULT 'pending',
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

── API Keys ──
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    key_hash TEXT UNIQUE NOT NULL,
    key_prefix TEXT NOT NULL,
    is_sandbox BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

── Audit Batches ──
CREATE TABLE audit_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    batch_reference TEXT NOT NULL,
    payroll_period TEXT NOT NULL,
    source_filename TEXT,
    total_records INTEGER DEFAULT 0,
    ready_count INTEGER DEFAULT 0,
    review_count INTEGER DEFAULT 0,
    blocked_count INTEGER DEFAULT 0,
    saudization_ratio DECIMAL(5,2),
    nitaqat_band TEXT,
    total_gosi_liability DECIMAL(12,2),
    penalty_exposure DECIMAL(12,2),
    company_health_score INTEGER,
    engine_version TEXT,
    rules_version TEXT,
    sif_file_url TEXT,
    passport_pdf_url TEXT,
    status TEXT DEFAULT 'processing',
    file_content_hash TEXT,
    idempotency_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    UNIQUE(company_id, batch_reference),
    UNIQUE(file_content_hash)
);

── Employee Records ──
CREATE TABLE employee_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    batch_id UUID REFERENCES audit_batches(id) ON DELETE CASCADE,
    ref_id TEXT,
    employee_name TEXT NOT NULL,
    iqama_number TEXT,
    iqama_expiry_date DATE,
    nationality TEXT,
    date_of_birth DATE,
    gosi_enrollment_date DATE,
    hire_date DATE,
    raw_job_title TEXT,
    ssco_code TEXT,
    ssco_title_en TEXT,
    ssco_title_ar TEXT,
    ssco_confidence DECIMAL(4,3),
    is_engineer BOOLEAN DEFAULT false,
    basic_salary DECIMAL(12,2),
    housing_allowance DECIMAL(12,2),
    transport_allowance DECIMAL(12,2),
    other_allowances DECIMAL(12,2),
    monthly_hours INTEGER,
    total_gross_wage DECIMAL(12,2),
    gosi_base DECIMAL(12,2),
    gosi_scheme TEXT,
    gosi_rate DECIMAL(5,4),
    gosi_deduction DECIMAL(12,2),
    employer_gosi DECIMAL(12,2),
    employee_gosi DECIMAL(12,2),
    nitaqat_weight DECIMAL(3,1),
    wage_floor_applied TEXT,
    qiwa_contract_days_elapsed INTEGER,
    qiwa_contract_flag TEXT DEFAULT 'unknown',
    compliance_status TEXT DEFAULT 'pending',
    flags JSONB DEFAULT '[]',
    corrections JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

── SSCO Dictionary ──
CREATE TABLE ssco_dictionary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_title TEXT NOT NULL,
    raw_title_normalized TEXT NOT NULL,
    ssco_code TEXT NOT NULL,
    title_en TEXT NOT NULL,
    title_ar TEXT NOT NULL,
    is_engineering_code BOOLEAN DEFAULT false,
    confidence DECIMAL(4,3),
    approved BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(raw_title_normalized, ssco_code)
);

── API Usage Log ──
CREATE TABLE api_usage_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    api_key_id UUID REFERENCES api_keys(id),
    endpoint TEXT NOT NULL,
    records_processed INTEGER DEFAULT 0,
    engine_version TEXT,
    rules_version TEXT,
    latency_ms INTEGER,
    status_code INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

── Iqama Expiry Tracker ──
CREATE TABLE iqama_tracker (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    employee_name TEXT NOT NULL,
    iqama_number TEXT NOT NULL,
    expiry_date DATE NOT NULL,
    alert_sent_90 BOOLEAN DEFAULT false,
    alert_sent_60 BOOLEAN DEFAULT false,
    alert_sent_30 BOOLEAN DEFAULT false,
    alert_sent_7 BOOLEAN DEFAULT false,
    renewed BOOLEAN DEFAULT false,
    renewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

── Contract Tracker ──
CREATE TABLE contract_tracker (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    employee_name TEXT NOT NULL,
    iqama_number TEXT NOT NULL,
    hire_date DATE NOT NULL,
    deadline_date DATE NOT NULL,
    alert_sent_day_25 BOOLEAN DEFAULT false,
    alert_sent_day_30 BOOLEAN DEFAULT false,
    contract_published BOOLEAN DEFAULT false,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

── Audit Trail (append-only) ──
CREATE TABLE audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    actor_email TEXT,
    action TEXT NOT NULL,
    description TEXT,
    input_data_hash TEXT,
    rules_version_applied TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

── Indexes ──
CREATE INDEX idx_audit_batches_company ON audit_batches(company_id);
CREATE INDEX idx_employees_org_id ON employee_records(company_id);
CREATE INDEX idx_compliance_history_lookup ON employee_records(company_id, compliance_status);
CREATE UNIQUE INDEX idx_unique_active_identity ON employee_records(company_id, iqama_number)
    WHERE compliance_status != 'blocked';
CREATE INDEX idx_employee_records_company ON employee_records(company_id);
CREATE INDEX idx_employee_records_batch ON employee_records(batch_id);
CREATE INDEX idx_compliance_rules_key ON compliance_rules(rule_key, effective_from);
CREATE INDEX idx_iqama_tracker_expiry ON iqama_tracker(expiry_date, renewed);
CREATE INDEX idx_contract_tracker_deadline ON contract_tracker(deadline_date, contract_published);

── Row-Level Security ──
ALTER TABLE audit_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE iqama_tracker ENABLE ROW LEVEL SECURITY;
ALTER TABLE contract_tracker ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_trail ENABLE ROW LEVEL SECURITY;

CREATE POLICY company_isolation_batches ON audit_batches
    FOR ALL USING (company_id = (auth.jwt() ->> 'company_id')::UUID);
CREATE POLICY company_isolation_employees ON employee_records
    FOR ALL USING (company_id = (auth.jwt() ->> 'company_id')::UUID);
CREATE POLICY company_isolation_keys ON api_keys
    FOR ALL USING (company_id = (auth.jwt() ->> 'company_id')::UUID);
CREATE POLICY company_isolation_iqama ON iqama_tracker
    FOR ALL USING (company_id = (auth.jwt() ->> 'company_id')::UUID);
CREATE POLICY company_isolation_contracts ON contract_tracker
    FOR ALL USING (company_id = (auth.jwt() ->> 'company_id')::UUID);
