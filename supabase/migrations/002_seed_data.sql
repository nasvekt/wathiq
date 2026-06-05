-- Wathiq Compliance Gateway — Seed Data Migration 002
-- Seeds compliance_rules with all May 2026 regulatory parameters
-- Matches the compliance_rules table schema from migration 001

INSERT INTO compliance_rules (rule_key, rule_category, parameter_value, parameter_text, effective_from, bilingual_circular_citation, source_url, is_active)
VALUES
    -- GOSI Rules
    ('gosi_legacy_rate', 'gosi', 0.215, '21.5% total (12% employer + 9.5% employee)', '2024-07-01', 'GOSI Circular — Legacy Scheme Rate / تعميم التأمينات — معدل النظام القديم', 'https://www.gosi.gov.sa', true),
    ('gosi_progressive_base_rate', 'gosi', 0.22, '22.0% base rate at July 2024 transition', '2024-07-01', 'GOSI Circular — Progressive Scheme Base Rate / تعميم التأمينات — المعدل الأساسي للنظام التصاعدي', 'https://www.gosi.gov.sa', true),
    ('gosi_progressive_annual_step', 'gosi', 0.005, '0.5% increase per full fiscal year since transition', '2024-07-01', 'GOSI Circular — Progressive Scheme Annual Step / تعميم التأمينات — الزيادة السنوية', 'https://www.gosi.gov.sa', true),
    ('gosi_progressive_max_rate', 'gosi', 0.245, '24.5% maximum ceiling rate', '2024-07-01', 'GOSI Circular — Progressive Scheme Rate Cap / تعميم التأمينات — الحد الأقصى', 'https://www.gosi.gov.sa', true),
    ('gosi_progressive_transition_date', 'gosi', NULL, '2024-07-01', '2024-07-01', 'GOSI Circular — Transition Date / تعميم التأمينات — تاريخ الانتقال', 'https://www.gosi.gov.sa', true),
    ('gosi_employer_share_legacy', 'gosi', 0.12, '12% employer share under legacy scheme', '2024-07-01', 'GOSI Circular — Legacy Employer Contribution / تعميم التأمينات — حصة صاحب العمل', 'https://www.gosi.gov.sa', true),
    ('gosi_employee_share_legacy', 'gosi', 0.095, '9.5% employee deduction under legacy scheme', '2024-07-01', 'GOSI Circular — Legacy Employee Deduction / تعميم التأمينات — حصة الموظف', 'https://www.gosi.gov.sa', true),
    ('gosi_expat_occupational_hazard_rate', 'gosi', 0.02, '2% employer-only for expatriates', '2024-07-01', 'GOSI Circular — Expatriate Occupational Hazard / تعميم التأمينات — الأخطار المهنية للوافدين', 'https://www.gosi.gov.sa', true),
    ('gosi_wage_base_cap', 'gosi', 45000.00, 'SAR 45,000 monthly cap (Basic + Housing only)', '2024-07-01', 'GOSI Circular — Wage Base Cap / تعميم التأمينات — الحد الأقصى للأجر الخاضع', 'https://www.gosi.gov.sa', true),
    ('gosi_scheme_age_threshold', 'gosi', 50, 'Age 50+ at transition = legacy scheme', '2024-07-01', 'GOSI Circular — Scheme Age Threshold / تعميم التأمينات — حد العمر', 'https://www.gosi.gov.sa', true),
    ('gosi_scheme_months_threshold', 'gosi', 12, '12+ months enrollment before transition = legacy scheme', '2024-07-01', 'GOSI Circular — Scheme Enrollment Threshold / تعميم التأمينات — حد مدة التسجيل', 'https://www.gosi.gov.sa', true),

    -- Nitaqat Rules
    ('nitaqat_full_weight_min', 'nitaqat', 4000.00, 'SAR 4,000 minimum for full 1.0 weight', '2024-01-01', 'MHRSD Nitaqat Framework / إطار نطاقات وزارة الموارد البشرية', 'https://www.hrsd.gov.sa', true),
    ('nitaqat_half_weight_min', 'nitaqat', 3000.00, 'SAR 3,000 minimum for half 0.5 weight', '2024-01-01', 'MHRSD Nitaqat Framework / إطار نطاقات', 'https://www.hrsd.gov.sa', true),
    ('nitaqat_half_weight_max', 'nitaqat', 3999.99, 'SAR 3,999.99 maximum for half 0.5 weight', '2024-01-01', 'MHRSD Nitaqat Framework / إطار نطاقات', 'https://www.hrsd.gov.sa', true),
    ('nitaqat_part_time_hours_threshold', 'nitaqat', 160, '160 hours/month for full-time equivalent', '2024-01-01', 'MHRSD Nitaqat Framework / إطار نطاقات', 'https://www.hrsd.gov.sa', true),

    -- WPS Rules
    ('wps_expat_floor', 'wps', 3200.00, 'SAR 3,200 minimum for expatriates', '2024-01-01', 'MHRSD Ministerial Decree — WPS Floor / قرار وزاري — الحد الأدنى لحماية الأجور', 'https://www.hrsd.gov.sa', true),
    ('wps_saudi_min_for_nitaqat', 'wps', 4000.00, 'SAR 4,000 minimum for Saudi Nitaqat compliance', '2024-01-01', 'MHRSD Nitaqat Framework / إطار نطاقات', 'https://www.hrsd.gov.sa', true),
    ('wps_variance_tolerance_pct', 'wps', 0.10, '10% variance tolerance from GOSI contract salary', '2024-01-01', 'MHRSD WPS Variance Rule / قاعدة تفاوت حماية الأجور', 'https://www.hrsd.gov.sa', true),

    -- Housing
    ('housing_min_pct_of_basic', 'housing', 0.10, '10% of basic salary minimum housing allowance', '2024-01-01', 'Saudi Labor Law — Housing Allowance / نظام العمل — بدل السكن', 'https://www.hrsd.gov.sa', true),

    -- Diversity
    ('diversity_cap_pct', 'diversity', 0.40, '40% maximum single nationality among expatriates', '2024-01-01', 'MHRSD Diversity Cap Rule / قاعدة تنوع الجنسيات', 'https://www.hrsd.gov.sa', true),
    ('diversity_warning_pct', 'diversity', 0.38, '38% warning threshold for nationality concentration', '2024-01-01', 'MHRSD Diversity Warning Threshold / حد التنبيه لتنوع الجنسيات', 'https://www.hrsd.gov.sa', true),
    ('diversity_min_headcount', 'diversity', 100, '100+ employees for diversity cap to apply', '2024-01-01', 'MHRSD Diversity Cap — Minimum Headcount / الحد الأدنى لتطبيق قاعدة التنوع', 'https://www.hrsd.gov.sa', true),

    -- Engineer Wage Floor
    ('engineer_min_salary', 'engineer', 7000.00, 'SAR 7,000 minimum for Saudi engineers (SSCO 2141xx-2149xx)', '2024-01-01', 'Saudi Engineers Commission Circular / تعميم الهيئة السعودية للمهندسين', 'https://www.saudieng.sa', true),

    -- Qiwa Contract Window
    ('qiwa_contract_window_days', 'qiwa', 30, '30 calendar days from hire to publish contract on Qiwa', '2024-01-01', 'Qiwa Platform — Contract Publication Window / منصة قوى — مدة نشر العقد', 'https://www.qiwa.sa', true),
    ('qiwa_contract_warning_day', 'qiwa', 25, 'Day 25 warning before 30-day deadline', '2024-01-01', 'Qiwa Platform — Contract Warning Day / منصة قوى — يوم التنبيه', 'https://www.qiwa.sa', true),

    -- Iqama Expiry
    ('iqama_expiry_alert_days', 'iqama', NULL, '90,60,30,7', '2024-01-01', 'Passport Authority — Iqama Expiry Alerts / الجوازات — تنبيهات انتهاء الإقامة', 'https://www.gdp.gov.sa', true);
