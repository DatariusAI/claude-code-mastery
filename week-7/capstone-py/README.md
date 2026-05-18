# 🎓 Claude Code Mastery — Capstone Project (Python)
## Notification Service API  ·  Flask / pytest / Docker

> **Session 14: End-to-End AI-Augmented SDLC**
> Pure Python. Works on Windows, Mac, and Linux.

---

## ⚡ Quick Start (5 minutes)

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run all tests (73 tests, ~96% coverage)
pytest

# 4. Start the server
python run.py

# 5. Test it live
curl http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/notifications/send ^
  -H "Content-Type: application/json" ^
  -d "{\"to\":\"you@example.com\",\"subject\":\"Hello!\",\"type\":\"welcome\"}"
```

---

## 🗺️ Hands-On Demo Script (for instructors)

### PHASE 1 — Setup (0:00 – 0:10)

```bash
# Show Claude the repo context
type CLAUDE.md

# Verify environment
pytest -q
python run.py
```

**Talk track:** *"CLAUDE.md is the AI's briefing document — it reads this
on every prompt to understand standards, structure, and constraints."*

### PHASE 2 — Read the Spec (0:10 – 0:25)

```bash
type feature_spec.yaml
```

**Claude prompt to demonstrate:**
```
Read CLAUDE.md and feature_spec.yaml.
Summarise REQ-001 to REQ-006 in one sentence each.
Tell me which source file implements each requirement.
Flag any risks before we start coding.
```

### PHASE 3 — Show the Implementation (0:25 – 0:45)

```bash
type src\notifications\notification_service.py
```

Point out: validation first, retry loop, audit on every path, injectable provider.

**Claude prompt:**
```
Review notification_service.py for OWASP Top 10 issues,
uncaught exceptions, and spec compliance. List concerns with severity.
```

### PHASE 4 — Run the Tests (0:45 – 1:00)

```bash
pytest -v
pytest --cov=src --cov-report=term-missing
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/regression/ -v
```

### PHASE 5 — CI/CD Pipeline (1:00 – 1:20)

```bash
type .github\workflows\ci.yml
```

6 stages: lint → unit → integration → regression → security → docker build.

### PHASE 6 — Docker Deployment (1:20 – 1:35)

```bash
docker-compose up --build

# In a second terminal:
curl http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/notifications/send ^
  -H "Content-Type: application/json" ^
  -d "{\"to\":\"demo@example.com\",\"subject\":\"Capstone\",\"type\":\"order\"}"
curl http://localhost:5000/api/notifications/audit
curl http://localhost:5000/api/notifications/stats

docker-compose down
```

### PHASE 7 — Demo All Features (1:35 – 2:00)

```bash
# Successful sends
curl -X POST http://localhost:5000/api/notifications/send -H "Content-Type: application/json" -d "{\"to\":\"customer@shop.com\",\"subject\":\"Order Confirmed\",\"type\":\"order\"}"
curl -X POST http://localhost:5000/api/notifications/send -H "Content-Type: application/json" -d "{\"to\":\"new@app.com\",\"subject\":\"Welcome!\",\"type\":\"welcome\"}"

# Validation errors (400)
curl -X POST http://localhost:5000/api/notifications/send -H "Content-Type: application/json" -d "{\"subject\":\"No recipient\",\"type\":\"order\"}"
curl -X POST http://localhost:5000/api/notifications/send -H "Content-Type: application/json" -d "{\"to\":\"not-an-email\",\"subject\":\"Bad\",\"type\":\"welcome\"}"

# Retry failure (500 + retry_history)
curl -X POST http://localhost:5000/api/notifications/send -H "Content-Type: application/json" -d "{\"to\":\"fail@test.com\",\"subject\":\"Will fail\",\"type\":\"alert\"}"

# History and audit
curl "http://localhost:5000/api/notifications?status=success"
curl "http://localhost:5000/api/notifications?status=failed"
curl http://localhost:5000/api/notifications/audit
curl http://localhost:5000/api/notifications/stats
```

---

## 📁 Project Structure

```
capstone-py/
├── CLAUDE.md                        ← AI context (read first)
├── feature_spec.yaml                ← 7 requirements, YAML spec
├── requirements.txt                 ← Flask, pytest, flake8
├── setup.cfg                        ← pytest + flake8 config
├── src/
│   ├── app.py                       ← Flask app factory
│   ├── run.py                       ← Server entry point
│   ├── notifications/
│   │   ├── notification_service.py  ← Core logic: send, retry, validate
│   │   └── email_provider.py        ← Mock/SMTP adapter
│   ├── routes/notifications.py      ← 6 REST endpoints (Blueprint)
│   ├── middleware/audit_logger.py   ← Before/after request hooks
│   └── utils/logger.py             ← Structured JSON logging
├── tests/
│   ├── conftest.py                  ← Shared fixtures + auto-reset
│   ├── unit/                        ← 28 unit tests
│   ├── integration/                 ← 28 integration tests
│   └── regression/                  ← 17 regression tests
├── .hooks/pre-commit                ← flake8 + pytest + audit log
├── .github/workflows/ci.yml        ← 6-stage pipeline
├── Dockerfile                       ← Multi-stage, non-root
├── docker-compose.yml
└── docs/
    ├── ARCHITECTURE.md
    └── metrics-report.md
```

---

## 🧪 Test Summary

| Suite        | Tests | Covers                                    |
|--------------|-------|-------------------------------------------|
| unit/        | 28    | REQ-001 to REQ-007 (service layer)        |
| integration/ | 28    | All API endpoints via Flask test client   |
| regression/  | 17    | REG-001 to REG-006 (named bug scenarios)  |
| **TOTAL**    | **73**| **~96% line coverage**                    |

---

## 🧑‍💻 Claude Prompts Cheat Sheet

```bash
# Explore the repo
"Read CLAUDE.md and feature_spec.yaml. Summarise what this service does
 and list each requirement with its implementing file."

# Security review
"Review src/notifications/notification_service.py for OWASP Top 10 issues,
 uncaught exceptions, and spec compliance. Severity + exact fix for each."

# Add a feature
"Add a DELETE /api/notifications/history endpoint that clears the history.
 Follow the patterns in src/routes/notifications.py."

# Improve tests
"Look at the coverage report. Find the top 3 uncovered branches in
 notification_service.py and generate pytest tests for them."

# Debug a failure
"This test is failing: [paste]. Read the test and the implementation.
 Explain the mismatch and give me the exact fix."
```

---

*Built with Claude Code · Session 14 · Claude Code Mastery Program · Python/Flask*
