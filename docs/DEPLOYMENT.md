# Deployment Guide

This guide documents how to run the platform locally and promote it to staging or production with predictable, reproducible steps.

## Prerequisites

- Python 3.10+ with `pip` and virtual environment tooling.
- Docker and Docker Compose for local services (databases, message brokers, Airflow).
- Node.js 18+ for the dashboard build.
- Access to required secrets (database credentials, API tokens) injected via environment variables or a secret manager.

## Local development workflow

1. **Install backend dependencies**
   ```bash
   pip install -e .
   pip install -r scraper-deps/requirements.txt
   ```
2. **Start core services** (databases, Airflow, API container)
   ```bash
   docker-compose up -d
   ```
3. **Configure environment**
   - Create a `.env` file or export variables for `DB_*`, `REDIS_*`, and any third-party tokens consumed by modules in `src/security` and `src/config`.
   - Verify connectivity with `docker-compose logs` and ensure health checks pass for the database and Airflow containers.
4. **Run backend processes**
   - Start API/worker entrypoints from `src/entrypoints` as needed (e.g., `python -m src.entrypoints.api`).
   - Trigger pipelines via CLI tools in `scripts/` or through Airflow UI using DAGs in `dags/`.
5. **Launch the dashboard**
   ```bash
   cd frontend-dashboard
   npm install
   npm run dev
   ```
   Configure the API base URL via `.env.local` in the dashboard root.

## Staging or production rollout

1. **Build images**
   - Use Dockerfiles under `docker/` or `Dockerfile` in the repo root as build contexts.
   - Tag images with semantic versions that match the Python package version to keep DAGs and services aligned.
2. **Provision infrastructure**
   - Databases and queues must be available and reachable; apply migrations or seed data using scripts in `scripts/` or `tools/` before enabling schedulers.
   - Ensure TLS termination and network policies protect API endpoints.
3. **Configure runtime**
   - Supply environment variables for database URLs, credentials, rate limits, and feature flags. Avoid embedding secrets in images.
   - Wire observability sinks (logging, metrics, tracing) using `src/observability` utilities; confirm dashboards/alerts are in place.
4. **Deploy Airflow DAGs**
   - Package DAGs from `dags/` alongside the same application version. Avoid mixed versions between DAGs and deployed API packages to prevent schema drift.
5. **Smoke tests and health checks**
   - Call health endpoints exposed by API entrypoints to verify dependencies.
   - Run a representative scraper job and confirm data lands in storage and downstream exports succeed.
6. **Operational readiness**
   - Review retry/backoff settings in `src/orchestration` and rate limits in `src/engines` before increasing load.
   - Confirm run-tracking and audit logs are available for incident triage.

## Troubleshooting

- Use `docker-compose logs` or service logs to inspect container failures during startup.
- Validate configuration by checking environment variables consumed in `src/config` and database connectivity in `src/db`.
- For scheduler issues, confirm DAG imports succeed and that package versions in the Airflow environment match the deployed services.
- For frontend/API communication problems, verify the dashboard `.env` API host matches the running backend and that CORS settings in `src/api` permit requests.
