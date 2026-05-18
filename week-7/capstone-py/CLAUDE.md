# CLAUDE.md — Capstone Project: Notification Service API (Python)

## Project Overview
This is the **Claude Code Mastery Capstone Project** — a production-grade
Notification Service API built using AI-augmented development practices.

## Tech Stack
- **Runtime**: Python 3.11+
- **Framework**: Flask 3.x
- **Testing**: pytest + pytest-cov
- **Linting**: flake8
- **Container**: Docker + docker-compose

## Project Structure
```
capstone-py/
├── run.py                           ← START HERE: python run.py
├── conftest.py                      ← sys.path fix for pytest
├── CLAUDE.md                        ← You are here (AI context)
├── feature_spec.yaml                ← Spec-driven development spec
├── requirements.txt                 ← Python dependencies
├── src/
│   ├── app.py                       ← Flask app factory
│   ├── notifications/
│   │   ├── __init__.py
│   │   ├── notification_service.py  ← Core business logic
│   │   └── email_provider.py        ← Email adapter (mockable)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── notifications.py         ← REST API routes (Blueprint)
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── audit_logger.py          ← Governance audit trail
│   └── utils/
│       ├── __init__.py
│       └── logger.py                ← Structured logging
├── tests/
│   ├── conftest.py                  ← pytest fixtures
│   ├── unit/test_notification_service.py
│   ├── integration/test_api.py
│   └── regression/test_regression.py
├── .hooks/pre-commit                ← Governance validation hook
├── .github/workflows/ci.yml        ← GitHub Actions CI/CD
├── Dockerfile                       ← Multi-stage production image
├── docker-compose.yml
└── docs/
    ├── ARCHITECTURE.md
    └── metrics-report.md
```

## Coding Standards (Claude must follow)
- Type hints on all public functions
- Docstrings on every class and public method (Google style)
- No hardcoded secrets — use environment variables only
- All changes must produce an audit log entry
- Test coverage must remain above 80%
- Follow PEP 8 — max line length 100

## AI Workflow Rules
- Always read feature_spec.yaml before implementing any feature
- Generate tests BEFORE or alongside implementation
- Run `pytest` after every code change
- Run `flake8 src/ tests/` before committing
- Log all AI-assisted changes in the audit trail

## Key Commands
```bash
pip install -r requirements.txt   # Install dependencies
python run.py                  # Start production server
flask --app src/app run --debug    # Start dev server (hot reload)
pytest                             # Run full test suite
pytest --cov=src --cov-report=term-missing  # With coverage
flake8 src/ tests/                 # Lint check
docker-compose up --build          # Start containerised stack
```

## Environment Variables
```
FLASK_ENV=development
PORT=5000
EMAIL_PROVIDER=mock
LOG_LEVEL=INFO
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=0.1
SECRET_KEY=dev-only-change-in-prod
```
