# Database Documentation

The scraper platform uses Postgres/Neon for storing:

- Raw scraper outputs  
- Normalized product records  
- PCID mapping  
- Run metadata (“run tracking”)  
- Audit logs  

---

## 1. Schema Overview

Primary tables:

### `runs`
- run_id (PK)
- source
- status
- started_at
- finished_at
- errors
- metadata (JSON)

### `records_raw`
- id (PK)
- run_id (FK)
- source
- raw_json (JSON)
- created_at

### `records_normalized`
- id (PK)
- run_id (FK)
- product_name
- manufacturer
- strength
- pack_size
- price
- pcid
- pcid_confidence
- created_at

### `audit_events`
- id (PK)
- event_type
- message
- created_at

---

## 2. Migrations

Use Alembic or SQL scripts in `db/migrations/`:

alembic upgrade head

yaml
Copy code

---

## 3. Connection Handling

Backend retrieves DSN via:

SCRAPER_DB_DSN=postgresql://user:pass@host/dbname

yaml
Copy code

Connections are handled through `src/db/connection.py`.

---

## 4. Export Flows

Output tables are used by:

- `src/exporters/db_exporter.py`
- dashboards
- external systems (CSV/JSON export)

---

This guide covers core DB concepts & usage patterns.
