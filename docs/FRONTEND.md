# Frontend Dashboard

The dashboard in `frontend-dashboard/` provides visibility into scraper executions and configuration. It is built with React and Vite.

## Local setup

```bash
cd frontend-dashboard
npm install
npm run dev
```

The dev server proxies API calls to the backend; configure API endpoints through the environment files in `frontend-dashboard` as needed.

## Production build

To generate static assets for deployment:

```bash
cd frontend-dashboard
npm run build
```

Serve the generated files from the `dist/` directory via your preferred web server or bundle them into a container alongside the backend API.
