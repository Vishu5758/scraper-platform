# Frontend Dashboard

The dashboard in `frontend-dashboard/` is a React/Vite application used to monitor runs, configure scrapers, and trigger jobs. This document covers local setup, configuration, and build guidance.

## Project structure

- `src/components` – Shared UI primitives and feature components.
- `src/pages` – Route-driven views (run lists, job detail, configuration screens).
- `src/api` or `src/services` – API clients and hooks that call backend endpoints exposed by `src/api` in the Python services.
- `src/state` – Store/helpers for global state management and feature flags.
- `public/` – Static assets bundled with builds.

## Local setup

```bash
cd frontend-dashboard
npm install
npm run dev
```

- The dev server proxies API calls to the backend. Set `VITE_API_BASE_URL` (or equivalent) in `.env.local` to point to the running API.
- If authentication is required, include tokens or client IDs in the `.env.local` file consumed by the API client layer.

## Development tips

- Use the provided ESLint/TypeScript configuration (if enabled) to maintain consistency.
- Keep API contract types in sync with `schemas/` and backend responses; generate or update types as needed.
- Prefer reusable components in `src/components` and centralized styling to maintain uniform UX.

## Production build and deployment

To generate static assets for deployment:

```bash
cd frontend-dashboard
npm run build
```

The build emits files under `dist/`. Serve them via a CDN, an application server, or a container. When containerizing, copy the build artifacts and configure the container to expose the static files alongside the backend or from a dedicated web server.

### Configuration for production

- Set `VITE_API_BASE_URL` and any auth-related variables at build time.
- Confirm CORS settings in the backend (`src/api`) permit the dashboard origin.
- Enable error monitoring or analytics via environment variables consumed by the dashboard’s client libraries.

## Validating changes

- Run UI/unit tests if available (`npm test` or framework-specific commands).
- Manually verify key flows: loading run history, triggering a job, and viewing logs/metrics.
- When API changes land, smoke test the dashboard against the updated backend before promoting to staging or production.
