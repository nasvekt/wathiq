"""
Wathiq — Qiwa Shield Premium Rescue Report (PDF)
Bilingual EN/AR, executive summary, Health Score, prioritized action list.
Blueprint-level quality: PwC/McKinsey standard.
"""
import hashlib
from datetime import datetime


def _hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def build_rescue_report_html(
    scan_result,
    company_name: str = "",
    company_logo_url: str | None = None,
) -> str:
    """Generate premium HTML for PDF conversion."""
    ts = datetime.utcnow().isoformat() + "Z"
    doc_hash = _hash(f"{company_name}{scan_result.scan_id}{ts}")

    band_colors = {
        "platinum": "#E8D5B7", "high_green": "#22C55E", "low_green": "#86EFAC",
        "yellow": "#EAB308", "red": "#DC2626",
    }
    band_color = band_colors.get(scan_result.current_nitaqat_band.value, "#6B7280")
    score = scan_result.compliance_health_score

    # Employee table rows
    emp_rows = ""
    for emp in scan_result.employees:
        if not emp.employee.is_saudi:
            continue
        doc_color = {"documented": "#3ECF8E", "missing": "#F5A623", "at_risk": "#E53E3E"}.get(
            emp.document_status.value, "#6B7280")
        emp_rows += f"""
        <tr>
            <td style="padding:6px;border-bottom:1px solid #E5E7EB;font-size:11px;">{emp.employee.employee_name}</td>
            <td style="padding:6px;border-bottom:1px solid #E5E7EB;font-size:11px;">{emp.employee.iqama_number}</td>
            <td style="padding:6px;border-bottom:1px solid #E5E7EB;font-size:11px;">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{doc_color};margin-right:4px;"></span>
                {emp.document_status.value.upper()}
            </td>
            <td style="padding:6px;border-bottom:1px solid #E5E7EB;font-size:11px;">{'✅' if emp.can_count_for_saudization else '❌'}</td>
            <td style="padding:6px;border-bottom:1px solid #E5E7EB;font-size:11px;">{emp.nitaqat_weight}</td>
            <td style="padding:6px;border-bottom:1px solid #E5E7EB;font-size:11px;">{len(emp.violations)} issues</td>
        </tr>"""

    # Action items
    actions_html = ""
    for i, item in enumerate(scan_result.action_items, 1):
        actions_html += f"<li style='margin-bottom:8px;color:#374151;font-size:12px;line-height:1.5;'><strong>{i}.</strong> {item}</li>"

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
    @page {{ size: A4; margin: 2cm; @bottom-center {{ content: "Page " counter(page) " of " counter(pages); font-size:9px; color:#9CA3AF; }} }}
    body {{ font-family:'Noto Sans Arabic','Sora',sans-serif; color:#111827; line-height:1.6; }}
    .header {{ background: linear-gradient(135deg, #111827, #1C1C1E); color:white; padding:40px; border-radius:12px 12px 0 0; }}
    .header h1 {{ margin:0; font-size:22px; color:#3ECF8E; }}
    .section {{ margin:20px 0; padding:24px; background:#F9FAFB; border-radius:12px; }}
    .section h2 {{ margin:0 0 16px; font-size:14px; color:#111827; text-transform:uppercase; letter-spacing:0.5px; }}
    .score-ring {{ width:120px;height:120px;border-radius:50%;background:conic-gradient({band_color} {score}%, #E5E7EB 0%);display:flex;align-items:center;justify-content:center;margin:0 auto; }}
    .score-ring-inner {{ width:90px;height:90px;border-radius:50%;background:#F9FAFB;display:flex;align-items:center;justify-content:center; }}
    .score-number {{ font-size:36px;font-weight:700;color:{band_color}; }}
    .badge {{ display:inline-block;padding:4px 12px;border-radius:4px;font-weight:600;font-size:11px; }}
    table {{ width:100%;border-collapse:collapse;font-size:12px; }}
    th {{ text-align:left;padding:8px;background:#F3F4F6;font-weight:600;font-size:10px;text-transform:uppercase; }}
    .legal {{ margin-top:24px;padding:16px;background:#FEF2F2;border:1px solid #FECACA;border-radius:8px;font-size:9px;color:#991B1B; }}
    .grid {{ display:grid;grid-template-columns:1fr 1fr;gap:12px; }}
    .card {{ background:white;padding:16px;border-radius:8px;border:1px solid #E5E7EB; }}
    .card .label {{ font-size:10px;color:#6B7280;text-transform:uppercase; }}
    .card .value {{ font-size:20px;font-weight:700;color:#111827; }}
</style></head><body>

<div class="header">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <h1>WATHIQ COMPLIANCE RESCUE REPORT</h1>
            <p style="margin:4px 0 0;font-size:12px;color:#9CA3AF;">
                تقرير إنقاذ الامتثال — وثيق
            </p>
            <p style="margin:8px 0 0;font-size:11px;color:#D1D5DB;">
                {company_name or 'Company'} | {scan_result.scan_id} | {scan_result.scanned_at[:10]}
            </p>
        </div>
    </div>
    <div style="margin-top:16px;border-top:1px solid rgba(255,255,255,0.1);padding-top:12px;font-size:11px;">
        <span>Hash: {doc_hash[:24]}...</span>
    </div>
</div>

<div class="section" style="text-align:center;">
    <h2>Compliance Health Score / درجة الصحة التنظيمية</h2>
    <div class="score-ring"><div class="score-ring-inner"><div class="score-number">{score}</div></div></div>
    <p style="margin-top:12px;">
        Nitaqat Band: <span class="badge" style="background:{band_color}20;color:{band_color};">{scan_result.current_nitaqat_band.value.upper()}</span>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        Saudization: <strong>{scan_result.saudization_ratio:.1f}%</strong>
    </p>
</div>

<div class="section">
    <h2>Executive Summary / الملخص التنفيذي</h2>
    <div class="grid">
        <div class="card"><div class="label">Total Employees</div><div class="value">{scan_result.total_employees}</div></div>
        <div class="card"><div class="label" style="color:#3ECF8E;">Documented</div><div class="value" style="color:#3ECF8E;">{scan_result.documented_count}</div></div>
        <div class="card"><div class="label" style="color:#F5A623;">Undocumented</div><div class="value" style="color:#F5A623;">{scan_result.undocumented_count}</div></div>
        <div class="card"><div class="label" style="color:#E53E3E;">At Risk</div><div class="value" style="color:#E53E3E;">{scan_result.at_risk_count}</div></div>
        <div class="card"><div class="label">Penalty Exposure</div><div class="value" style="color:#E53E3E;">SAR {scan_result.estimated_penalty_exposure:,.0f}</div></div>
        <div class="card"><div class="label" style="color:#3ECF8E;">Potential Savings</div><div class="value" style="color:#3ECF8E;">SAR {scan_result.estimated_penalty_savings:,.0f}</div></div>
    </div>
</div>

<div class="section">
    <h2>Corrective Actions / الإجراءات التصحيحية</h2>
    <ol style="padding-left:20px;">{actions_html}</ol>
</div>

<h3 style="font-size:13px;margin:16px 0 8px;color:#374151;">Saudi Employee Compliance / امتثال الموظفين السعوديين</h3>
<table>
    <tr><th>Name</th><th>IQAMA</th><th>Qiwa Status</th><th>Nitaqat Eligible</th><th>Weight</th><th>Issues</th></tr>
    {emp_rows}
</table>

<div class="legal">
    <strong>Legal Disclaimer</strong><br>
    This Rescue Report is an automated compliance audit by Wathiq (Engine v0.2, Rules {scan_result.scanned_at[:10]}). 
    All calculations use publicly available regulatory formulas. This is an objective data audit, not legal certification.
    Document hash: {doc_hash}
</div>

</body></html>"""