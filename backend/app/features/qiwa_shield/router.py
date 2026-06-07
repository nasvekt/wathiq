"""
Qiwa Shield — API endpoints.
POST /api/v1/qiwa/upload      — Upload and scan
GET  /api/v1/qiwa/status/{id} — Scan status
POST /api/v1/qiwa/simulate    — Nitaqat what-if
POST /api/v1/qiwa/report      — Generate PDF rescue report
"""
import uuid
from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.features.qiwa_shield.schemas import (
    BatchUploadRequest,
    SimulateRequest,
    ReportRequest,
)
from app.features.qiwa_shield.engine import (
    EmployeeRecord,
    scan_batch,
    simulate_nitaqat,
)

router = APIRouter()

# In-memory scan store (replace with Redis/DB in production)
_scans: dict[str, dict] = {}


def _upload_to_employees(req: BatchUploadRequest) -> list[EmployeeRecord]:
    """Convert upload schema to engine EmployeeRecords."""
    employees = []
    for i, e in enumerate(req.employees):
        hire = None
        if e.hire_date:
            try:
                hire = datetime.strptime(e.hire_date, "%Y-%m-%d").date()
            except ValueError:
                pass
        end = None
        if e.contract_end_date:
            try:
                end = datetime.strptime(e.contract_end_date, "%Y-%m-%d").date()
            except ValueError:
                pass

        employees.append(EmployeeRecord(
            ref_id=e.ref_id or f"emp-{i+1:04d}",
            employee_name=e.employee_name,
            employee_name_ar=e.employee_name_ar,
            iqama_number=e.iqama_number,
            nationality=e.nationality,
            is_saudi=e.is_saudi,
            basic_salary=Decimal(str(e.basic_salary)),
            total_gross_wage=Decimal(str(e.total_gross_wage or e.basic_salary)),
            job_title=e.job_title,
            ssco_code=e.ssco_code,
            hire_date=hire,
            contract_end_date=end,
            contract_documented_in_qiwa=e.contract_documented_in_qiwa,
            gosi_enrolled=e.gosi_enrolled,
            monthly_hours=e.monthly_hours,
            housing_allowance=Decimal(str(e.housing_allowance)),
        ))
    return employees


def _result_to_json(result) -> dict:
    """Convert BatchScanResult to JSON-serializable dict."""
    return {
        "scan_id": result.scan_id,
        "scanned_at": result.scanned_at,
        "company_name": result.company_name,
        "total_employees": result.total_employees,
        "saudi_count": result.saudi_count,
        "documented_count": result.documented_count,
        "undocumented_count": result.undocumented_count,
        "at_risk_count": result.at_risk_count,
        "total_violations": result.total_violations,
        "blocker_count": result.blocker_count,
        "warning_count": result.warning_count,
        "saudization_ratio": result.saudization_ratio,
        "current_nitaqat_band": result.current_nitaqat_band.value,
        "compliance_health_score": result.compliance_health_score,
        "estimated_penalty_exposure": result.estimated_penalty_exposure,
        "estimated_penalty_savings": result.estimated_penalty_savings,
        "employees": [
            {
                "ref_id": e.employee.ref_id,
                "employee_name": e.employee.employee_name,
                "employee_name_ar": e.employee.employee_name_ar,
                "iqama_number": e.employee.iqama_number,
                "is_saudi": e.employee.is_saudi,
                "nitaqat_weight": e.nitaqat_weight,
                "document_status": e.document_status.value,
                "can_count_for_saudization": e.can_count_for_saudization,
                "violations": [
                    {
                        "id": v.id,
                        "name": v.name,
                        "name_ar": v.name_ar,
                        "severity": v.severity,
                        "message": v.violation_message,
                        "message_ar": v.violation_message_ar,
                    }
                    for v in e.violations
                ],
                "estimated_penalty_savings": float(e.estimated_penalty_savings),
            }
            for e in result.employees
        ],
        "action_items": result.action_items,
    }


@router.post("/qiwa/upload")
async def qiwa_upload(request: Request, body: BatchUploadRequest):
    """Upload employees, run Qiwa compliance scan, and save to Supabase."""
    company_id = request.headers.get("x-company-id", "dev-company-001")

    try:
        if not body.employees:
            raise HTTPException(status_code=400, detail="No employees provided")

        employees = _upload_to_employees(body)
        result = scan_batch(employees, company_name=body.company_name)

        # Save results to Supabase so the dashboard shows them
        batch_id = str(uuid.uuid4())
        try:
            from app.database import insert, delete as db_delete
            await db_delete("employee_records", {"company_id": f"eq.{company_id}"}, use_admin=True)
            await db_delete("audit_batches", {"company_id": f"eq.{company_id}"}, use_admin=True)

            await insert("audit_batches", [{
                "id": batch_id, "company_id": company_id,
                "batch_reference": f"QS-{result.scan_id}",
                "payroll_period": datetime.utcnow().strftime("%Y-%m"),
                "source_filename": "qiwa-shield-upload",
                "total_records": result.total_employees, "ready_count": result.total_employees - result.blocker_count - result.warning_count,
                "review_count": result.warning_count, "blocked_count": result.blocker_count,
                "saudization_ratio": result.saudization_ratio, "nitaqat_band": result.current_nitaqat_band.value,
                "company_health_score": result.compliance_health_score, "status": "complete",
            }], use_admin=True)

            for emp in result.employees:
                if emp.employee.is_saudi:
                    await insert("employee_records", [{
                        "id": str(uuid.uuid4()), "company_id": company_id, "batch_id": batch_id,
                        "ref_id": emp.employee.ref_id, "employee_name": emp.employee.employee_name,
                        "iqama_number": emp.employee.iqama_number, "compliance_status": "review" if emp.violations else "ready",
                        "nitaqat_weight": emp.nitaqat_weight,
                        "flags": [v.id for v in emp.violations] if emp.violations else [],
                    }], use_admin=True)
        except Exception:
            pass  # Supabase save is optional — results still return

        _scans[result.scan_id] = {"status": "complete", "result": result}
        return JSONResponse(content={"success": True, "scan_id": result.scan_id, **_result_to_json(result)})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan error: {str(e)}")


@router.get("/qiwa/status/{scan_id}")
async def qiwa_status(scan_id: str):
    """Check scan progress and results."""
    scan = _scans.get(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {
        "scan_id": scan_id,
        "status": scan["status"],
    }


@router.post("/qiwa/simulate")
async def qiwa_simulate(request: SimulateRequest):
    """Simulate Nitaqat band impact of workforce changes."""
    try:
        scan = _scans.get(request.scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")

        result = simulate_nitaqat(
            current_batch=scan["result"],
            add_saudi=request.add_saudi,
            add_saudi_documented=request.add_saudi_documented,
            increase_salaries_for=request.increase_salaries_for,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@router.post("/qiwa/report")
async def qiwa_report(request: ReportRequest):
    """Generate premium PDF rescue report."""
    try:
        from app.outputs.qiwa_report_builder import build_rescue_report_html

        scan = _scans.get(request.scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")

        result = scan["result"]
        html = build_rescue_report_html(result, company_name=request.company_name or result.company_name)

        return JSONResponse(content={
            "success": True,
            "html": html,
            "scan_id": request.scan_id,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report error: {str(e)}")