export interface ComplianceDashboard {
  health_score: number;
  health_trend: 'up' | 'down' | 'stable';
  nitaqat_band: string;
  nitaqat_percentage: number;
  total_records: number;
  ready_count: number;
  review_count: number;
  blocked_count: number;
  at_risk_count: number;
  penalty_exposure: number;
  recent_activity: ComplianceActivity[];
  band_projection?: string;
}

export interface ComplianceActivity {
  id: string;
  type: string;
  message: string;
  timestamp: string;
  severity: 'info' | 'warning' | 'error';
}

export interface ComplianceFilter {
  search: string;
  status: string;
  nationality: string;
  nitaqat_weight: string;
  page: number;
  page_size: number;
}

export interface NitaqatSimParams {
  current_expat_count: number;
  current_saudi_count: number;
  target_expat_count: number;
  target_saudi_count: number;
  industry: string;
  region: string;
  company_size: string;
}

export interface NitaqatSimResult {
  current_band: string;
  projected_band: string;
  current_percentage: number;
  projected_percentage: number;
  saudis_needed: number;
  saudis_surplus: number;
  penalty_change: number;
}

export interface SifExportParams {
  batch_id: string;
  include_all: boolean;
  status_filter?: string;
}

export interface SifExportResult {
  download_url: string;
  filename: string;
  record_count: number;
  generated_at: string;
}

export interface ApiKey {
  id: string;
  name: string;
  key_preview: string;
  created_at: string;
  last_used: string | null;
  active: boolean;
}

export interface BillingInfo {
  plan: string;
  credits_used: number;
  credits_total: number;
  next_billing: string;
  invoices: Invoice[];
}

export interface Invoice {
  id: string;
  amount: number;
  status: string;
  date: string;
  url: string;
}