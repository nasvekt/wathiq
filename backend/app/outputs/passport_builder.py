"""
Wathiq — Verification Passport Builder.
Generates the bilingual PDF compliance certificate.
Blueprint Section 13 — PwC/McKinsey quality standard.
"""
import hashlib
import uuid
from datetime import datetime


def _generate_hash(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def build_passport_html(
    company_name_en: str,
    company_name_ar: str,
    commercial_registration: str,
    payroll_period: str,
    batch_reference: str,
    health_score: int,
    nitaqat_band: str,
    total_records: int,
    ready_count: int,
    review_count: int,
    blocked_count: int,
    saudization_ratio: float,
    total_gosi_liability: float,
    penalty_exposure: float,
    engine_version: str,
    rules_version: str,
    employees: list[dict] | None = None,
    corrective_actions: list[str] | None = None,
    rules_applied: list[dict] | None = None,
) -> str:
    """
    Generate the HTML template for the Verification Passport PDF.
    Designed for WeasyPrint rendering with bilingual EN/AR layout.
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    batch_ref = batch_reference or f"WTH-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4]}"
    
    # Generate cryptographic hash
    hash_input = f"{company_name_en}{commercial_registration}{payroll_period}{total_records}{timestamp}"
    doc_hash = _generate_hash(hash_input)

    # Nitaqat band color
    band_colors = {
        "platinum": "#E8D5B7",
        "high_green": "#22C55E",
        "low_green": "#86EFAC",
        "yellow": "#EAB308",
        "red": "#DC2626",
    }
    band_color = band_colors.get(nitaqat_band, "#6B7280")

    # Build employee table rows
    emp_rows = ""
    if employees:
        for emp in employees:
            status_color = {
                "ready": "#3ECF8E", "review": "#F5A623", "blocked": "#E53E3E", "at_risk": "#F97316"
            }.get(emp.get("status", ""), "#6B7280")
            emp_rows += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #E5E7EB;">{emp.get('employee_name', '')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #E5E7EB;">{emp.get('iqama_number', '')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #E5E7EB;">{emp.get('ssco_code', '')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #E5E7EB;">SAR {emp.get('basic_salary', 0):,.2f}</td>
                <td style="padding: 8px; border-bottom: 1px solid #E5E7EB;">
                    <span style="display: inline-block; padding: 2px 8px; border-radius: 4px; 
                          background: {status_color}20; color: {status_color}; font-weight: 600; font-size: 11px;">
                        {emp.get('status', '').upper()}
                    </span>
                </td>
            </tr>"""

    # Build corrective actions
    actions_html = ""
    if corrective_actions:
        for i, action in enumerate(corrective_actions, 1):
            actions_html += f"<li style='margin-bottom: 8px; color: #374151;'>{action}</li>"

    # Build rules applied
    rules_html = ""
    if rules_applied:
        for rule in rules_applied:
            rules_html += f"""
            <tr>
                <td style="padding: 6px; border-bottom: 1px solid #F3F4F6; font-family: monospace; font-size: 11px;">{rule.get('rule_id', '')}</td>
                <td style="padding: 6px; border-bottom: 1px solid #F3F4F6; font-size: 11px;">{rule.get('value', '')}</td>
                <td style="padding: 6px; border-bottom: 1px solid #F3F4F6; font-size: 11px;">{rule.get('citation', '')}</td>
            </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: A4;
        margin: 2cm;
        @bottom-center {{
            content: "Page " counter(page) " of " counter(pages);
            font-size: 9px;
            color: #9CA3AF;
        }}
    }}
    body {{
        font-family: 'Noto Sans Arabic', 'Sora', sans-serif;
        color: #111827;
        line-height: 1.6;
    }}
    .header {{
        background: #111827;
        color: white;
        padding: 30px;
        border-radius: 8px 8px 0 0;
        margin-bottom: 0;
    }}
    .header h1 {{
        margin: 0;
        font-size: 18px;
        color: #3ECF8E;
    }}
    .header .seal {{
        float: right;
        width: 60px;
        height: 60px;
        border: 2px solid #3ECF8E;
        border-radius: 50%;
        text-align: center;
        line-height: 60px;
        font-size: 10px;
        color: #3ECF8E;
        font-weight: bold;
    }}
    .section {{
        margin: 20px 0;
        padding: 20px;
        background: #F9FAFB;
        border-left: 4px solid #3ECF8E;
        border-radius: 0 8px 8px 0;
    }}
    .section h2 {{
        margin: 0 0 12px 0;
        font-size: 14px;
        color: #111827;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .health-score {{
        font-size: 48px;
        font-weight: bold;
        color: {band_color};
        text-align: center;
        padding: 20px;
    }}
    .badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
    }}
    th {{
        text-align: left;
        padding: 8px;
        background: #F3F4F6;
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .legal {{
        margin-top: 30px;
        padding: 15px;
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 8px;
        font-size: 10px;
        color: #991B1B;
        line-height: 1.5;
    }}
    .gold-accent {{
        height: 2px;
        background: linear-gradient(90deg, #D4AF37, #F5E6A3, #D4AF37);
        margin: 0;
    }}
    .summary-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }}
    .summary-item {{
        background: white;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #E5E7EB;
    }}
    .summary-item .label {{
        font-size: 10px;
        color: #6B7280;
        text-transform: uppercase;
    }}
    .summary-item .value {{
        font-size: 18px;
        font-weight: bold;
        color: #111827;
    }}
</style>
</head>
<body>

<div class="header">
    <div class="seal">وثيق</div>
    <h1>WATHIQ VERIFICATION PASSPORT</h1>
    <p style="margin: 4px 0 0 0; font-size: 12px; color: #9CA3AF;">
        وثيقة التحقق من الامتثال — {company_name_ar}
    </p>
    <div style="margin-top: 12px; font-size: 11px; color: #D1D5DB;">
        <span>Batch: {batch_ref}</span> &nbsp;|&nbsp; 
        <span>Period: {payroll_period}</span> &nbsp;|&nbsp;
        <span>{timestamp}</span>
    </div>
</div>

<div class="gold-accent"></div>

<div class="section">
    <h2>Company / الشركة</h2>
    <p><strong>{company_name_en}</strong> — {company_name_ar}</p>
    <p>CR: {commercial_registration} | Engine: {engine_version} | Rules: {rules_version}</p>
</div>

<div class="section" style="text-align: center;">
    <h2>Company Health Score / درجة الصحة</h2>
    <div class="health-score">{health_score}</div>
    <p>Nitaqat Band: <span class="badge" style="background: {band_color}20; color: {band_color};">{nitaqat_band.upper()}</span></p>
</div>

<div class="section">
    <h2>Executive Summary / الملخص التنفيذي</h2>
    <div class="summary-grid">
        <div class="summary-item">
            <div class="label">Total Records</div>
            <div class="value">{total_records}</div>
        </div>
        <div class="summary-item">
            <div class="label" style="color: #3ECF8E;">Ready</div>
            <div class="value" style="color: #3ECF8E;">{ready_count}</div>
        </div>
        <div class="summary-item">
            <div class="label" style="color: #F5A623;">Review</div>
            <div class="value" style="color: #F5A623;">{review_count}</div>
        </div>
        <div class="summary-item">
            <div class="label" style="color: #E53E3E;">Blocked</div>
            <div class="value" style="color: #E53E3E;">{blocked_count}</div>
        </div>
        <div class="summary-item">
            <div class="label">Saudization</div>
            <div class="value">{saudization_ratio:.1f}%</div>
        </div>
        <div class="summary-item">
            <div class="label">GOSI Liability</div>
            <div class="value">SAR {total_gosi_liability:,.2f}</div>
        </div>
        <div class="summary-item">
            <div class="label">Penalty Exposure</div>
            <div class="value" style="color: #E53E3E;">SAR {penalty_exposure:,.2f}</div>
        </div>
        <div class="summary-item">
            <div class="label">Hash</div>
            <div class="value" style="font-size: 10px; font-family: monospace; word-break: break-all;">{doc_hash[:32]}...</div>
        </div>
    </div>
</div>

<div class="section">
    <h2>Cryptographic Proof / الإثبات الرقمي</h2>
    <p style="font-family: monospace; font-size: 11px; word-break: break-all;">
        SHA-256: {doc_hash}
    </p>
    <p style="font-family: monospace; font-size: 11px;">
        Reference: {batch_ref}
    </p>
</div>

"""
    if rules_applied:
        html += f"""
<div class="section">
    <h2>Rules Applied / القواعد المطبقة</h2>
    <table>
        <tr><th>Rule</th><th>Value Applied</th><th>Authority</th></tr>
        {rules_html}
    </table>
</div>"""

    if corrective_actions:
        html += f"""
<div class="section">
    <h2>Corrective Actions / الإجراءات التصحيحية</h2>
    <ol>{actions_html}</ol>
</div>"""

    if employees:
        html += f"""
<div class="section">
    <h2>Employee Compliance / امتثال الموظفين</h2>
    <table>
        <tr><th>Name</th><th>ID</th><th>SSCO</th><th>Salary</th><th>Status</th></tr>
        {emp_rows}
    </table>
</div>"""

    html += f"""
<div class="legal">
    <strong>Legal Disclaimer / إخلاء مسؤولية قانوني</strong><br><br>
    This Verification Passport documents the results of an automated compliance audit conducted by Wathiq 
    Compliance Gateway (Engine {engine_version}, Rules Database {rules_version}) on {timestamp}. 
    All calculations were performed against active, publicly available regulatory formulas as published 
    by MHRSD, GOSI, Mudad, and Qiwa as of the audit date. Wathiq does not guarantee the behavior of 
    government portal backend systems, which may be subject to undocumented maintenance or updates 
    outside the scope of publicly available regulatory publications. This document constitutes an 
    objective automated data audit, not a legal compliance certification.
</div>

</body>
</html>"""
    return html


def build_etimad_passport_html(**kwargs) -> str:
    """Etimad Tender Passport — procurement-specific variant."""
    html = build_passport_html(**kwargs)
    # Add procurement-specific header
    html = html.replace(
        "<h1>WATHIQ VERIFICATION PASSPORT</h1>",
        "<h1>PROCUREMENT SAUDIZATION EVIDENCE — ETIMAD TENDER SUBMISSION</h1>"
    )
    return html