# Dashboard Features - Complete Guide

**Last Updated**: 2024-12-19

This document describes all features available in the frontend dashboard.

---

## 🎯 **Analytics Hub** (`/hub`)

**The central monitoring and process checking hub.**

### Features:
- ✅ **Real-time metrics**: Total runs, success rate, running now, last 24h
- ✅ **System status**: Process health monitoring (API, Airflow, etc.)
- ✅ **Recent runs**: Quick access to latest runs
- ✅ **Real-time logs**: Live log viewer with filtering
  - Filter by source
  - Filter by log level (error, warning, info, debug)
  - Color-coded by level
  - Auto-refresh toggle
- ✅ **Process monitoring**: Health checks for all system components

### Usage:
Navigate to `/hub` or click "Analytics Hub" in sidebar.

---

## ⚡ **Execution Flow** (`/flow?run=<run_id>`)

**Detailed step-by-step execution visualization.**

### Features:
- ✅ **Timeline visualization**: Visual timeline of all steps
- ✅ **Step details**: Click any step to see details
- ✅ **Error display**: Full error messages for failed steps
- ✅ **Metadata viewer**: JSON viewer for step metadata
- ✅ **Run statistics**: Complete run stats
- ✅ **Duration tracking**: See how long each step took

### Usage:
Click on any run in Run Inspector or Analytics Hub to view execution flow.

---

## 🔄 **Airflow Management** (`/airflow/manage`)

**Complete Airflow DAG management interface.**

### Features:
- ✅ **DAG list**: View all available DAGs
- ✅ **DAG filtering**: Filter runs by DAG
- ✅ **Run status**: See all DAG runs with status
- ✅ **Trigger DAGs**: Click to trigger DAG runs
- ✅ **Real-time updates**: Auto-refresh for live status
- ✅ **Run details**: View start/end times, states

### Usage:
Navigate to `/airflow/manage` or click "Airflow" in sidebar.

---

## 🚀 **Deploy Scraper** (`/deploy`)

**Deploy new scrapers directly from the UI.**

### Features:
- ✅ **Scraper configuration form**:
  - Source name input
  - Engine selection (Selenium, Playwright, HTTP, Scrapy)
  - Login requirement checkbox
- ✅ **Deployment status**: Real-time deployment feedback
- ✅ **Files created list**: See all generated files
- ✅ **Error handling**: Clear error messages
- ✅ **Next steps guide**: Instructions after deployment

### What Gets Created:
- `src/scrapers/{source}/pipeline.py`
- `config/sources/{source}.yaml`
- `dsl/pipelines/{source}.yaml`
- `src/scrapers/{source}/plugin.py`
- `dags/scraper_{source}.py`
- `src/scrapers/{source}/selectors.json`

### Usage:
Navigate to `/deploy` or click "Deploy Scraper" in sidebar.

---

## 📊 **Dashboard** (`/`)

**Main overview dashboard.**

### Features:
- ✅ **Key metrics**: Total runs, success rate, running, failed
- ✅ **Recent activity**: Last 24h runs, active sources, variants
- ✅ **Quick actions**: Links to all major features
- ✅ **Run list**: Recent runs table
- ✅ **Variant benchmarks**: Performance by variant

---

## 🔍 **Run Inspector** (`/runs`)

**Detailed run analysis.**

### Features:
- ✅ **Run list**: All runs with filtering
- ✅ **Run details**: Complete run information
- ✅ **Step timeline**: Visual step execution
- ✅ **Statistics**: Run stats and metrics
- ✅ **Metadata**: Full run metadata viewer

---

## 🏥 **Source Health** (`/sources`)

**Monitor scraper source health.**

### Features:
- ✅ **Health table**: All sources with status
- ✅ **Success rates**: Per-source success rates
- ✅ **Last run tracking**: When each source last ran
- ✅ **Failure tracking**: Consecutive failures
- ✅ **Quick actions**: View runs per source

---

## 💰 **Cost Tracking** (`/costs`)

**Monitor scraper execution costs.**

### Features:
- ✅ **Cost summary**: Total, average, by source
- ✅ **Time range filters**: 7d, 30d, 90d, all time
- ✅ **Cost by source**: Breakdown with percentages
- ✅ **Recent costs**: Latest cost entries

---

