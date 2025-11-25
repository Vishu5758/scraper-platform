from __future__ import annotations

from typing import Optional, Dict, Any, List, Tuple

from fastapi import APIRouter, Query, Header
from psycopg2.extras import RealDictCursor

from src.common import db
from src.common.logging_utils import get_logger

log = get_logger("audit-api")

router = APIRouter(prefix="/api/audit", tags=["audit"])


def _build_filters(
    *,
    event_type: Optional[str],
    source: Optional[str],
    run_id: Optional[str],
) -> Tuple[str, List[Any]]:
    clauses = ["1=1"]
    params: List[Any] = []
    if event_type:
        clauses.append("event_type = %s")
        params.append(event_type)
    if source:
        clauses.append("source = %s")
        params.append(source)
    if run_id:
        clauses.append("run_id = %s")
        params.append(run_id)
    return " AND ".join(clauses), params


def _serialize_event(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(row["id"]),
        "event_type": row["event_type"],
        "source": row.get("source"),
        "run_id": row.get("run_id"),
        "payload": row.get("payload") or {},
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
    }


@router.get("/events")
def get_audit_events(
    event_type: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    run_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-Id"),
) -> dict:
    """
    Fetch audit trail events from Postgres.
    
    Tenant isolation: If tenant_id is provided, only returns events for that tenant.
    If not provided, returns events for 'default' tenant.
    """
    # Enforce tenant isolation - default to 'default' if not provided
    effective_tenant_id = tenant_id or "default"
    
    where_clause, params = _build_filters(event_type=event_type, source=source, run_id=run_id)
    
    # Add tenant_id filter
    where_clause = f"{where_clause} AND tenant_id = %s"
    params.append(effective_tenant_id)

    with db.transaction() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT id, event_type, source, run_id, payload, created_at
                FROM scraper.audit_events
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                (*params, limit, offset),
            )
            rows = cur.fetchall()

            cur.execute(
                f"SELECT COUNT(*) AS total FROM scraper.audit_events WHERE {where_clause}",
                params,
            )
            total = cur.fetchone()["total"]

    return {
        "events": [_serialize_event(row) for row in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
        "tenant_id": effective_tenant_id,
    }

