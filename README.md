# NEXO Bug Hunter — Advanced

**Automated Web Security Intelligence**

A polished FastAPI + React platform for authorized web application security assessment. This release adds live scan stages/events, scanner catalog, profile selection, evidence-backed findings, CSV/JSON export, stronger ownership checks, rate limiting, SSRF-oriented destination controls, PostgreSQL dependency support, and a responsive enterprise AppSec UI.

## Safety boundary

NEXO requires explicit target authorization. It does not implement stealth, credential theft, malware, persistence, CAPTCHA bypass, WAF evasion, destructive exploitation, or unauthorized access. Scanner modules never invent findings.

The safe baseline actively runs:
- HTTP security-header checks
- Passive technology/header inventory

Other OWASP scanner modules are registered extension points and intentionally do not emit fabricated results until implemented with bounded, authorized, evidence-backed checks.

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
export VITE_API_BASE=http://localhost:8000
npm run dev
```

Open the Vite URL.

### Docker

From the repository root:

```bash
docker compose up --build
```

- UI: http://localhost:5173
- API: http://localhost:8000
- OpenAPI: http://localhost:8000/docs

## GitHub upload

```bash
git init
git add .
git commit -m "Initial NEXO Bug Hunter release"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

You can also create the repository on GitHub and upload the extracted files through the web interface.

## Render

1. Push this repository to GitHub.
2. In Render, choose **New → Blueprint** and select the repository.
3. Render reads `render.yaml`.
4. Create/connect a PostgreSQL database for production.
5. Set `DATABASE_URL`.
6. Keep Render-generated `SECRET_KEY` and `JWT_SECRET`.
7. Set `CORS_ORIGINS` to the exact public frontend origin.
8. After the API deploys, set `VITE_API_BASE` on the frontend service to the API's public HTTPS URL.
9. Redeploy the frontend.
10. Verify `https://YOUR-API/api/health`.

Expected health response:

```json
{
  "status": "ok",
  "service": "nexo-bug-hunter",
  "version": "1.1.0"
}
```

## Production database

SQLite is suitable for development. Use PostgreSQL for production and multi-instance deployments. The SQLAlchemy model layer is PostgreSQL-compatible and `psycopg` is included.

For production schema management, apply migrations rather than relying on `create_all()`.

## Main APIs

Authentication:
- `POST /api/auth/register`
- `POST /api/auth/login`

System:
- `GET /api/health`
- `GET /api/system/status`
- `GET /api/scanner-catalog`

Targets:
- `POST /api/targets`
- `GET /api/targets`
- `DELETE /api/targets/{id}`

Scans:
- `POST /api/scans`
- `GET /api/scans`
- `GET /api/scans/{id}`
- `GET /api/scans/{id}/events`
- `POST /api/scans/{id}/cancel`

Findings:
- `GET /api/findings`
- `GET /api/findings/{id}`
- `PATCH /api/findings/{id}`

Exports:
- `GET /api/exports/findings.json`
- `GET /api/exports/findings.csv`

## Architecture

```text
Target
  ↓
Authorization + Ownership Gate
  ↓
Scope Validation / SSRF Controls
  ↓
HTTP Discovery
  ↓
Technology Detection
  ↓
Passive Security Checks
  ↓
Authorized OWASP Scanner Registry
  ↓
Finding Normalization
  ↓
Database
  ↓
Dashboard / Evidence / Export
```

Long-running scans execute outside the request handler using an asynchronous worker task and expose progress/events through polling APIs. For horizontally scaled production deployments, replace the in-process task runner with a durable queue such as Celery/RQ/Arq backed by Redis.

## Project layout

```text
nexo-bug-hunter/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── scanners/
│   │   ├── utils/
│   │   ├── workers/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── migrations/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── render.yaml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## Security defaults

- Password hashing with bcrypt
- JWT-based protected API
- User-specific target and finding queries
- Explicit authorization confirmation
- Target validation
- Basic DNS resolution checks against private/loopback/link-local/multicast/reserved addresses
- Request timeouts
- Per-client API rate limiting
- Scan request budgets
- Audit events
- Generic internal-error responses
- Environment-based secrets
- No shell command execution for scanners
- No synthetic vulnerabilities or accuracy claims

## Important production hardening

Before public production use:
1. Configure PostgreSQL.
2. Add Alembic revisions and run migrations.
3. Put the API behind HTTPS.
4. Set exact `CORS_ORIGINS`.
5. Use strong generated secrets.
6. Move scan execution to a durable external worker queue for multiple API instances.
7. Add centralized structured logging/monitoring.
8. Add automated tests and CI.
9. Add CSRF protection if cookie authentication is introduced.
10. Review target-scope rules against the organization's bug-bounty authorization policy.

## License

MIT.
