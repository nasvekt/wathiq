export interface User {
  id: string;
  email: string;
  name: string;
  company_id: string;
  plan_tier: string;
}

export interface Employee {
  id: string;
  iqama: string;
  name_en: string;
  name_ar: string;
  nationality: string;
  job_title: string;
  ssco_code: string;
  basic_salary: number;
  housing_allowance: number;
  gross_salary: number;
  gender: 'male' | 'female';
  birth_date: string;
  iqama_expiry: string;
  contract_start: string;
  contract_end: string;
  gosi_enrolled: boolean;
  wps_registered: boolean;
  nitaqat_weight: number;
  status: ComplianceStatus;
  flags: string[];
}

export type ComplianceStatus = 'ready' | 'review' | 'blocked' | 'at_risk' | 'pending';

export interface ComplianceRecord {
  employee_id: string;
  engine: string;
  status: ComplianceStatus;
  detail: string;
  timestamp: string;
}

export interface ComplianceSummary {
  total_employees: number;
  ready_count: number;
  review_count: number;
  blocked_count: number;
  at_risk_count: number;
  pending_count: number;
  health_score: number;
  nitaqat_band: NitaqatBand;
  nitaqat_percentage: number;
  penalty_exposure: number;
  saudi_count: number;
  expat_count: number;
}

export type NitaqatBand = 'platinum' | 'high_green' | 'low_green' | 'yellow' | 'red';

export interface HealthScoreData {
  score: number;
  previous_score: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
  breakdown: {
    gosi: number;
    wps: number;
    nitaqat: number;
    iqama: number;
    contracts: number;
  };
}

export interface TransactionResult {
  transaction_id: string;
  processed_at: string;
  engine_version: string;
  rules_version: string;
  total_processed: number;
  results: ComplianceRecord[];
}

export interface ApiError {
  detail: string;
  transaction_id?: string;
  code?: string;
}