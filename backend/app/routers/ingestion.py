"""
Wathiq — Payroll data ingestion endpoint.
POST /api/v1/ingest/upload
Parses CSV, runs compliance engines, saves results to Supabase.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from app.schemas.compliance import ComplianceValidationRequest
from app.engines.compliance_engine import validate_batch
from app.database import insert, update as db_update

router = APIRouter()


@router.post("/ingest/upload")
async def ingest_payroll(
    request: Request,
    file: UploadFile = File(...),
    sector_code: str = Form(...),
    size_category: str = Form(...),
    payroll_period: str = Form(...),
):
    """Upload CSV, validate, and save results to Supabase."""
    company_id = request.headers.get("x-company-id", "dev-company-001")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = ""
    if "." in file.filename:
        ext = "." + file.filename.rsplit(".", 1)[1].lower()

    if ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(status_code=400, detail="Unsupported format. Use .csv, .xlsx, or .xls")

    try:
        content = await file.read()

        if ext == ".csv":
            raw_records = _parse_csv(content)
        else:
            raise HTTPException(status_code=400, detail="XLSX support coming. Use CSV for now.")

        if not raw_records:
            raise HTTPException(status_code=400, detail="No valid records found in CSV")

        # Convert to Pydantic EmployeeInput
        from app.schemas.compliance import EmployeeInput
        employees = [_dict_to_employee_input(r) for r in raw_records]

        # Run compliance validation
        result = validate_batch(
            employees=employees,
            sector_code=sector_code,
            size_category=size_category,
        )

        # Save to Supabase
        batch_id = str(uuid.uuid4())
        engine_version = "0.2.0"
        rules_version = datetime.utcnow().strftime("%Y-%m-%d")
        transaction_id = f"tx-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"

        try:
            # Insert audit batch
            summary = result.summary
            analytics = result.workforce_analytics
            total_gosi = float(analytics.total_gosi_liability) if hasattr(analytics, 'total_gosi_liability') and analytics.total_gosi_liability else 0

            await insert("audit_batches", [{
                "id": batch_id,
                "company_id": company_id,
                "batch_reference": f"BATCH-{payroll_period}-{uuid.uuid4().hex[:4].upper()}",
                "payroll_period": payroll_period,
                "source_filename": file.filename,
                "total_records": summary.total_processed,
                "ready_count": summary.ready_count,
                "review_count": summary.review_count,
                "blocked_count": summary.blocked_count,
                "saudization_ratio": analytics.saudization_ratio,
                "nitaqat_band": analytics.nitaqat_band,
                "total_gosi_liability": total_gosi,
                "penalty_exposure": float(summary.penalty_exposure) if hasattr(summary, 'penalty_exposure') and summary.penalty_exposure else 0,
                "company_health_score": summary.company_health_score,
                "engine_version": engine_version,
                "rules_version": rules_version,
                "status": "complete",
            }], use_admin=True)

            # Insert employee records
            for emp_result in result.records:
                try:
                    gosi = emp_result.gosi
                    natz = emp_result.nationalization
                    flags_list = emp_result.flags if isinstance(emp_result.flags, list) else []

                    record = {
                        "id": str(uuid.uuid4()),
                        "company_id": company_id,
                        "batch_id": batch_id,
                        "ref_id": emp_result.ref_id,
                        "employee_name": emp_result.employee_name,
                        "iqama_number": emp_result.iqama_number,
                        "compliance_status": emp_result.status.value if hasattr(emp_result.status, 'value') else str(emp_result.status),
                        "nitaqat_weight": float(natz.nitaqat_weight) if hasattr(natz, 'nitaqat_weight') and natz.nitaqat_weight else 0,
                        "flags": flags_list,
                    }

                    await insert("employee_records", [record], use_admin=True)
                except Exception:
                    pass  # Skip individual employee failures

        except Exception:
            pass  # Supabase save failed — still return results to user

        return {
            "success": True,
            "transaction_id": transaction_id,
            "processed_at": datetime.utcnow().isoformat() + "Z",
            "filename": file.filename,
            "payroll_period": payroll_period,
            "company_id": company_id,
            "batch_id": batch_id,
            "summary": {
                "total_processed": summary.total_processed,
                "ready_count": summary.ready_count,
                "review_count": summary.review_count,
                "blocked_count": summary.blocked_count,
                "company_health_score": summary.company_health_score,
                "penalty_exposure": float(summary.penalty_exposure) if hasattr(summary, 'penalty_exposure') and summary.penalty_exposure else 0,
            },
            "workforce_analytics": {
                "saudization_ratio": analytics.saudization_ratio,
                "nitaqat_band": analytics.nitaqat_band,
                "total_gosi_liability": total_gosi,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")


def _parse_csv(content: bytes) -> list[dict]:
    import csv, io
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return []
    records = []
    for row in reader:
        record = {
            "ref_id": row.get("ref_id", uuid.uuid4().hex[:8]),
            "employee_name": row.get("employee_name", ""),
            "iqama_number": row.get("iqama_number", ""),
            "nationality": row.get("nationality", ""),
            "basic_salary": _parse_float(row.get("basic_salary", "0")),
            "housing_allowance": _parse_float(row.get("housing_allowance", "0")),
            "transport_allowance": _parse_float(row.get("transport_allowance", "0")),
            "other_allowances": _parse_float(row.get("other_allowances", "0")),
        }
        for opt in ["iqama_expiry_date", "date_of_birth", "gosi_enrollment_date", "hire_date", "raw_job_title", "ssco_code"]:
            if row.get(opt):
                record[opt] = row[opt]
        if row.get("monthly_hours"):
            try:
                record["monthly_hours"] = int(row["monthly_hours"])
            except (ValueError, TypeError):
                pass
        if row.get("registered_gosi_contract_salary"):
            record["registered_gosi_contract_salary"] = _parse_float(row["registered_gosi_contract_salary"])
        records.append(record)
    return records


def _parse_float(v: str) -> float:
    try:
        return float(v.replace(",", "").strip())
    except (ValueError, AttributeError):
        return 0.0


def _dict_to_employee_input(d: dict):
    from decimal import Decimal
    from app.schemas.compliance import EmployeeInput

    def pd(v):
        if not v:
            return None
        try:
            from datetime import datetime
            return datetime.strptime(str(v).strip(), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    def pdv(v):
        if not v:
            return Decimal("0.00")
        try:
            return Decimal(str(v).replace(",", "").strip())
        except (ValueError, TypeError):
            return Decimal("0.00")

    return EmployeeInput(
        ref_id=str(d.get("ref_id", "")),
        employee_name=str(d.get("employee_name", "")),
        iqama_number=str(d.get("iqama_number", "")),
        iqama_expiry_date=pd(d.get("iqama_expiry_date")),
        nationality=str(d.get("nationality", "")),
        date_of_birth=pd(d.get("date_of_birth")),
        gosi_enrollment_date=pd(d.get("gosi_enrollment_date")),
        hire_date=pd(d.get("hire_date")),
        raw_job_title=str(d.get("raw_job_title", "")) or None,
        ssco_code=str(d.get("ssco_code", "")) or None,
        basic_salary=pdv(d.get("basic_salary", 0)),
        housing_allowance=pdv(d.get("housing_allowance", 0)),
        transport_allowance=pdv(d.get("transport_allowance", 0)),
        other_allowances=pdv(d.get("other_allowances", 0)),
        monthly_hours=d.get("monthly_hours"),
        registered_gosi_contract_salary=pdv(d.get("registered_gosi_contract_salary", 0)) or None,
        contract_published=bool(d.get("contract_published", False)),
    )