# Architecture Overview

This document summarizes the current architecture of the scraper platform and highlights where to look for implementation details.

## Backend services

- **API and client access**: `src/api` exposes service endpoints while `src/client_api` packages client helpers. `src/entrypoints` contains adapters for running the platform as CLIs or services.
- **Scraping and execution**: `src/scrapers` hosts scraper definitions, `src/engines` manages execution backends, and `src/processors` provides reusable transforms. Browser-centric automation lives alongside other runtime integrations in these modules.
- **Pipelines and orchestration**: `src/orchestration`, `src/pipeline_pack`, `src/scheduler`, and `src/etl` coordinate end-to-end jobs, batching, retries, and data movement across stages.
- **Data management**: `src/db` handles database access, while `src/exporters` moves processed payloads to external systems.
- **Observability and governance**: `src/observability`, `src/run_tracking`, and `src/validation` keep runs traceable. `src/audit`, `src/compliance`, and `src/security` enforce policy and auditing.
- **Extensibility**: `src/plugins` and `src/integrations` host optional capabilities such as third-party connectors, feature flags, or ML-driven features under `src/ml`.

## Frontend dashboard

The `frontend-dashboard` package is a React/Vite application used for monitoring and controlling the platform. It consumes API endpoints exposed by the backend and can be run locally for development alongside the backend services.

## Airflow and scheduling

Airflow DAGs in `dags/` provide packaged workflows that depend on the same pipeline primitives. They can be deployed with the Docker services included in the repository or integrated into existing Airflow deployments.

## Configuration and schemas

Validation and typing for requests and responses are centralized under `schemas/`. These definitions are shared by API handlers, exporters, and runtime pipeline components to guarantee compatibility between services.

## Utilities and tooling

Supporting scripts live under `tools/`, `scripts/`, and `dsl/` for tasks such as seeding environments or generating configurations. The `docker/` directory contains container assets that mirror production-like environments.
