# Database Notes

The platform relies on database helpers in `src/db` to manage connections, migrations, and ORM models. This guide outlines how to configure local and production databases safely.

## Local development

- Databases are provisioned via Docker Compose; connection strings are exposed as environment variables consumed by `src/db`.
- Apply any seed scripts in `scripts/` or `tools/` after services start to ensure reference data exists.
- If you adjust models or migrations, run them against the local database before opening a PR to catch contract issues early.

## Configuration

- Set database URLs, usernames, and passwords via environment variables (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, etc.).
- Connection pooling and timeouts should be tuned via configuration helpers in `src/config` and `src/db` to avoid resource exhaustion.
- Keep credentials outside of the repository; use secret managers or environment injection in CI/CD pipelines.

## Migrations and schema changes

- Store migration scripts alongside the codebase (e.g., in `scripts/` or a migrations directory) and execute them before enabling schedulers.
- Align schema versions between Airflow environments and the API service to prevent runtime failures.
- When schemas change, update related validators in `schemas/` and downstream exporters to keep payloads compatible.

## Backups and observability

- Configure automated backups for production databases and test restore procedures regularly.
- Enable query logging or metrics where supported to monitor slow queries and connection usage.
- Audit trails recorded via `src/audit` should land in durable storage with retention policies that match compliance needs.
