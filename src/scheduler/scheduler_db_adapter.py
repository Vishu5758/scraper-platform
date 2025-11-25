# src/scheduler/scheduler_db_adapter.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import threading
from contextlib import contextmanager
from typing import Dict, List, Optional

from psycopg2.extras import Json, RealDictCursor

from src.common import db
from src.common.logging_utils import get_logger
from src.observability.run_trace_context import get_current_tenant_id

log = get_logger("scheduler-db-adapter")

RUNS_TABLE = "scraper.run_tracking_runs"
STEPS_TABLE = "scraper.run_tracking_steps"

_SCHEMA_INITIALIZED = False
_SCHEMA_LOCK = threading.Lock()


def _resolve_tenant_id(tenant_id: Optional[str]) -> str:
    return tenant_id or get_current_tenant_id() or "default"


def _ensure_schema() -> None:
    global _SCHEMA_INITIALIZED
    if _SCHEMA_INITIALIZED:
        return
    with _SCHEMA_LOCK:
        if _SCHEMA_INITIALIZED:
            return
        conn = db.get_conn()
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS scraper")
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {RUNS_TABLE} (
                    run_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    tenant_id TEXT NOT NULL DEFAULT 'default',
                    status TEXT NOT NULL,
                    started_at TIMESTAMPTZ NOT NULL,
                    finished_at TIMESTAMPTZ,
                    duration_seconds INTEGER,
                    stats JSONB,
                    metadata JSONB
                )
                """
            )
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {STEPS_TABLE} (
                    step_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES {RUNS_TABLE}(run_id),
                    tenant_id TEXT NOT NULL DEFAULT 'default',
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMPTZ NOT NULL,
                    duration_seconds INTEGER
                )
                """
            )
            cur.execute(
                f"CREATE INDEX IF NOT EXISTS idx_run_tracking_runs_tenant_started ON {RUNS_TABLE} (tenant_id, started_at DESC)"
            )
            cur.execute(
                f"CREATE INDEX IF NOT EXISTS idx_run_tracking_steps_tenant_run ON {STEPS_TABLE} (tenant_id, run_id)"
            )
        conn.commit()
        _SCHEMA_INITIALIZED = True


@contextmanager
def transaction():
    _ensure_schema()
    with db.transaction() as conn:
        yield conn


@dataclass
class SourceRunMetricsRow:
    source: str
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_change_ratio: float
    consecutive_failures: int
    budget_exhausted: bool


def fetch_source_metrics(tenant_id: Optional[str] = None) -> List[SourceRunMetricsRow]:
    """Fetch source health metrics, optionally filtered by tenant_id."""
    _ensure_schema()
    effective_tenant_id = _resolve_tenant_id(tenant_id)
    
    conn = db.get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            SELECT
                source,
                MAX(started_at) AS last_run_at,
                MAX(finished_at) FILTER (WHERE status = 'success') AS last_success_at,
                COUNT(*) FILTER (WHERE status != 'success' AND started_at > NOW() - INTERVAL '7 days') AS consecutive_failures
            FROM {RUNS_TABLE}
            WHERE tenant_id = %s
            GROUP BY source
            """,
            (effective_tenant_id,),
        )
        rows = cur.fetchall()

    metrics: List[SourceRunMetricsRow] = []
    for row in rows:
        metrics.append(
            SourceRunMetricsRow(
                source=row["source"],
                last_run_at=row["last_run_at"],
                last_success_at=row["last_success_at"],
                last_change_ratio=0.0,
                consecutive_failures=int(row.get("consecutive_failures") or 0),
                budget_exhausted=False,
            )
        )
    return metrics


@dataclass
class RunSummaryRow:
    run_id: str
    source: str
    tenant_id: str
    status: str
    started_at: datetime
    duration_seconds: Optional[int]
    metadata: Optional[Dict[str, object]] = None


@dataclass
class RunDetailRow(RunSummaryRow):
    finished_at: Optional[datetime] = None
    stats: Optional[Dict[str, object]] = None


@dataclass
class RunStepRow:
    step_id: str
    name: str
    status: str
    started_at: datetime
    duration_seconds: Optional[int]


@dataclass
class RunStatsRow:
    run_id: str
    source: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime]
    duration_seconds: Optional[int]
    stats: Optional[Dict[str, object]] = None
    metadata: Optional[Dict[str, object]] = None


def fetch_run_summaries(*, tenant_id: Optional[str] = None) -> List[RunSummaryRow]:
    _ensure_schema()
    conn = db.get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = f"""
            SELECT run_id, source, tenant_id, status, started_at, duration_seconds, metadata
            FROM {RUNS_TABLE}
        """
        params: List[object] = []
        resolved_tenant = tenant_id or get_current_tenant_id()
        if resolved_tenant:
            query += " WHERE tenant_id = %s"
            params.append(resolved_tenant)
        query += " ORDER BY started_at DESC"
        cur.execute(query, params)
        rows = cur.fetchall()

    return [
        RunSummaryRow(
            run_id=row["run_id"],
            source=row["source"],
            tenant_id=row["tenant_id"],
            status=row["status"],
            started_at=row["started_at"],
            duration_seconds=row["duration_seconds"],
            metadata=row.get("metadata"),
        )
        for row in rows
    ]


def fetch_run_detail(run_id: str, *, tenant_id: Optional[str] = None) -> Optional[RunDetailRow]:
    _ensure_schema()
    conn = db.get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            SELECT run_id, source, tenant_id, status, started_at, finished_at, duration_seconds, stats, metadata
            FROM {RUNS_TABLE}
            WHERE run_id = %s AND tenant_id = %s
            """,
            (run_id, _resolve_tenant_id(tenant_id)),
        )
        row = cur.fetchone()

    if not row:
        return None

    return RunDetailRow(
        run_id=row["run_id"],
        source=row["source"],
        tenant_id=row["tenant_id"],
        status=row["status"],
        started_at=row["started_at"],
        finished_at=row["finished_at"],
        duration_seconds=row["duration_seconds"],
        stats=row.get("stats"),
        metadata=row.get("metadata"),
    )


