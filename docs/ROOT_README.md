# Scraper Platform (Relocated Overview)

This repository hosts the scraper platform codebase, including multiple agent orchestrators, Airflow DAGs, and supporting utilities. This overview was previously the root `README.md` and now lives under `docs/` as part of the consolidated documentation set.

Key entry points:
- `docs/README.md`: Documentation index and onboarding pointers.
- `docs/ARCHITECTURE.md`: High-level system design.
- `config/agents/`: Agent configuration defaults and pipelines.
- `dags/`: Airflow DAGs for orchestrating scraping workflows.

If you are upgrading from a previous drop that included additional status reports, those documents are now organized in `docs/status/`, `docs/validation/`, and `docs/gaps/`. Update them as needed during releases.
