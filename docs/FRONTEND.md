# Frontend Dashboard Documentation

The dashboard (`frontend-dashboard/`) is a React + Vite application for monitoring and controlling the scraper platform.

---

## 1. Overview

The dashboard interacts with backend API endpoints to show:

- Live scraper runs
- Run histories and logs
- Pipeline configuration
- Engine health
- Proxy status
- Error breakdowns
- Data export summaries

---

## 2. Development Setup

### Install dependencies

cd frontend-dashboard
npm install

shell
Copy code

### Start development server

npm run dev

mathematica
Copy code

Default URL:

http://localhost:5173

yaml
Copy code

---

## 3. Environment Variables

Create `.env.local`:

VITE_API_BASE_URL=http://localhost:8080/api
VITE_AUTH_TOKEN=<optional>

yaml
Copy code

---

## 4. Folder Structure

frontend-dashboard/
src/
components/
pages/
hooks/
services/
api.ts
stores/

yaml
Copy code

---

## 5. API Calls

The dashboard consumes backend routes such as:

GET /api/runs
GET /api/runs/{id}
GET /api/pipelines
POST /api/run/{source}
GET /api/status

yaml
Copy code

---

## 6. Build for Production

npm run build

yaml
Copy code

Output stored in:

frontend-dashboard/dist/

yaml
Copy code

Integrate via Nginx or serve via container.

---

## 7. Deployment Options

- Docker / docker-compose  
- Kubernetes Ingress  
- Nginx static hosting behind API  

---

This frontend serves as the primary visibility interface for operations and development teams.
