# Scraper Platform Documentation

This documentation set provides an operator- and developer-focused reference for running, extending, and observing the scraper platform. The goal is to give newcomers enough context to contribute safely while offering production checklists for practitioners.

## What the platform does

The platform coordinates ingestion, scraping, enrichment, and delivery pipelines. Core capabilities include:

- **Task orchestration** for scheduled and ad-hoc jobs, with retry, backoff, and dependency handling.
- **Scraper execution** using headless browsers or HTTP clients with pluggable engines for site-specific logic.
- **Data governance** through auditing, compliance hooks, and validation gates before payloads are exported.
- **APIs and dashboard** that expose controls, status, and telemetry to internal consumers.

## Repository layout (high level)

- `src/` – Primary Python packages for orchestration, scrapers, data validation, exporters, and integrations.
- `frontend-dashboard/` – React/Vite dashboard used for monitoring runs, configuring scrapers, and triggering jobs.
- `schemas/` – Shared schema definitions that shape API payloads and internal contracts.
- `dags/` – Airflow DAG definitions that compose pipelines using the same primitives as the Python packages.
- `docker/` and `docker-compose*.yml` – Container build assets and local orchestration for parity with production.
- `tests/` – Automated tests for backend logic, schemas, and integrations.
- `tools/`, `scripts/`, `dsl/` – Utility scripts, CLI helpers, and DSL assets for generating or seeding configuration.
- `docs/` – This documentation set plus subsystem-specific guidance under `docs/db` and feature folders.

## Getting started (development)

1. **Set up Python**
   - Use Python 3.10+ with a virtual environment.
   - Install core dependencies and optional extras:
     ```bash
     pip install -e .
     pip install -r scraper-deps/requirements.txt
     ```
2. **Start supporting services**
   - Bring up databases, queues, and Airflow locally:
     ```bash
     docker-compose up -d
     ```
   - Environment variables in `.env` or your shell configure connection strings for modules in `src/db`, `src/config`, and `src/security`.
3. **Run backend entrypoints**
   - Use the service entrypoints in `src/entrypoints` to start APIs or worker processes.
   - Run the scheduler/orchestrator for recurring jobs, and use CLI tools in `scripts/` for manual triggers.
4. **Launch the dashboard**
   - From `frontend-dashboard`, install dependencies and start the dev server:
     ```bash
     npm install
     npm run dev
     ```
   - Configure API base URLs via `.env.local` files in the dashboard root.
5. **Validate changes**
   - Execute backend tests: `pytest` from the repository root.
   - Run linting or type checks if configured in `pyproject.toml`/`setup.cfg`.

## Operating guidance

- **Credentials and secrets**: inject via environment variables or secret managers; do not commit them. Modules in `src/security` and `src/config` expect external provisioning.
- **Observability**: logging/metrics hooks live in `src/observability` and `src/run_tracking`. Configure sinks (e.g., Prometheus, OpenTelemetry) before production rollout.
- **Validation**: schemas under `schemas/` and validators in `src/validation` enforce payload quality; keep them in sync with API changes.
- **Extensibility**: add new scrapers under `src/scrapers` and register them with orchestrators or DAGs. Integrations and plugins belong in `src/integrations` or `src/plugins`.

Refer to the architecture, deployment, frontend, and database documents in this folder for deeper guidance on each subsystem.
