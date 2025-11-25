# scraper-platform v5.0 scaffold

This repository contains the v5.0-ready scaffold for the scraper platform, including backend services, agentic repair utilities, and a Vite/React dashboard.

## Layout
- Backend services and shared modules live in `src/`.
- Airflow DAGs live in `dags/`.
- Configuration resides in `config/` (env overlays, sources, logging).
- Frontend dashboard code is under `frontend-dashboard/` (Vite + React + TS).
- Database migrations live in `db/migrations/`.
- CLI and operational helpers live in `tools/`.

## Getting started

### Linux/Unix
1. Copy `.env.example` to `.env` and adjust secrets.
2. Install Python deps: `pip install -r requirements.txt`.
3. (Optional) Install frontend deps: `cd frontend-dashboard && npm install`.
4. Run API locally: `uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000`.
5. Run frontend: `npm run dev -- --host --port 4173` from `frontend-dashboard/`.
6. Or use the setup script: `chmod +x scripts/setup_and_run_alfabeta.sh && ./scripts/setup_and_run_alfabeta.sh`

### Windows
1. Copy `.env.example` to `.env` and adjust secrets.
2. Install Python deps: `pip install -r requirements.txt`.
3. (Optional) Install frontend deps: `cd frontend-dashboard && npm install`.
4. Run API locally: `uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000`.
5. Run frontend: `npm run dev -- --host --port 4173` from `frontend-dashboard/`.
6. Or use the setup script: `scripts/setup_and_run_alfabeta.bat`

## Dependency files

This repository intentionally ships two `requirements.txt` files:

- `scraper-deps/requirements.txt` contains the lightweight, crawler-centric dependencies shared by Airflow DAGs and headless scraper jobs (e.g., Selenium, BeautifulSoup, YAML parsing). Keeping this list separate makes it easy to install just the scraper stack when running workers independently of the API or dashboard.
- The root-level `requirements.txt` includes `-r scraper-deps/requirements.txt` and adds API-facing and testing dependencies (e.g., FastAPI, uvicorn, pytest, LangGraph). Use this file when you want the full platform environment for local development or CI.

Keeping the scraper dependencies modular avoids bundling unnecessary packages into scraper-only deployments while still allowing a single command to install everything for end-to-end development.

## Audit event exports
- Export matching audit events (all rows, no pagination) via `GET /api/audit/export`.
- Supported formats: `csv`, `xlsx`, `json` (set with the `format` query param).
- Filters mirror the dashboard view: `event_type`, `source`, and `run_id`, and the endpoint enforces `X-Tenant-Id` scoping.
- Requests exceeding 50k rows return a clear 413 response prompting users to narrow the range.
- Responses include `Content-Disposition` headers so the dashboard can trigger downloads with sensible filenames.

## Docker
- `docker-compose.yml` runs the API with Postgres and Redis.
- `docker-compose.dashboard.yml` runs the frontend dashboard separately and forwards Vite dev server output.

Refer to:
- `CODEX.md` - Full platform specification
- `GAP_TO_V5.md` - Production-readiness items
- `LINUX_DEPLOYMENT.md` - Linux server deployment guide
- `END_TO_END_VALIDATION.md` - System validation report
- `GIT_CONFLICT_CHECK.md` - Git conflict status