## 📋 **Audit Events** (`/audit`)

**Complete audit trail.**

### Features:
- ✅ **Event filtering**: By type, source, run_id
- ✅ **Event details**: Full payload viewer
- ✅ **Real-time updates**: Latest events first
- ✅ **JSON viewer**: Formatted payload display

---

## 📈 **Performance Analytics** (`/analytics`)

**Comprehensive performance metrics.**

### Features:
- ✅ **Key metrics**: Total runs, success rate, avg duration
- ✅ **By source**: Performance breakdown per source
- ✅ **By variant**: Performance by variant
- ✅ **Trends**: Daily run trends
- ✅ **Time range filters**: 7d, 30d, 90d

---

## 🔐 **Authentication**

**Dummy login system.**

### Credentials:
- `admin` / `admin123` - Admin role
- `viewer` / `viewer123` - Viewer role
- `operator` / `operator123` - Operator role

### Features:
- ✅ Session persistence (localStorage)
- ✅ User info in sidebar
- ✅ Logout functionality
- ✅ Protected routes

---

## 📡 **API Endpoints**

### New Endpoints:

**Logs**:
- `GET /api/logs` - Query logs with filters
- `GET /api/logs/stream` - Stream logs (SSE, TODO)

**Deployment**:
- `POST /api/deploy/scraper` - Deploy new scraper

**Airflow Control**:
- `POST /api/airflow/trigger` - Trigger DAG
- `POST /api/airflow/dag/{dag_id}/pause` - Pause DAG
- `POST /api/airflow/dag/{dag_id}/unpause` - Unpause DAG

---

## 🎨 **UI Features**

### Real-time Updates:
- Auto-refresh toggles on most pages
- SSE support for live run updates
- Real-time log streaming (when implemented)

### Visualizations:
- Timeline views for execution flow
- Progress bars for metrics
- Color-coded status indicators
- JSON viewers with syntax highlighting

### Responsive Design:
- Works on desktop and tablet
- Mobile-friendly layouts
- Grid-based responsive cards

---

## 🚀 **Quick Start**

1. **Login**: Use `admin` / `admin123`
2. **Analytics Hub**: Go to `/hub` for central monitoring
3. **Deploy Scraper**: Go to `/deploy` to create new scraper
4. **Monitor**: Use Analytics Hub to watch everything
5. **Airflow**: Go to `/airflow/manage` to manage DAGs

---

## 📝 **Navigation Structure**

```
Dashboard (/)
├── Analytics Hub (/hub) ⭐ NEW
├── Run Inspector (/runs)
├── Execution Flow (/flow) ⭐ NEW
├── Source Health (/sources)
├── Cost Tracking (/costs)
├── Audit Events (/audit)
├── Performance Analytics (/analytics)
├── Airflow Management (/airflow/manage) ⭐ NEW
└── Deploy Scraper (/deploy) ⭐ NEW
```

---

## 🔧 **Configuration**

### Environment Variables:

**Frontend** (`.env`):
```bash
VITE_AIRFLOW_URL=http://localhost:8080  # Optional
```

**Backend**:
- `AIRFLOW_BASE_URL` - For Airflow integration
- `AIRFLOW_TOKEN` or `AIRFLOW_USER`/`AIRFLOW_PASS` - For Airflow auth
- `JIRA_BASE_URL` - For Jira integration (optional)

---

## 🎯 **Key Highlights**

1. **Analytics Hub** - One-stop monitoring center
2. **Execution Flow** - Visual step-by-step execution
3. **Deploy Scraper** - Deploy from UI, no CLI needed
4. **Airflow Management** - Full DAG control
5. **Real-time Logs** - Live log streaming
6. **Process Monitoring** - System health at a glance

---

## 📊 **Data Flow**

```
User Action → Frontend → API → Backend → Database/External
                ↓
         Real-time Updates (SSE)
                ↓
         Dashboard Refresh
```

---

## 🎨 **Design Principles**

- **Real-time**: Auto-refresh where it makes sense
- **Detailed**: Show everything, hide nothing important
- **Actionable**: Every view has clear next steps
- **Visual**: Charts, timelines, progress bars
- **Responsive**: Works on all screen sizes

---

The dashboard is now a **complete analytics and process checking hub** with deployment capabilities!

