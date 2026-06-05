"""
Wathiq — Payroll data ingestion endpoint.
POST /api/v1/ingest/upload
"""
import uuid
from datetime import date, datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.schemas.compliance import ComplianceValidationRequest
from app.engines.compliance_engine import validate_batch

router = APIRouter()


@router.post("/ingest/upload")
async def ingest_payroll(
    file: UploadFile = File(...),
    sector_code: str = Form(...),
    size_category: str = Form(...),
    payroll_period: str = Form(...),
):
    """
    Upload a payroll file and validate against all compliance rules.
    Accepts CSV format. Returns validation results with employee statuses.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    valid_extensions = [".csv", ".xlsx", ".xls"]
    ext = ""
    if "." in file.filename:
        ext = "." + file.filename.rsplit(".", 1)[1].lower()

    if ext not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Accepted: {', '.join(valid_extensions)}",
        )

    try:
        content = await file.read()

        if ext == ".csv":
            raw_records = _parse_csv(content)
        else:
            raise HTTPException(status_code=400, detail="XLSX/XLS parser coming in Phase 2. Use CSV for now.")

        if not raw_records:
            raise HTTPException(status_code=400, detail="No valid records found in file")

        # Convert to Pydantic EmployeeInput objects
        from app.schemas.compliance import EmployeeInput
        employees = [_dict_to_employee_input(r) for r in raw_records]

        # Run compliance validation
        result = validate_batch(
            employees=employees,
            sector_code=sector_code,
            size_category=size_category,
        )

        return {
            "transaction_id": f"tx-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}",
            "processed_at": datetime.utcnow().isoformat() + "Z",
            "filename": file.filename,
            "payroll_period": payroll_period,
            **result.model_dump(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")


def _parse_csv(content: bytes) -> list[dict]:
    """Simple CSV parser. Returns list of dicts for compliance validation."""
    import csv
    import io

    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        return []

    records = []
    for row in reader:
        record = {
            "ref_id": row.get("ref_id", str(uuid.uuid4().hex[:8])),
            "employee_name": row.get("employee_name", ""),
            "iqama_number": row.get("iqama_number", ""),
            "nationality": row.get("nationality", ""),
            "basic_salary": _parse_decimal(row.get("basic_salary", "0")),
            "housing_allowance": _parse_decimal(row.get("housing_allowance", "0")),
            "transport_allowance": _parse_decimal(row.get("transport_allowance", "0")),
            "other_allowances": _parse_decimal(row.get("other_allowances", "0")),
        }

        # Optional fields
        if row.get("iqama_expiry_date"):
            record["iqama_expiry_date"] = row["iqama_expiry_date"]
        if row.get("date_of_birth"):
            record["date_of_birth"] = row["date_of_birth"]
        if row.get("gosi_enrollment_date"):
            record["gosi_enrollment_date"] = row["gosi_enrollment_date"]
        if row.get("hire_date"):
            record["hire_date"] = row["hire_date"]
        if row.get("raw_job_title"):
            record["raw_job_title"] = row["raw_job_title"]
        if row.get("ssco_code"):
            record["ssco_code"] = row["ssco_code"]
        if row.get("monthly_hours"):
            try:
                record["monthly_hours"] = int(row["monthly_hours"])
            except (ValueError, TypeError):
                pass
        if row.get("registered_gosi_contract_salary"):
            record["registered_gosi_contract_salary"] = _parse_decimal(row["registered_gosi_contract_salary"])

        records.append(record)

    return records


def _parse_decimal(value: str) -> float:
    """Parse a string to float, returning 0.0 on failure."""
    try:
        return float(value.replace(",", "").strip())
    except (ValueError, AttributeError):
        return 0.0


def _dict_to_employee_input(d: dict) -> "EmployeeInput":
    """Convert a raw dict to a validated EmployeeInput."""
    from datetime import date
    from decimal import Decimal
    from app.schemas.compliance import EmployeeInput

    def _parse_date(val):
        if not val:
            return None
        try:
            from datetime import datetime
            return datetime.strptime(str(val).strip(), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    def _parse_decimal_val(val):
        if not val:
            return Decimal("0.00")
        try:
            return Decimal(str(val).replace(",", "").strip())
        except (ValueError, TypeError, InvalidOperation):
            return Decimal("0.00")

    return EmployeeInput(
        ref_id=str(d.get("ref_id", "")),
        employee_name=str(d.get("employee_name", "")),
        iqama_number=str(d.get("iqama_number", "")),
        iqama_expiry_date=_parse_date(d.get("iqama_expiry_date")),
        nationality=str(d.get("nationality", "")),
        date_of_birth=_parse_date(d.get("date_of_birth")),
        gosi_enrollment_date=_parse_date(d.get("gosi_enrollment_date")),
        hire_date=_parse_date(d.get("hire_date")),
        raw_job_title=str(d.get("raw_job_title", "")) or None,
        ssco_code=str(d.get("ssco_code", "")) or None,
        basic_salary=_parse_decimal_val(d.get("basic_salary", 0)),
        housing_allowance=_parse_decimal_val(d.get("housing_allowance", 0)),
        transport_allowance=_parse_decimal_val(d.get("transport_allowance", 0)),
        other_allowances=_parse_decimal_val(d.get("other_allowances", 0)),
        monthly_hours=d.get("monthly_hours"),
        registered_gosi_contract_salary=_parse_decimal_val(d.get("registered_gosi_contract_salary", 0)) or None,
        contract_published=bool(d.get("contract_published", False)),
    )
