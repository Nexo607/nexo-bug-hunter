# NEXO Bug Hunter v3
Automated Web Security Intelligence — production-oriented authorized AppSec baseline.

## v3 upgrades
- Cleaner modular scanner catalog and profiles: Quick / Standard / Deep.
- Evidence-based passive findings with confidence and Potential status.
- Target normalization and DNS/IP safety gate.
- Background scan runner, cancellation state, progress and structured events.
- Technology/recon metadata and robots/sitemap discovery.
- Security headers, HSTS, cookie, CORS and HTTP transport checks.
- Responsive SOC dashboard with live polling, scan queue and finding view.
- Docker/Compose/Render deployment files.
- FastAPI OpenAPI docs.

## Login
Development defaults: `Nexo` / `admin`.
Production: override `LOGIN_USERNAME` and `LOGIN_PASSWORD` using environment variables.

## Run locally
Backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Frontend:
```bash
cd frontend
npm install
npm run dev
```
API docs: http://localhost:8000/docs

## Docker
`docker compose up --build`

## Render
Deploy the repository using `render.yaml`. Set `CORS_ORIGINS` to the UI URL and `VITE_API_URL` to the API URL. Set a production login password. Never commit `.env`.

## Safety
This release is deliberately bounded. It does not perform database dumping, credential theft, password spraying, destructive exploitation, persistence, CAPTCHA/WAF bypass, stealth/evasion, Internet-wide scanning, or bulk sensitive-data extraction. Advanced active detectors should be implemented as individually scoped, rate-limited, evidence-producing modules.
