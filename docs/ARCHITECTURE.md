# Scraper Platform – Architecture Overview

This document describes the end-to-end architecture of the scraper platform, its execution model, extensibility points, and system-wide responsibilities.

---

## 1. System Layers

### **1.1 Entry & Control Plane**
- `src/api/` exposes REST endpoints for job creation, run status, health checks, and pipeline triggers.
- `src/client_api/` provides client-side libraries for triggering pipelines safely.
- `src/entrypoints/` offers CLIs and service bootstrappers for local or container execution.

---

### **1.2 Execution Plane**
Responsible for fetching & processing content.

- `src/scrapers/`  
  Site-specific scraper implementations, selectors, pagination logic.

- `src/engines/`  
  - HTTP engine  
  - Playwright engine  
  - Selenium engine  
  - Proxy routing, session/cookie reuse  
  - Retry/backoff logic, anti-bot strategies

- `src/processors/`  
  - HTML → structured data  
  - JSON → normalized rows  
  - PDF → tables  
  - LLM-based normalization  
  - PCID Matching  
  - QC validation

---

### **1.3 Orchestration & Pipelines**
Manages the workflow of scrapes.

- `src/pipeline_pack/`  
  Agentic orchestration engine:
  - `BaseAgent`, `AgentContext`, `AgentRegistry`
  - Agents: `http_fetch`, `html_parse`, `llm_normalizer`, `qc_rules`, `pcid_match`, `db_export`

- `src/orchestration/`  
  High-level pipeline control, error policy, retries.

- `src/scheduler/`  
  Non-Airflow scheduling utilities.

- `dags/`  
  Airflow DAGs wrapping the same pipelines for batch scheduling.

---

### **1.4 Data & State Layer**
Handles persistence and export.

- `src/db/`  
  Database connectors, models, migrations.

- `src/exporters/`  
  - Postgres/Neon exports  
  - CSV/JSON/S3 export  
  - Batched flushers  
  - Run summaries

- `schemas/`  
  Contract definitions for input/output payloads.

- `src/validation/`  
  Runtime schema enforcement and type validation.

---

### **1.5 Governance & Observability**

- `src/audit/` – audit logs, compliance events  
- `src/compliance/` – policy enforcement  
- `src/security/` – secret loading, safe handling  
- `src/observability/` – Prometheus metrics, logs, latencies  
- `src/run_tracking/` – run-level lifecycle tracking

---

### **1.6 Extensibility**

- `src/integrations/` – third-party connectors  
- `src/plugins/` – experimental plugins  
- `src/ml/` – ML utilities, LLM agents, embeddings, PDF parsing

---

## 2. End-to-End Data Flow

1. **A job is triggered** (API/CLI/DAG).
2. **Orchestrator loads pipeline** from `config/agents/pipelines.yaml`.
3. **Engine selection** (HTTP/Playwright/Selenium).
4. **Scraping** with proxy routing & session reuse.
5. **Processors** clean → normalize → validate (QC rules).
6. **PCID Matching** assigns product IDs.
7. **Exporters** persist rows to DB/S3/CSV.
8. **Observability** streams metrics/logs.
9. **Run tracker** records completion status.

---

## 3. Reliability Model

- Centralized retry/backoff  
- Circuit breakers on failing domains  
- Timeout enforcement  
- Proxy rotation to avoid bans  
- Health checks exposed through API  

---

## 4. Configuration

- Environment-first config (`.env`, env vars)
- YAML-based mapping (`config/sources/*.yaml`)
- Schemas in `schemas/` enforce contract consistency

---

## 5. Deployment Architecture

- Docker Compose for local dev  
- Airflow for batch scheduling  
- API service handles runtime pipelines  
- Prometheus/Grafana for observability  
- Centralized logging (stdout + aggregator)

---

## 6. Safe Extension

- Add new scrapers under `src/scrapers/<source>/`
- Add config files under `config/sources/<source>.yaml`
- Register pipeline steps in `pipelines.yaml`
- Update schemas and tests for all payload changes
- Add DAG under `dags/scraper_<source>.py`

---

This is the master architectural reference for maintainers and contributors.