def fetch_run_steps(run_id: str, *, tenant_id: Optional[str] = None) -> List[RunStepRow]:
    _ensure_schema()
    conn = db.get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            SELECT step_id, name, status, started_at, duration_seconds
            FROM {STEPS_TABLE}
            WHERE run_id = %s AND tenant_id = %s
            ORDER BY started_at
            """,
            (run_id, _resolve_tenant_id(tenant_id)),
        )
        rows = cur.fetchall()

    return [
        RunStepRow(
            step_id=row["step_id"],
            name=row["name"],
            status=row["status"],
            started_at=row["started_at"],
            duration_seconds=row["duration_seconds"],
        )
        for row in rows
    ]


def fetch_runs_with_stats(source: Optional[str] = None, tenant_id: Optional[str] = None) -> List[RunStatsRow]:
    """
    Fetch runs with stats, optionally filtered by source and tenant.
    
    Args:
        source: Optional source filter
        tenant_id: Optional tenant_id for isolation (defaults to 'default')
    """
    _ensure_schema()
    conn = db.get_conn()
    effective_tenant_id = tenant_id or "default"
    
    query = f"""
        SELECT run_id, source, status, started_at, finished_at, duration_seconds, stats, metadata
        FROM {RUNS_TABLE}
    """
    params: List[object] = []
    where_clauses = []
    
    # Add tenant filter if tenant_id column exists
    try:
        if "." in RUNS_TABLE:
            table_schema, table_name = RUNS_TABLE.split(".", 1)
        else:
            table_schema, table_name = "public", RUNS_TABLE

        with conn.cursor() as check_cur:
            check_cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = %s
                AND table_name = %s
                AND column_name = 'tenant_id'
                """,
                (table_schema, table_name),
            )
            has_tenant_id = check_cur.fetchone() is not None
        
        if has_tenant_id:
            where_clauses.append("tenant_id = %s")
            params.append(effective_tenant_id)
    except Exception:
        pass  # If check fails, assume no tenant_id column
    
    if source:
        where_clauses.append("source = %s")
        params.append(source)
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " ORDER BY started_at DESC"

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

    return [
        RunStatsRow(
            run_id=row["run_id"],
            source=row["source"],
            status=row["status"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            duration_seconds=row["duration_seconds"],
            stats=row.get("stats"),
            metadata=row.get("metadata"),
        )
        for row in rows
    ]


def _upsert_run(
    conn,
    *,
    run_id: str,
    source: str,
    tenant_id: Optional[str],
    status: str,
    started_at: datetime,
    finished_at: Optional[datetime],
    duration_seconds: Optional[int],
    stats: Optional[Dict[str, object]],
    metadata: Optional[Dict[str, object]],
) -> None:
    resolved_tenant = _resolve_tenant_id(tenant_id)
    with conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO {RUNS_TABLE} (
                run_id, source, tenant_id, status, started_at, finished_at,
                duration_seconds, stats, metadata
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (run_id) DO UPDATE SET
                status = EXCLUDED.status,
                finished_at = EXCLUDED.finished_at,
                duration_seconds = EXCLUDED.duration_seconds,
                stats = EXCLUDED.stats,
                metadata = EXCLUDED.metadata,
                tenant_id = EXCLUDED.tenant_id
            """,
            (
                run_id,
                source,
                resolved_tenant,
                status,
                started_at,
                finished_at,
                duration_seconds,
                Json(stats) if stats else None,
                Json(metadata) if metadata else None,
            ),
        )


def upsert_run(
    *,
    run_id: str,
    source: str,
    tenant_id: Optional[str] = None,
    status: str,
    started_at: datetime,
    finished_at: Optional[datetime] = None,
    duration_seconds: Optional[int] = None,
    stats: Optional[Dict[str, object]] = None,
    metadata: Optional[Dict[str, object]] = None,
    conn=None,
) -> None:
    _ensure_schema()
    try:
        if conn is None:
            with transaction() as txn:
                _upsert_run(
                    txn,
                    run_id=run_id,
                    source=source,
                    tenant_id=tenant_id,
                    status=status,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_seconds=duration_seconds,
                    stats=stats,
                    metadata=metadata,
                )
        else:
            _upsert_run(
                conn,
                run_id=run_id,
                source=source,
                tenant_id=tenant_id,
                status=status,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=duration_seconds,
                stats=stats,
                metadata=metadata,
            )
    except Exception:
        log.exception("Failed to upsert run %s", run_id)
        raise


def _record_run_step(
    conn,
    *,
    step_id: str,
    run_id: str,
    name: str,
    status: str,
    tenant_id: Optional[str],
    started_at: datetime,
    duration_seconds: Optional[int],
) -> None:
    resolved_tenant = _resolve_tenant_id(tenant_id)
    with conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO {STEPS_TABLE} (
                step_id, run_id, tenant_id, name, status, started_at, duration_seconds
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (step_id) DO UPDATE SET
                status = EXCLUDED.status,
                duration_seconds = EXCLUDED.duration_seconds
            """,
            (step_id, run_id, resolved_tenant, name, status, started_at, duration_seconds),
        )


def record_run_step(
    *,
    step_id: str,
    run_id: str,
    name: str,
    status: str,
    tenant_id: Optional[str] = None,
    started_at: datetime,
    duration_seconds: Optional[int] = None,
    conn=None,
) -> None:
    _ensure_schema()
    try:
        if conn is None:
            with transaction() as txn:
                _record_run_step(
                    txn,
                    step_id=step_id,
                    run_id=run_id,
                    name=name,
                    status=status,
                    tenant_id=tenant_id,
                    started_at=started_at,
                    duration_seconds=duration_seconds,
                )
        else:
            _record_run_step(
                conn,
                step_id=step_id,
                run_id=run_id,
                name=name,
                status=status,
                tenant_id=tenant_id,
                started_at=started_at,
                duration_seconds=duration_seconds,
            )
    except Exception:
        log.exception("Failed to record run step %s for run %s", step_id, run_id)
        raise


def fetch_run_stats(run_id: str) -> Optional[RunStatsRow]:
    detail = fetch_run_detail(run_id)
    if not detail:
        return None
    return RunStatsRow(
        run_id=detail.run_id,
        source=detail.source,
        status=detail.status,
        started_at=detail.started_at,
        finished_at=detail.finished_at,
        duration_seconds=detail.duration_seconds,
        stats=detail.stats,
        metadata=detail.metadata,
    )


def fetch_runs_for_source(source: str, limit: int = 10, *, tenant_id: Optional[str] = None) -> List[RunSummaryRow]:
    summaries = fetch_run_summaries(tenant_id=tenant_id)
    return [row for row in summaries if row.source == source][:limit]

