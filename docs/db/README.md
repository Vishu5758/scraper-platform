# Database Notes

The platform relies on database helpers in `src/db` to manage connections, migrations, and ORM models. When running locally with Docker Compose, databases are provisioned automatically; point the backend to the provided connection strings via environment variables.

For production deployments:

- Apply migrations or seed scripts packaged in `scripts/` or `tools/` before enabling schedulers.
- Keep credentials and secrets outside of the repository, injecting them at runtime through environment variables or secret managers referenced by `src/security`.
