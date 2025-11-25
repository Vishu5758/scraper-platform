"""
Airflow DAG for running the AlfaBeta scraper.

This DAG supports:
- Scheduled daily runs (2 AM by default)
- Jira-triggered runs (via webhook integration)

When triggered from Jira, the DAG receives conf with:
- jira_issue_key: Jira issue key
- source: Source name (alfabeta)
- run_type: FULL_REFRESH, DELTA, or SINGLE_PRODUCT
- params: Additional parameters
- environment: dev, staging, or prod
"""

from datetime import timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from src.entrypoints.run_pipeline import run_pipeline
from src.integrations.jira_airflow_integration import get_integration_service


def _extract_dag_conf(context) -> Dict[str, Any]:
    """Extract DAG run configuration from context."""
    dag_run = context.get("dag_run") if context else None
    conf = getattr(dag_run, "conf", None) or {}
    return conf if isinstance(conf, dict) else {}


def _run_alfabeta_pipeline(**context):
    """
    Task callable that runs the AlfaBeta pipeline.

    Supports both scheduled runs and Jira-triggered runs.
    """
    conf = _extract_dag_conf(context)
    dag_run = context.get("dag_run")
    dag_run_id = dag_run.dag_run_id if dag_run else None

    # Extract parameters from conf (Jira-triggered) or use defaults (scheduled)
    source = conf.get("source", "alfabeta")
    run_type = conf.get("run_type", "FULL_REFRESH")
    params = conf.get("params", {})
    environment = conf.get("environment", "prod")
    jira_issue_key = conf.get("jira_issue_key")

    print(f"[AlfaBeta DAG] Starting run - source={source}, run_type={run_type}, env={environment}")
    if jira_issue_key:
        print(f"[AlfaBeta DAG] Jira issue: {jira_issue_key}")

    # Call programmatic entry point
    result = run_pipeline(
        source=source,
        run_type=run_type,
        params=params,
        environment=environment,
        jira_issue_key=jira_issue_key,
        airflow_dag_run_id=dag_run_id,
    )

    # Log results
    print(f"[AlfaBeta DAG] Run completed - status={result['status']}, run_id={result['run_id']}")
    if result.get("item_count"):
        print(f"[AlfaBeta DAG] Items processed: {result['item_count']}")
    if result.get("error"):
        print(f"[AlfaBeta DAG] Error: {result['error']}")

    # Update Jira if this was a Jira-triggered run
    if jira_issue_key:
        integration_service = get_integration_service()
        if integration_service:
            try:
                integration_service.update_jira_on_completion(
                    issue_key=jira_issue_key,
                    status=result["status"],
                    run_id=result["run_id"],
                    dag_run_id=dag_run_id,
                    item_count=result.get("item_count"),
                    error=result.get("error"),
                )
            except Exception as exc:
                print(f"[AlfaBeta DAG] Failed to update Jira: {exc}")

    # Raise exception if run failed (so Airflow marks task as failed)
    if result["status"] == "failed":
        raise RuntimeError(f"Pipeline run failed: {result.get('error', 'Unknown error')}")

    return result


default_args = {
    "owner": "scraper",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="scraper_alfabeta_daily",
    description="Daily AlfaBeta pharma scraper (v4.9)",
    default_args=default_args,
    schedule_interval="0 2 * * *",  # daily at 02:00
    start_date=days_ago(1),
    catchup=False,
    tags=["scraper", "alfabeta", "pharma"],
) as dag:

    run_alfabeta = PythonOperator(
        task_id="run_alfabeta_pipeline",
        python_callable=_run_alfabeta_pipeline,
        provide_context=True,
    )

    # If you add more tasks later (QC, upload, etc.), chain them here:
    # run_alfabeta >> some_other_task
