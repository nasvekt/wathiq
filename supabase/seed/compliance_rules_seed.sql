-- Wathiq Compliance Rules Seed Data
-- Standalone seed file for local development
-- Same data as migration 002

INSERT INTO compliance_rules (rule_key, rule_category, parameter_value, parameter_text, effective_from, bilingual_circular_citation, source_url, is_active)
VALUES
    ('gosi_legacy_rate', 'gosi', 0.215, '21.5% total (12% employer + 9.5% employee)', '2024-07-01', 'GOSI Circular — Legacy Scheme Rate', 'https://www.gosi.gov.sa', true),
    ('gosi_progressive_base_rate', 'gosi', 0.22, '22.0% base rate at July 2024 transition', '2024-07-01', 'GOSI Circular — Progressive Scheme Base Rate', 'https://www.gosi.gov.sa', true),
    ('gosi_progressive_annual_step', 'gosi', 0.005, '0.5% increase per full fiscal year', '2024-07-01', 'GOSI Circular — Annual Step', 'https://www.gosi.gov.sa', true),
    ('gosi_progressive_max_rate', 'gosi', 0.245, '24.5% maximum ceiling', '2024-07-01', 'GOSI Circular — Rate Cap', 'https://www.gosi.gov.sa', true),
    ('gosi_progressive_transition_date', 'gosi', NULL, '2024-07-01', '2024-07-01', 'GOSI Circular — Transition Date', 'https://www.gosi.gov.sa', true),
    ('gosi_employer_share_legacy', 'gosi', 0.12, '12% employer share', '2024-07-01', 'GOSI Circular — Employer Share', 'https://www.gosi.gov.sa', true),
    ('gosi_employee_share_legacy', 'gosi', 0.095, '9.5% employee deduction', '2024-07-01', 'GOSI Circular — Employee Share', 'https://www.gosi.gov.sa', true),
    ('gosi_expat_occupational_hazard_rate', 'gosi', 0.02, '2% employer-only for expats', '2024-07-01', 'GOSI Circular — Expat Hazard Rate', 'https://www.gosi.gov.sa', true),
    ('gosi_wage_base_cap', 'gosi', 45000.00, 'SAR 45,000 cap (Basic + Housing)', '2024-07-01', 'GOSI Circular — Wage Cap', 'https://www.gosi.gov.sa', true),
    ('gosi_scheme_age_threshold', 'gosi', 50, 'Age 50+ = legacy scheme', '2024-07-01', 'GOSI Circular — Age Threshold', 'https://www.gosi.gov.sa', true),
    ('gosi_scheme_months_threshold', 'gosi', 12, '12+ months enrollment = legacy', '2024-07-01', 'GOSI Circular — Enrollment Threshold', 'https://www.gosi.gov.sa', true),
    ('nitaqat_full_weight_min', 'nitaqat', 4000.00, 'SAR 4,000 for full 1.0 weight', '2024-01-01', 'MHRSD Nitaqat Framework', 'https://www.hrsd.gov.sa', true),
    ('nitaqat_half_weight_min', 'nitaqat', 3000.00, 'SAR 3,000 for half 0.5 weight', '2024-01-01', 'MHRSD Nitaqat Framework', 'https://www.hrsd.gov.sa', true),
    ('nitaqat_half_weight_max', 'nitaqat', 3999.99, 'SAR 3,999.99 max for half weight', '2024-01-01', 'MHRSD Nitaqat Framework', 'https://www.hrsd.gov.sa', true),
    ('nitaqat_part_time_hours_threshold', 'nitaqat', 160, '160 hours/month = full-time', '2024-01-01', 'MHRSD Nitaqat Framework', 'https://www.hrsd.gov.sa', true),
    ('wps_expat_floor', 'wps', 3200.00, 'SAR 3,200 expat minimum', '2024-01-01', 'MHRSD WPS Floor', 'https://www.hrsd.gov.sa', true),
    ('wps_saudi_min_for_nitaqat', 'wps', 4000.00, 'SAR 4,000 Saudi minimum', '2024-01-01', 'MHRSD Nitaqat Framework', 'https://www.hrsd.gov.sa', true),
    ('wps_variance_tolerance_pct', 'wps', 0.10, '10% variance tolerance', '2024-01-01', 'MHRSD WPS Variance Rule', 'https://www.hrsd.gov.sa', true),
    ('housing_min_pct_of_basic', 'housing', 0.10, '10% of basic minimum', '2024-01-01', 'Saudi Labor Law — Housing', 'https://www.hrsd.gov.sa', true),
    ('diversity_cap_pct', 'diversity', 0.40, '40% max per nationality', '2024-01-01', 'MHRSD Diversity Cap', 'https://www.hrsd.gov.sa', true),
    ('diversity_warning_pct', 'diversity', 0.38, '38% warning threshold', '2024-01-01', 'MHRSD Diversity Warning', 'https://www.hrsd.gov.sa', true),
    ('diversity_min_headcount', 'diversity', 100, '100+ employees for cap', '2024-01-01', 'MHRSD Diversity Min Headcount', 'https://www.hrsd.gov.sa', true),
    ('engineer_min_salary', 'engineer', 7000.00, 'SAR 7,000 for Saudi engineers', '2024-01-01', 'Saudi Engineers Commission', 'https://www.saudieng.sa', true),
    ('qiwa_contract_window_days', 'qiwa', 30, '30 days to publish contract', '2024-01-01', 'Qiwa — Contract Window', 'https://www.qiwa.sa', true),
    ('qiwa_contract_warning_day', 'qiwa', 25, 'Day 25 warning', '2024-01-01', 'Qiwa — Warning Day', 'https://www.qiwa.sa', true),
    ('iqama_expiry_alert_days', 'iqama', NULL, '90,60,30,7', '2024-01-01', 'Passport Authority — Expiry Alerts', 'https://www.gdp.gov.sa', true);
