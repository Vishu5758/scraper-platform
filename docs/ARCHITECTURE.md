# Architecture Overview

This document describes the major components of the scraper platform, how data flows between them, and where to extend or observe behavior. Use it as a roadmap before modifying modules.

## System layers

- **Entry and control plane**
  - `src/api` exposes HTTP/JSON endpoints for job control and status queries.
  - `src/client_api` offers client libraries that mirror the server endpoints.
  - `src/entrypoints` packages CLIs and service starters for local and containerized runs.
- **Execution plane**
  - `src/scrapers` defines site-specific logic and reusable scraper primitives.
  - `src/engines` hosts browser/HTTP runtimes and concurrency controls.
  - `src/processors` provides enrichment, cleanup, and transformation steps.
- **Orchestration and pipelines**
  - `src/orchestration`, `src/pipeline_pack`, and `src/scheduler` manage job graphs, dependencies, retries, and handoff between stages.
  - `dags/` contains Airflow DAGs that wrap the same primitives for batch scheduling.
- **Data and state**
  - `src/db` manages connections and models; `src/exporters` ships data to downstream systems.
  - `schemas/` defines payload contracts; `src/validation` enforces them at runtime.
- **Governance and observability**
  - `src/audit`, `src/compliance`, and `src/security` implement policy, auditing, and secret handling.
  - `src/observability`, `src/run_tracking`, and `src/validation` provide metrics, logging, tracing, and run health checks.
- **Extensibility**
  - Optional connectors live in `src/integrations` and `src/plugins`. Machine-learning assisted flows belong to `src/ml`.

## Data flow (typical run)

1. A job is created via API, CLI, or scheduled trigger.
2. The orchestrator resolves dependencies and assigns work to an engine (`src/engines`).
3. Scraper implementations fetch data, applying throttling and anti-bot techniques as needed.
4. Processors enrich, clean, and validate data using schemas from `schemas/`.
5. Validated payloads are persisted via `src/db` and optionally exported through `src/exporters`.
6. Observability hooks emit logs/metrics/traces; audit trails capture compliance events.

## Concurrency and reliability

- Retries and backoff policies are centralized in orchestration modules; adhere to existing strategies when adding new tasks.
- Circuit breakers, timeouts, and rate limits should be configured through `src/config` and enforced within `src/engines` and `src/scrapers`.
- Health checks and run status tracking are surfaced through `src/run_tracking` and API endpoints for dashboards.

## Configuration strategy

- Environment-driven configuration is the default; secrets and tokens must be injected from the runtime environment.
- Shared configuration schemas live in `schemas/`; defaults may be provided via `src/config` utilities.
- Feature flags or experimental flows belong in `src/plugins` or `src/integrations` with guarded rollout paths.

## Frontend integration

- The dashboard in `frontend-dashboard` consumes API endpoints from `src/api` and displays run history, logs, and configuration views.
- Build-time environment files (e.g., `.env.local`) define API hosts and auth scopes used by the React/Vite app.

## Deployment considerations

- Dockerfiles under `docker/` encapsulate runtime dependencies. `docker-compose.yml` provides a baseline stack with databases, Airflow, and the API service.
- Airflow DAGs consume the same package version as the API; keep package versions aligned to avoid contract drift.
- Observability sinks (logging, metrics, traces) should be wired before production rollout to enable run triage.

## How to extend safely

- When adding a scraper, implement it in `src/scrapers` and register it with the orchestrator or relevant DAG.
- Introduce new integrations under `src/integrations` with clear configuration keys and schema updates.
- Update `schemas/` and validators when modifying payload shapes, and ensure exporters handle new fields.
- Add tests in `tests/` for orchestration logic, scraper behavior, and schema changes to prevent regressions.
