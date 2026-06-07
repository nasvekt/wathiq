"""
Wathiq — Procurement Saudization Engine.
Enforces 70% Saudization in 12 procurement roles.
Blueprint Section 4B — Primary Market Wedge.
"""
from decimal import Decimal

# The 12 procurement roles and their SSCO codes (from blueprint Section 4B)
PROCUREMENT_ROLES = {
    "1321": {"title_en": "Procurement Manager", "title_ar": "مدير المشتريات", "min_salary": 7000},
    "1219": {"title_en": "Contracts Manager", "title_ar": "مدير العقود", "min_salary": 7000},
    "3323": {"title_en": "Purchasing Specialist", "title_ar": "أخصائي مشتريات", "min_salary": 4000},
    "3331": {"title_en": "Logistics Coordinator", "title_ar": "منسق لوجستيات", "min_salary": 4000},
    "1324": {"title_en": "Warehouse Manager", "title_ar": "مدير مستودعات", "min_salary": 5000},
    "2141": {"title_en": "Supply Chain Analyst", "title_ar": "محلل سلسلة التوريد", "min_salary": 7000},
    "2431": {"title_en": "E-Commerce Specialist", "title_ar": "أخصائي تجارة إلكترونية", "min_salary": 4000},
    "4321": {"title_en": "Inventory Controller", "title_ar": "مراقب المخزون", "min_salary": 4000},
}


def is_procurement_role(ssco_code: str | None) -> bool:
    """Check if an SSCO code maps to a procurement role."""
    if not ssco_code:
        return False
    # Check by prefix (3323 covers Purchasing Specialist, Tenders Specialist, Procurement Officer, Buyer)
    for code in PROCUREMENT_ROLES:
        if ssco_code.startswith(code) or code.startswith(ssco_code):
            return True
    return False


def calculate_procurement_saudization(
    procurement_employees: list[dict],
) -> dict:
    """
    Calculate procurement Saudization rate for a company.
    
    Input: list of dicts with keys: ssco_code, nationality, total_gross_wage, basic_salary, monthly_hours
    
    Returns: dict with saudization_pct, total, saudi_count, compliant, min_salary_violations
    """
    total = len(procurement_employees)
    if total == 0:
        return {
            "saudization_pct": 0.0,
            "total": 0,
            "saudi_count": 0,
            "saudi_weight_sum": 0.0,
            "compliant": True,
            "min_salary_violations": [],
            "message": "No procurement roles found",
        }

    saudi_weight_sum = Decimal("0.0")
    min_salary_violations = []

    for emp in procurement_employees:
        nationality = (emp.get("nationality", "") or "").strip().lower()
        is_saudi = nationality in ("saudi", "saudi arabia", "sa")
        ssco = emp.get("ssco_code", "")
        basic = Decimal(str(emp.get("basic_salary", 0)))
        total_gross = Decimal(str(emp.get("total_gross_wage", basic)))
        monthly_hours = emp.get("monthly_hours", 0)

        # Calculate Nitaqat weight
        if not is_saudi:
            weight = Decimal("0.0")
        elif monthly_hours and monthly_hours >= 160:
            weight = Decimal("1.0")
        elif total_gross >= Decimal("4000"):
            weight = Decimal("1.0")
        elif total_gross >= Decimal("3000"):
            weight = Decimal("0.5")
        else:
            weight = Decimal("0.0")

        saudi_weight_sum += weight

        # Check minimum salary for this procurement role
        role_info = PROCUREMENT_ROLES.get(ssco)
        if role_info and is_saudi and basic < Decimal(str(role_info["min_salary"])):
            min_salary_violations.append({
                "ssco_code": ssco,
                "title_en": role_info["title_en"],
                "actual_salary": float(basic),
                "min_required": role_info["min_salary"],
            })

    # Procurement Saudization % = Saudi weight sum / total procurement employees * 100
    saudization_pct = float(saudi_weight_sum / Decimal(str(total)) * Decimal("100"))
    compliant = saudization_pct >= 70.0

    return {
        "saudization_pct": round(saudization_pct, 1),
        "total": total,
        "saudi_count": int(saudi_weight_sum),
        "saudi_weight_sum": float(saudi_weight_sum),
        "compliant": compliant,
        "min_salary_violations": min_salary_violations,
        "required_pct": 70.0,
    }


def check_title_duties_mismatch(
    employee: dict,
    activity_evidence: list[str] | None = None,
) -> dict:
    """
    Title-Duties Mismatch Detector.
    Flags employees whose actual duties don't match their registered title.
    Blueprint Section 4B — The most important new feature.
    """
    ssco = employee.get("ssco_code", "")
    title = (employee.get("raw_job_title", "") or "").lower()
    role_info = PROCUREMENT_ROLES.get(ssco)
    
    if not role_info:
        return {"mismatch_risk_score": 0.0, "risk_level": "LOW", "evidence": []}

    evidence = []
    risk_score = 0.0

    # Check 1: Title contains mismatched keywords
    procurement_keywords = ["procurement", "purchasing", "tenders", "contract", "buyer", "supply chain",
                           "مشتريات", "مناقصات", "عقود", "مشتري", "سلسلة التوريد"]
    has_procurement_keywords = any(kw in title for kw in procurement_keywords)
    
    if not has_procurement_keywords and title:
        risk_score += 0.3
        evidence.append(f"Job title '{employee.get('raw_job_title', '')}' does not contain procurement keywords")

    # Check 3: Activity evidence
    if activity_evidence:
        meaningful_activity = [a for a in activity_evidence if len(a) > 20]
        procurement_activity = [a for a in activity_evidence if any(kw in a.lower() for kw in ["tender", "purchase", "order", "procurement", "supplier", "contract"])]
        
        if len(meaningful_activity) < 3:
            risk_score += 0.3
            evidence.append("Insufficient activity evidence to confirm procurement duties")
        elif len(procurement_activity) < 2:
            risk_score += 0.2
            evidence.append("Activity records lack procurement-specific actions")

    # Determine risk level
    risk_score = min(risk_score, 1.0)
    if risk_score >= 0.7:
        risk_level = "HIGH"
    elif risk_score >= 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "mismatch_risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "evidence": evidence,
    }