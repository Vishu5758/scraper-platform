# Deployment Guide

This document explains how to deploy the scraper platform locally, in staging, and in production.

---

# 1. Prerequisites

- Docker ≥ 24.0
- Docker Compose ≥ v2
- Python ≥ 3.10
- Node.js ≥ 18 (for dashboard)
- Postgres ≥ 14
- Airflow ≥ 2.7 (optional for batch)

---

# 2. Environment Variables

Create `.env` with:

SCRAPER_ENV=prod
SCRAPER_DB_DSN=postgresql://user:pass@host:5432/scraper
API_PORT=8080
AIRFLOW__CORE__DAGS_FOLDER=/app/dags

yaml
Copy code

Secrets must **never** be stored in the repo.

---

# 3. Local Development (Docker)

docker-compose up --build

yaml
Copy code

Services included:

- API (`src/api`)
- Orchestrator
- Postgres
- Airflow scheduler + webserver
- Prometheus metrics exporter
- React dashboard

Access:
- API → http://localhost:8080
- Airflow → http://localhost:8081
- Dashboard → http://localhost:5173

---

# 4. Running Locally Without Docker

### Install dependencies

pip install -r requirements.txt
cd frontend-dashboard && npm install && npm run dev

shell
Copy code

### Start API server

python -m src.entrypoints.run_api

shell
Copy code

### Trigger a pipeline

python -m src.entrypoints.run_pipeline --source=alfabeta --env=dev

yaml
Copy code

---

# 5. Deploying to Production

## Option A: Docker Compose on VM

1. Copy repo to server
2. Configure environment + secrets via `.env`
3. Run:

docker-compose -f docker-compose.prod.yml up -d --build

yaml
Copy code

## Option B: Kubernetes

- Use manifests under `k8s/` (if present)
- Use secrets manager (Vault/SSM)
- Use ingress for API exposure

## Option C: Airflow-only deployment

- Install `scraper-platform` as pip package
- Load DAGs from `dags/`
- Configure Airflow variables:
  - `SCRAPER_SOURCE`
  - `SCRAPER_ENV`
  - Proxy config
  - DB config

---

# 6. Observability & Monitoring

- Prometheus endpoint: `/metrics`
- Grafana dashboards supported
- Logs streamed to stdout for CloudWatch/ELK
- Health endpoint: `/api/health`

---

# 7. Production Checklist

- [ ] DB migrations applied  
- [ ] Secrets configured  
- [ ] Airflow scheduler healthy  
- [ ] API latency < 200ms  
- [ ] Retry/backoff enabled  
- [ ] Proxy routing validated  
- [ ] Dashboard connected to API  

---

This guide ensures consistent deployment across dev, staging, and production.
