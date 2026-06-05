"""
Wathiq Compliance Engines
All 10 compliance rule engines plus the master orchestrator and rules fetcher.
"""

from app.engines.compliance_engine import validate_employee, validate_batch
from app.engines.gosi_engine import calculate_gosi_contribution
from app.engines.nitaqat_engine import (
    calculate_nitaqat_weight,
    calculate_saudization_ratio,
    classify_nitaqat_band,
)
from app.engines.wps_engine import check_wps_floor, check_wps_variance
from app.engines.housing_engine import check_housing_allowance
from app.engines.iqama_engine import check_iqama_expiry
from app.engines.contract_engine import check_contract_window
from app.engines.engineer_wage_engine import check_engineer_wage_floor
from app.engines.penalty_engine import calculate_health_score, calculate_penalty_exposure
from app.engines.diversity_engine import check_diversity_cap
from app.engines.rules_fetcher import get_rule, get_all_rules

__all__ = [
    # Master orchestrator
    "validate_employee",
    "validate_batch",
    # Individual engines
    "calculate_gosi_contribution",
    "calculate_nitaqat_weight",
    "calculate_saudization_ratio",
    "classify_nitaqat_band",
    "check_wps_floor",
    "check_wps_variance",
    "check_housing_allowance",
    "check_iqama_expiry",
    "check_contract_window",
    "check_engineer_wage_floor",
    "calculate_health_score",
    "calculate_penalty_exposure",
    "check_diversity_cap",
    # Rules
    "get_rule",
    "get_all_rules",
]
