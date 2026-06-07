"""
Wathiq — SIF (Mudad WPS Bank File) Builder.
Generates bank-compliant .SIF files for payroll execution.
Spec: Section 8, Output 1 of the master blueprint.
"""
import hashlib
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

SIF_LINE_SEPARATOR = "\r\n"
SIF_ACTION_CODE = "ACTN"
SIF_DAYS_WORKED = "30"


def build_sif_header(
    establishment_id: str,
    payer_iban: str,
    payroll_period: str,
    bank_code: str,
    row_count: int,
    total_paid_sum: Decimal,
) -> str:
    """
    Build the H (header) line of the SIF file.
    H,[EstablishmentID],[PayerIBAN],[Date:YYYYMMDD],[Time:HHMMSS],[BankCode],[Period:YYYYMM],MUDADWPS,[RowCount],[TotalPaidSum]
    """
    now = datetime.utcnow()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    total_str = f"{total_paid_sum:.2f}"
    return f"H,{establishment_id},{payer_iban},{date_str},{time_str},{bank_code},{payroll_period},MUDADWPS,{row_count},{total_str}"


def build_sif_detail(
    index: int,
    national_id: str,
    employee_name: str,
    employee_iban: str,
    payer_bank_code: str,
    basic_salary: Decimal,
    housing_allowance: Decimal,
    other_allowances: Decimal,
    gosi_deduction: Decimal,
) -> str:
    """
    Build a D (detail) line for one employee.
    D,[Index],[NationalID],[EmployeeName],[EmployeeIBAN],[PayerBankCode],[BasicSalary],[HousingAllowance],[OtherAllowances],[GOSIDeduction],30,ACTN
    """
    # Strip commas from employee name — critical SIF format requirement
    clean_name = employee_name.replace(",", "")
    basic_str = f"{basic_salary:.2f}"
    housing_str = f"{housing_allowance:.2f}"
    other_str = f"{other_allowances:.2f}"
    gosi_str = f"{gosi_deduction:.2f}"
    return (
        f"D,{index},{national_id},{clean_name},{employee_iban},{payer_bank_code},"
        f"{basic_str},{housing_str},{other_str},{gosi_str},"
        f"{SIF_DAYS_WORKED},{SIF_ACTION_CODE}"
    )


def build_sif_file(
    establishment_id: str,
    payer_iban: str,
    payroll_period: str,
    bank_code: str,
    employees: list[dict],
) -> tuple[str, str]:
    """
    Build the complete SIF file content and its SHA-256 hash.
    employees: list of dicts with keys: national_id, employee_name, employee_iban,
               basic_salary, housing_allowance, other_allowances, gosi_deduction
    Returns: (sif_content, sha256_hash)
    """
    lines = []
    detail_lines = []
    total_paid = Decimal("0.00")

    for i, emp in enumerate(employees, start=1):
        basic = Decimal(str(emp["basic_salary"]))
        housing = Decimal(str(emp.get("housing_allowance", 0)))
        other = Decimal(str(emp.get("other_allowances", 0)))
        gosi = Decimal(str(emp.get("gosi_deduction", 0)))
        total_paid += basic + housing + other

        detail = build_sif_detail(
            index=i,
            national_id=emp["national_id"],
            employee_name=emp["employee_name"],
            employee_iban=emp["employee_iban"],
            payer_bank_code=bank_code,
            basic_salary=basic,
            housing_allowance=housing,
            other_allowances=other,
            gosi_deduction=gosi,
        )
        detail_lines.append(detail)

    header = build_sif_header(
        establishment_id=establishment_id,
        payer_iban=payer_iban,
        payroll_period=payroll_period,
        bank_code=bank_code,
        row_count=len(employees),
        total_paid_sum=total_paid,
    )

    lines.append(header)
    lines.extend(detail_lines)

    sif_content = SIF_LINE_SEPARATOR.join(lines) + SIF_LINE_SEPARATOR
    sha256_hash = hashlib.sha256(sif_content.encode("utf-8")).hexdigest()

    return sif_content, sha256_hash


def validate_sif(sif_content: str) -> list[str]:
    """Validate a generated SIF file for common errors. Returns list of issues."""
    issues = []
    lines = sif_content.strip().split(SIF_LINE_SEPARATOR)

    if not lines:
        return ["Empty SIF file"]

    # Check header
    header = lines[0]
    if not header.startswith("H,"):
        issues.append("Missing or malformed header line (must start with 'H,')")

    # Check CRLF line separators
    if not sif_content.endswith(SIF_LINE_SEPARATOR):
        issues.append("File must end with CRLF line separator")

    # Check detail lines
    detail_count = 0
    total_paid_detail = Decimal("0.00")
    for i, line in enumerate(lines[1:], start=2):
        if line.startswith("D,"):
            detail_count += 1
            parts = line.split(",")
            if len(parts) != 12:
                issues.append(f"Line {i}: Detail line has {len(parts)} fields (expected 12)")
                continue
            try:
                basic = Decimal(parts[6])
                housing = Decimal(parts[7])
                other = Decimal(parts[8])
                total_paid_detail += basic + housing + other
            except (IndexError, ValueError):
                issues.append(f"Line {i}: Invalid salary values")

    # Verify row count in header
    if header.startswith("H,"):
        parts = header.split(",")
        if len(parts) >= 9:
            try:
                declared_count = int(parts[8])
                if declared_count != detail_count:
                    issues.append(f"Header declares {declared_count} rows but found {detail_count}")
            except ValueError:
                issues.append("Invalid row count in header")

    return issues
