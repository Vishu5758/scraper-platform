# Documentation Restructuring Report

## A. Deleted duplicates
- No Markdown files with >85% similarity were retained as duplicates; none required deletion beyond consolidation moves.

## B. Files moved
- `docs/ARCHITECTURE.md` → `docs/architecture/system-overview.md` and `docs/architecture/scraper-architecture.md`
- `docs/ROOT_README.md` → `docs/architecture/system-overview.md`
- `docs/BROWSER_AUTOMATION.md` → `docs/workflows/proxy-management-flow.md`
- `docs/DEPLOYMENT.md` and `docs/deployment/LINUX_DEPLOYMENT.md` → `docs/requirements/technical-requirements.md`
- `docs/FRONTEND.md` and `docs/DASHBOARD_FEATURES.md` → `docs/misc/roadmap.md`
- `docs/frontend/FRONTEND_ENHANCEMENTS.md` → `docs/misc/roadmap.md`
- `docs/CI_DEEPAGENT_INTEGRATION.md` and `docs/JIRA_AIRFLOW_INTEGRATION.md` → `docs/misc/roadmap.md`
- `docs/LLM_INTEGRATION.md`, `docs/LLM_STATUS.md`, `docs/LLM_IMPLEMENTATION_STATUS.md`, and `docs/LLM_QUICK_REFERENCE.md` → `docs/workflows/llm-flow.md`
- `docs/db/README.md` and `docs/db/README_LEGACY.md` → `docs/workflows/db-export-flow.md`
- `docs/status/DEPLOYMENT_STATUS.md`, `docs/status/PRODUCTION_READINESS.md`, and `docs/status/SYSTEM_STATUS.md` → `docs/requirements/v5.0-requirements.md` and `docs/troubleshooting/known-issues.md`
- `docs/validation/END_TO_END_VALIDATION.md` → `docs/workflows/scraper-run-flow.md`
- `docs/validation/GIT_CONFLICT_CHECK.md` → `docs/troubleshooting/debugging-guide.md`
- `docs/gaps/GAP_TO_V5.md`, `docs/gaps/REMAINING_GAPS_V5.md`, and `docs/gaps/GAPS_FIXED_SUMMARY.md` → `docs/changelogs/migration-notes.md` and `docs/requirements/v5.0-requirements.md`
- `docs/gaps/P0_BLOCKERS_FIXED.md`, `docs/gaps/P1_P2_FIXES_SUMMARY.md`, and `docs/gaps/PATCHES_APPLIED.md` → `docs/changelogs/changelog-v4.md` and `docs/changelogs/changelog-v5.md`
- `docs/meta/CODEX.md` → `docs/onboarding/coding-guidelines.md`

## C. New folder structure
```
docs/
├── README.md
├── architecture/
│   ├── orchestration-design.md
│   ├── pipeline-flow.md
│   ├── scraper-architecture.md
│   └── system-overview.md
├── changelogs/
│   ├── changelog-v4.md
│   ├── changelog-v5.md
│   └── migration-notes.md
├── misc/
│   ├── faq.md
│   ├── glossary.md
│   ├── restructuring-report.md
│   └── roadmap.md
├── onboarding/
│   ├── coding-guidelines.md
│   ├── config-standards.md
│   └── new-scraper-onboarding.md
├── requirements/
│   ├── business-requirements.md
│   ├── technical-requirements.md
│   ├── v4.8-requirements.md
│   └── v5.0-requirements.md
├── troubleshooting/
│   ├── debugging-guide.md
│   ├── error-codes.md
│   └── known-issues.md
└── workflows/
    ├── db-export-flow.md
    ├── llm-flow.md
    ├── proxy-management-flow.md
    └── scraper-run-flow.md
```

## D. Ambiguous documents flagged
- None. All previously scattered Markdown files were consolidated into the defined categories; miscellaneous roadmap/FAQ items reside under `docs/misc/` by design.
