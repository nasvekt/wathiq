# Wathiq (وثيق) — Saudi Compliance Gateway

Wathiq is a Saudi corporate payroll compliance gateway that validates employee payroll records against Saudi labor law, GOSI pension rules, Nitaqat nationalization quotas, WPS salary floors, Qiwa contract windows, and 5 other regulatory dimensions. It processes batches of employee records through 10 deterministic compliance engines and returns per-employee status (ready/review/blocked) plus company-wide workforce analytics, penalty exposure estimates, and Saudization metrics. Built for Saudi enterprises, logistics operators, and payroll providers who need automated, audit-ready compliance validation.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python 3.11+), Pydantic V2, Uvicorn |
| Database | Supabase (PostgreSQL 15+ with pgcrypto) |
| AI Layer | Hermes (primary) + Google Gemini (fallback) |
| Dashboard | Vite + React 18 + TypeScript |
| Marketing Site | Astro |
| PDF Generation | WeasyPrint + arabic-reshaper + python-bidi |
| PDF Parsing | pdfplumber |
| Data Ingestion | pandas + openpyxl |
| Testing | pytest + pytest-asyncio |
| Deployment | Docker |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Supabase project (for database)
- Gemini API key (optional, for AI fallback)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your actual values

# Run development server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### Running Tests

```bash
cd backend
source venv/bin/activate
pytest -v
```

### Running with Docker

```bash
cd backend
docker build -t wathiq-backend .
docker run -p 8000:8000 --env-file .env wathiq-backend
```

## Project Structure

```
wathiq/
├── .cursorrules              # AI agent context file
├── .gitignore
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py                    # FastAPI entry point
│       ├── config.py                  # Pydantic Settings
│       ├── database.py                # Supabase client
│       ├── routers/
│       │   ├── compliance.py          # Compliance endpoints
│       │   └── health.py              # Health check
│       ├── schemas/
│       │   └── compliance.py          # Pydantic V2 schemas
│       ├── engines/
│       │   ├── compliance_engine.py   # Master orchestrator
│       │   ├── gosi_engine.py         # GOSI pension calculations
│       │   ├── nitaqat_engine.py      # Nitaqat weight & bands
│       │   ├── wps_engine.py          # Wage Protection System
│       │   ├── housing_engine.py      # Housing allowance parity
│       │   ├── iqama_engine.py        # Iqama expiry monitoring
│       │   ├── contract_engine.py     # Qiwa contract window
│       │   ├── engineer_wage_engine.py # Saudi engineer wage floor
│       │   ├── penalty_engine.py      # Health score & penalties
│       │   ├── diversity_engine.py    # Expatriate diversity cap
│       │   └── rules_fetcher.py       # Runtime rule fetching
│       ├── hermes/                    # Hermes AI client
│       ├── ai/                        # AI abstraction layer
│       ├── ingestion/                 # Data ingestion pipeline
│       ├── outputs/                   # Report/PDF generation
│       ├── tasks/                     # Background tasks
│       ├── utils/                     # Shared utilities
│       ├── middleware/                 # FastAPI middleware
│       └── tests/                     # pytest test suite
└── frontend/                          # (Vite React + Astro — planned)
```

## API Endpoints

### Health Check
```
GET /health
```
Returns service status. No authentication required.

**Response:**
```json
{
  "status": "ok",
  "service": "wathiq-compliance-gateway",
  "version": "0.1.0"
}
```

### Compliance Validation
```
POST /api/v1/validate/compliance
```
Validate a batch of employee records against all Saudi compliance rules.

**Request Body:**
```json
{
  "payroll_period": "2026-05",
  "company_sector_code": "technology",
  "company_size_category": "medium_a",
  "strict_mode": true,
  "records": [
    {
      "ref_id": "EMP001",
      "employee_name": "Ahmed Al-Rashid",
      "iqama_number": "1098765432",
      "nationality": "Saudi",
      "basic_salary": "8000.00",
      "housing_allowance": "2000.00",
      "transport_allowance": "800.00",
      "other_allowances": "0.00",
      "iqama_expiry_date": "2027-03-15",
      "hire_date": "2023-01-10",
      "contract_published": true
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "transaction_id": "tx-20260501120000-a1b2c3d4",
  "processed_at": "2026-05-01T12:00:00Z",
  "engine_version": "0.1.0",
  "rules_version": "2026-05-01",
  "summary": {
    "total_processed": 1,
    "ready_count": 1,
    "review_count": 0,
    "blocked_count": 0,
    "company_health_score": 95,
    "penalty_exposure": "0.00"
  },
  "workforce_analytics": {
    "saudization_ratio": "1.00",
    "nitaqat_band": "platinum",
    "total_gosi_liability": "1760.00",
    "expat_diversity": {
      "total_expatriates": 0,
      "excap": false,
      "warning_nationalities": []
    }
  },
  "records": [...]
}
```

**Rules Engine List (10 engines):**
1. Iqama/National ID format validation
2. Nitaqat weight calculation (wage-based Saudization credit)
3. Nitaqat target matrix (sector × company size)
4. WPS salary floor & variance check
5. Housing allowance parity (min 10% of basic)
6. GOSI pension contribution (legacy/progressive/expat)
7. Expatriate diversity cap (40% max per nationality)
8. Saudi engineer wage floor (SAR 7,000 for SSCo 214x)
9. Qiwa contract window (30-day publication deadline)
10. Iqama expiry monitoring (90/60/30/7-day alerts)

## Compliance Thresholds (May 2026)

| Rule | Threshold | Source |
|---|---|---|
| GOSI legacy rate | 21.5% (12/9.5 split) | GOSI |
| GOSI progressive rate | 22% base + 0.5%/yr, max 24.5% | GOSI |
| GOSI wage cap | SAR 45,000 | GOSI |
| Nitaqat full weight | ≥ SAR 4,000/month | Nitaqat |
| Nitaqat half weight | SAR 3,000–3,999.99 | Nitaqat |
| WPS expat floor | SAR 3,200 | MHRSD |
| Housing allowance min | 10% of basic salary | Labor Law |
| Diversity cap | 40% per nationality | MHRSD |
| Engineer wage floor | SAR 7,000 (SSCo 214x) | MHRSD |
| Qiwa contract window | 30 days from hire | Qiwa |
| Iqama expiry alerts | 90/60/30/7 days | Passport Authority |

## License

Proprietary. All rights reserved.
