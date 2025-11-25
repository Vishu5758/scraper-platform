# Scraper Platform Documentation

This documentation set summarizes the current codebase and how to work with it. It is organized by topic so newcomers can quickly find the right entry point for developing or operating the platform.

## What the platform does

The platform coordinates ingestion, scraping, and post-processing pipelines. Core modules live under `src/` and provide:

- **Task execution and orchestration** under `src/orchestration`, `src/pipeline_pack`, and `src/scheduler` for defining jobs and moving data through ETL stages.
- **Scraping and browser automation** under `src/scrapers`, `src/engines`, and `src/entrypoints` for task-specific logic and runtime integration.
- **Data and storage interfaces** under `src/db`, `src/exporters`, and `src/etl` for persistence and downstream delivery.
- **Governance, auditing, and compliance** helpers under `src/audit`, `src/compliance`, `src/governance`, and `src/security` to keep runs observable and policy-aligned.
- **User- and service-facing APIs** under `src/api`, `src/client_api`, and `src/entrypoints` for interacting with the platform programmatically.
- **Observability and reliability** utilities in `src/observability`, `src/run_tracking`, and `src/validation`.

## Repository layout (high level)

- `src/` – Primary Python packages for scheduling, scraping, validation, and integrations.
- `frontend-dashboard/` – React-based dashboard for monitoring and control.
- `schemas/` – Shared schema definitions for validating configuration and payloads.
- `dags/` – Airflow DAG definitions for orchestrated workloads.
- `docker-compose.yml` and `docker/` – Containers and orchestration for local deployment.
- `tests/` – Automated tests targeting the core Python packages.

## Getting started

1. Install Python dependencies with `pip install -e .` and any extras you need from `scraper-deps/`.
2. Start core services via `docker-compose up` for local experimentation.
3. Run backend tests with `pytest` from the repository root.
4. Start the dashboard from `frontend-dashboard` with `npm install` then `npm run dev`.

Refer to the architecture and deployment documents in this folder for deeper guidance.
