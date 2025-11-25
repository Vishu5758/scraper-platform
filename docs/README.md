# Scraper Platform Documentation

Welcome to the consolidated documentation hub for the scraper platform. All Markdown guides now live under the `docs/` directory.

---

## Getting Started
- Overview of architecture: `ARCHITECTURE.md`
- Deployment walkthroughs: `DEPLOYMENT.md` and `deployment/LINUX_DEPLOYMENT.md`
- Frontend notes: `FRONTEND.md` and `frontend/FRONTEND_ENHANCEMENTS.md`
- Database reference: `db/README.md`

---

## Documentation Map

### Core Guides
- `ARCHITECTURE.md` – High-level system design and workflows
- `DEPLOYMENT.md` – Local and production deployment guidance
- `FRONTEND.md` – Dashboard architecture and setup
- `BROWSER_AUTOMATION.md` – Engine options and caveats for browser-driven scraping
- `LLM_INTEGRATION.md` & companions (`LLM_STATUS.md`, `LLM_IMPLEMENTATION_STATUS.md`, `LLM_QUICK_REFERENCE.md`) – LLM usage and status tracking
- `CI_DEEPAGENT_INTEGRATION.md`, `JIRA_AIRFLOW_INTEGRATION.md` – CI/CD and ticketing integrations

### Status & Validation
- `status/DEPLOYMENT_STATUS.md`
- `status/PRODUCTION_READINESS.md`
- `status/SYSTEM_STATUS.md`
- `validation/ARCHITECTURE_VALIDATION.md`
- `validation/END_TO_END_VALIDATION.md`
- `validation/GIT_CONFLICT_CHECK.md`

### Gaps, Fixes, and Release Notes
- `gaps/GAP_TO_V5.md`
- `gaps/REMAINING_GAPS_V5.md`
- `gaps/GAPS_FIXED_SUMMARY.md`
- `gaps/P0_BLOCKERS_FIXED.md`
- `gaps/P1_P2_FIXES_SUMMARY.md`
- `gaps/PATCHES_APPLIED.md`

### Deployment Notes
- `deployment/LINUX_DEPLOYMENT.md`

### Frontend & Auxiliary
- `frontend/FRONTEND_ENHANCEMENTS.md`
- `meta/CODEX.md`

---

## Related Resources
- `../src/` – Backend runtime
- `../frontend-dashboard/` – UI dashboard source
- `../dags/` – Airflow pipelines
- `../config/` – Source configs & pipeline definitions
- `../schemas/` – Validation schemas

---

Use this index as the central starting point for contributors and operators.
