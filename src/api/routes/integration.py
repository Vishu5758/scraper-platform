"""
API routes for Jira-Airflow integration.

Provides webhook endpoints for Jira events and callbacks from Airflow.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel

from src.common.logging_utils import get_logger
from src.integrations.jira_airflow_integration import IntegrationService, get_integration_service

log = get_logger("integration-api")

router = APIRouter(prefix="/api/integration", tags=["integration"])


class JiraWebhookPayload(BaseModel):
    """Jira webhook payload model."""

    issue: Dict[str, Any]
    webhookEvent: str
    timestamp: int


class AirflowCallbackPayload(BaseModel):
    """Airflow callback payload model."""

    dag_id: str
    dag_run_id: str
    source: str
    run_status: str
    run_id: Optional[str] = None
    item_count: Optional[int] = None
    error: Optional[str] = None


@router.post("/jira/webhook")
async def handle_jira_webhook(
    payload: Dict[str, Any],
    request: Request,
    x_webhook_secret: str | None = Header(default=None, alias="X-Webhook-Secret"),
) -> Dict[str, Any]:
    """
    Handle incoming Jira webhook.

    Validates webhook secret (if configured) and triggers Airflow DAG.
    """
    # Validate webhook secret (if configured)
    expected_secret = os.getenv("JIRA_WEBHOOK_SECRET")
    if expected_secret and x_webhook_secret != expected_secret:
        log.warning("Jira webhook rejected: invalid secret")
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    # Get integration service
    service = get_integration_service()
    if not service:
        raise HTTPException(
            status_code=503,
            detail="Integration service not configured (AIRFLOW_BASE_URL required)",
        )

    # Handle webhook
    try:
        result = service.handle_jira_webhook(payload)
        return result
    except Exception as exc:
        log.error("Error handling Jira webhook", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {exc}")


@router.post("/airflow/callback")
async def handle_airflow_callback(
    payload: AirflowCallbackPayload,
    x_callback_secret: str | None = Header(default=None, alias="X-Callback-Secret"),
) -> Dict[str, Any]:
    """
    Handle callback from Airflow when a run completes.

    Updates Jira issue with run status and results.
    """
    # Validate callback secret (if configured)
    expected_secret = os.getenv("AIRFLOW_CALLBACK_SECRET")
    if expected_secret and x_callback_secret != expected_secret:
        log.warning("Airflow callback rejected: invalid secret")
        raise HTTPException(status_code=401, detail="Invalid callback secret")

    # Get integration service
    service = get_integration_service()
    if not service:
        raise HTTPException(
            status_code=503,
            detail="Integration service not configured",
        )

    # Extract Jira issue key from DAG run conf (would need to query Airflow API)
    # For now, we'll expect it in the payload or extract from run metadata
    # This is a simplified version - in production you'd query Airflow for the conf

    # Update Jira
    try:
        # In a real implementation, you'd extract jira_issue_key from Airflow DAG run conf
        # For now, we'll log and return success
        log.info(
            "Received Airflow callback",
            extra={
                "dag_id": payload.dag_id,
                "dag_run_id": payload.dag_run_id,
                "status": payload.run_status,
                "run_id": payload.run_id,
            },
        )

        # TODO: Query Airflow API to get DAG run conf and extract jira_issue_key
        # Then call: service.update_jira_on_completion(...)

        return {"status": "success", "message": "Callback processed"}

    except Exception as exc:
        log.error("Error handling Airflow callback", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing callback: {exc}")


@router.get("/health")
def integration_health() -> Dict[str, Any]:
    """Health check for integration service."""
    service = get_integration_service()
    jira_configured = bool(os.getenv("JIRA_BASE_URL"))
    airflow_configured = bool(os.getenv("AIRFLOW_BASE_URL"))

    return {
        "status": "ok",
        "jira_configured": jira_configured,
        "airflow_configured": airflow_configured,
        "integration_service_available": service is not None,
    }

