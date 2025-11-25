"""
Common helpers for scraper DAGs.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from src.entrypoints.run_pipeline import run_pipeline
from src.integrations.jira_airflow_integration import get_integration_service


def _extract_dag_conf(context: Dict[str, Any]) -> Dict[str, Any]:
    dag_run = context.get("dag_run") if context else None
    conf = getattr(dag_run, "conf", None) or {}
    return conf if isinstance(conf, dict) else {}


def _build_task_callable(source: str):
    def _task_callable(**context: Any) -> Dict[str, Any]:
        conf = _extract_dag_conf(context)
        dag_run = context.get("dag_run")
        dag_run_id = dag_run.dag_run_id if dag_run else None

        run_type = conf.get("run_type", "FULL_REFRESH")
        params = conf.get("params", {})
        environment = conf.get("environment", "prod")
        jira_issue_key = conf.get("jira_issue_key")

        result = run_pipeline(
            source=conf.get("source", source),
            run_type=run_type,
            params=params,
            environment=environment,
            jira_issue_key=jira_issue_key,
            airflow_dag_run_id=dag_run_id,
        )

        if jira_issue_key:
            integration_service = get_integration_service()
            if integration_service:
                integration_service.update_jira_on_completion(
                    issue_key=jira_issue_key,
                    status=result["status"],
                    run_id=result["run_id"],
                    dag_run_id=dag_run_id,
                    item_count=result.get("item_count"),
                    error=result.get("error"),
                )

        if result["status"] == "failed":
            raise RuntimeError(result.get("error") or "Pipeline run failed")

        return result

    return _task_callable


def build_scraper_dag(
    *,
    source: str,
    dag_id: str,
    description: str,
    schedule: Optional[str],
    tags: Optional[list[str]] = None,
    start_days_ago: int = 1,
) -> DAG:
    default_args = {
        "owner": "scraper",
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=10),
    }

    dag = DAG(
        dag_id=dag_id,
        description=description,
        default_args=default_args,
        schedule_interval=schedule,
        start_date=days_ago(start_days_ago),
        catchup=False,
        tags=tags or ["scraper", source],
    )

    with dag:
        PythonOperator(
            task_id=f"run_{source}_pipeline",
            python_callable=_build_task_callable(source),
            provide_context=True,
        )

    return dag

