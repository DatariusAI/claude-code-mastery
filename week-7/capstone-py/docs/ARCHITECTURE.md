# ARCHITECTURE.md — Notification Service (Python/Flask)

## System Overview

A RESTful microservice built spec-first using the AI-Augmented SDLC
methodology from the Claude Code Mastery program.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│              CLIENT (curl / Postman)             │
└──────────────────────┬──────────────────────────┘
                       │ HTTP
                       ▼
┌─────────────────────────────────────────────────┐
│              FLASK APPLICATION                  │
│                                                 │
│  ┌────────────────┐   ┌──────────────────────┐  │
│  │ audit_logger   │──▶│  Blueprint: /api/*   │  │
│  │ (before/after  │   │                      │  │
│  │  request hooks)│   │  /health             │  │
│  └────────────────┘   │  /notifications/send │  │
│                       │  /notifications      │  │
│                       │  /notifications/audit│  │
│                       │  /notifications/stats│  │
│                       └──────────┬───────────┘  │
│                                  │               │
│                    ┌─────────────▼────────────┐  │
│                    │  NotificationService     │  │
│                    │  validate()              │  │
│                    │  send()  ← retry loop    │  │
│                    │  get_history()           │  │
│                    │  get_audit_log()         │  │
│                    │  get_stats()             │  │
│                    └──────────┬───────────────┘  │
│                               │                  │
│                    ┌──────────▼───────────────┐  │
│                    │   email_provider         │  │
│                    │   mock_email_provider()  │  │
│                    │   smtp_email_provider()  │  │
│                    └──────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## API Reference

| Method | Endpoint                       | Description                  | Spec  |
|--------|-------------------------------|------------------------------|-------|
| GET    | `/api/health`                 | Health check                 | REQ-005 |
| POST   | `/api/notifications/send`     | Send a notification          | REQ-001 |
| GET    | `/api/notifications`          | Notification history         | REQ-006 |
| GET    | `/api/notifications?status=`  | Filtered history             | REQ-006 |
| GET    | `/api/notifications/audit`    | Governance audit log         | REQ-003 |
| GET    | `/api/notifications/stats`    | Stats summary                | REQ-007 |

### POST /api/notifications/send

**Request body (JSON):**
```json
{
  "to": "user@example.com",
  "subject": "Order Confirmed",
  "type": "order",
  "body": "Optional custom body"
}
```

**Valid types:** `order`, `welcome`, `password_reset`, `alert`, `marketing`

**Success (200):**
```json
{ "success": true, "message_id": "mock-uuid", "attempts": 1 }
```

**Validation error (400):**
```json
{ "success": false, "error": "Validation failed: \"to\" is required" }
```

**Retry exhaustion (500):**
```json
{
  "success": false,
  "error": "Notification failed after 3 attempts: ...",
  "retry_history": [
    { "attempt": 1, "error": "SMTP refused", "timestamp": "..." }
  ]
}
```

---

## AI-Augmented SDLC Map

| Week | Technique               | Applied In                              |
|------|-------------------------|-----------------------------------------|
| 1–2  | Codebase exploration    | Claude read CLAUDE.md + spec first      |
| 3–4  | Spec-driven dev         | feature_spec.yaml → implementation      |
| 5–6  | Hooks & governance      | audit_logger.py, .hooks/pre-commit      |
| 7–8  | Large repo & MCP        | Architecture constraint prompts         |
| 9–10 | Multi-agent & Skills    | Separate review/test/security passes    |
| 11–12| CI/CD & Docker          | ci.yml, Dockerfile                      |
| 13   | Debug & security        | OWASP review, regression tests          |
| 14   | Capstone integration    | This entire project                     |

---

## Local Development

```bash
# Setup
python -m venv venv
venv\Scripts\activate           # Windows
source venv/bin/activate        # Mac/Linux
pip install -r requirements.txt

# Run
python src/run.py               # Production mode (port 5000)
flask --app src/app run --debug # Dev mode with hot reload

# Test
pytest                          # All tests + coverage
pytest tests/unit/ -v           # Unit only
pytest --cov=src --cov-report=html  # HTML coverage report

# Docker
docker-compose up --build       # Build + run container
docker-compose down             # Stop
```
