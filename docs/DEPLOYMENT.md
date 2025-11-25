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

