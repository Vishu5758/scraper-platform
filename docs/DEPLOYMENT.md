# Deployment Guide

This guide outlines how to run the platform locally and prepare it for staging or production environments.

## Prerequisites

- Python 3.10+ with `pip` and optional virtual environment tooling.
- Docker and Docker Compose for running dependent services.
- Node.js 18+ for the dashboard.

## Local development

1. Install backend dependencies:
   ```bash
   pip install -e .
   pip install -r scraper-deps/requirements.txt
   ```
2. Bring up supporting services with Docker:
   ```bash
   docker-compose up -d
   ```
3. Run the API or CLI entrypoints from `src/entrypoints` once services are available.
4. Start the dashboard in a separate terminal:
   ```bash
   cd frontend-dashboard
   npm install
   npm run dev
   ```

## Airflow-based runs

- Use the DAGs under `dags/` with the provided `docker-compose.yml` or integrate them into an existing Airflow deployment. Pipelines rely on the same Python packages shipped from `src/`.

## Production considerations

- Build container images using the Dockerfiles under `docker/` and `docker-compose.yml` as references.
- Configure database connections and secrets through environment variables consumed by modules in `src/db`, `src/security`, and `src/config`.
- Enable observability by wiring logging and metrics sinks using utilities in `src/observability` and `src/run_tracking`.
