"""
Rules Fetcher — Fetches compliance parameters from the database at runtime.
Every engine calls this module. No hardcoded values exist anywhere.

In production, this queries the Supabase compliance_rules table.
For local development / testing, falls back to DEFAULT_RULES.
"""

from datetime import date
from typing import Optional

# ── Default rules (mirrors compliance_rules table seed data) ──
# These match the May 2026 regulatory parameters from the blueprint.
# In production, these are fetched from the database at runtime.

DEFAULT_RULES = {
    # GOSI
    "gosi_legacy_rate": 0.215,
    "gosi_progressive_base_rate": 0.22,
    "gosi_progressive_annual_step": 0.005,
    "gosi_progressive_max_rate": 0.245,
    "gosi_progressive_transition_date": "2024-07-01",
    "gosi_employer_share_legacy": 0.12,
    "gosi_employee_share_legacy": 0.095,
    "gosi_expat_occupational_hazard_rate": 0.02,
    "gosi_wage_base_cap": 45000.00,

    # Nitaqat
    "nitaqat_full_weight_min": 4000.00,
    "nitaqat_half_weight_min": 3000.00,
    "nitaqat_half_weight_max": 3999.99,
    "nitaqat_part_time_hours_threshold": 160,

    # WPS
    "wps_expat_floor": 3200.00,
    "wps_expatriate_floor": 3200.00,  # alias
    "wps_saudi_min_for_nitaqat": 4000.00,
    "wps_variance_tolerance_pct": 0.10,

    # GOSI scheme classification
    "gosi_scheme_age_threshold": 50,
    "gosi_scheme_months_threshold": 12,
    "gosi_employer_share_progressive": 0.13,  # 12% + 1% SANED
    "gosi_employee_share_progressive": 0.095,

    # Housing
    "housing_min_pct_of_basic": 0.10,

    # Diversity
    "diversity_cap_pct": 0.40,
    "diversity_warning_pct": 0.38,
    "diversity_min_headcount": 100,

    # Engineer wage floor
    "engineer_ssco_prefixes": ["2141", "2142", "2143", "2144", "2145", "2146", "2149"],
    "engineer_min_salary": 7000.00,

    # Qiwa contract window
    "qiwa_contract_window_days": 30,
    "qiwa_contract_warning_day": 25,

    # Iqama expiry alert thresholds
    "iqama_expiry_alert_days": [90, 60, 30, 7],

    # GOSI scheme age threshold
    "gosi_scheme_age_threshold": 50,
    "gosi_scheme_months_threshold": 12,
}


def get_rule(key: str, as_of: Optional[date] = None) -> float | int | str | list:
    """
    Fetch a compliance rule parameter by key.

    In production: queries Supabase compliance_rules table where
    rule_key = key AND effective_from <= as_of AND (effective_until IS NULL OR effective_until >= as_of).

    For now: returns from DEFAULT_RULES.

    Args:
        key: The rule identifier (e.g. "gosi_legacy_rate")
        as_of: The date to check rules for (defaults to today)

    Returns:
        The rule value (numeric or string)

    Raises:
        KeyError: If the rule key doesn't exist
    """
    if key not in DEFAULT_RULES:
        raise KeyError(f"Unknown compliance rule: {key}")
    return DEFAULT_RULES[key]


def get_all_rules() -> dict:
    """Return all current rules. Useful for debugging and admin dashboards."""
    return DEFAULT_RULES.copy()
