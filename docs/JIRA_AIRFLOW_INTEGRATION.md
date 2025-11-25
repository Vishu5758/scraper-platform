# Jira-Airflow-Scraper Platform Integration

This document describes the complete integration between Jira, Airflow, and the Scraper Platform.

## Overview

The integration allows Jira tickets to trigger scraper runs through Airflow, with automatic status updates back to Jira.

## Architecture

```
Jira Ticket → Webhook → Integration Service → Airflow DAG → Scraper Platform → Jira Update
```

## Components

### 1. Integration Service (`src/integrations/`)

- **`jira_client.py`**: Jira API client for reading/updating issues
- **`jira_airflow_integration.py`**: Main integration logic

### 2. Platform Entry Point (`src/entrypoints/`)

- **`run_pipeline.py`**: Programmatic entry point for running pipelines

### 3. API Endpoints (`src/api/routes/integration.py`)

- **`POST /api/integration/jira/webhook`**: Receives Jira webhooks
- **`POST /api/integration/airflow/callback`**: Receives Airflow callbacks

### 4. Airflow DAGs (`dags/`)

- Updated DAGs to handle Jira-triggered runs with context

## Configuration

### Environment Variables

**Jira:**
- `JIRA_BASE_URL`: Jira base URL (e.g., `https://yourcompany.atlassian.net`)
- `JIRA_USERNAME`: Jira username/email
- `JIRA_API_TOKEN`: Jira API token (from https://id.atlassian.com/manage-profile/security/api-tokens)
- `JIRA_WEBHOOK_SECRET`: Secret for validating webhook requests (optional but recommended)

**Airflow:**
- `AIRFLOW_BASE_URL`: Airflow base URL
- `AIRFLOW_TOKEN`: Bearer token (or use `AIRFLOW_USER`/`AIRFLOW_PASS` for basic auth)
- `AIRFLOW_CALLBACK_SECRET`: Secret for validating callback requests (optional but recommended)

## Jira Setup

### 1. Create Custom Fields

You need to create custom fields in Jira:

- **Source** (`customfield_source`): Single-select or text field for scraper source (alfabeta, quebec, lafa)
- **Run Type** (`customfield_run_type`): Single-select with options: FULL_REFRESH, DELTA, SINGLE_PRODUCT
- **Parameters** (`customfield_params`): Multi-line text field for JSON parameters
- **Environment** (`customfield_environment`): Single-select with options: dev, staging, prod
- **Airflow Run ID** (`customfield_airflow_run_id`): Text field (auto-populated)
- **Run Status** (`customfield_run_status`): Single-select (auto-populated)
- **Platform Run ID** (`customfield_run_id`): Text field (auto-populated)

### 2. Configure Webhook

In Jira, create a webhook that triggers on issue transitions:

1. Go to Jira Settings → System → Webhooks
2. Create new webhook
3. URL: `https://your-platform-api.com/api/integration/jira/webhook`
4. Events: Issue updated, Issue created
5. Add header: `X-Webhook-Secret: <your-secret>`

### 3. Workflow Transitions

Configure your Jira workflow to have:
- **"Ready to Run"** status that triggers the webhook
- **"Completed"** status for successful runs
- **"Failed - Needs Investigation"** status for failed runs

## Usage

### Creating a Jira Ticket

1. Create a new issue in your scraper project
2. Fill in required fields:
   - **Source**: e.g., `alfabeta`
   - **Run Type**: e.g., `FULL_REFRESH`
   - **Parameters**: JSON object, e.g., `{"country": "AR", "max_pages": 50}`
   - **Environment**: e.g., `staging`
3. Transition issue to **"Ready to Run"**

### What Happens

1. Jira fires webhook → Integration Service
2. Integration Service validates fields
3. Integration Service triggers Airflow DAG with parameters
4. Airflow executes DAG → calls platform entry point
5. Platform runs scraper pipeline
6. On completion, Airflow updates Jira via callback

### Monitoring

- Check Jira issue comments for status updates
- Check Airflow UI for DAG execution details
- Check platform dashboard for run details

## API Reference

### Webhook Endpoint

**POST** `/api/integration/jira/webhook`

Headers:
- `X-Webhook-Secret`: Webhook secret (if configured)

Body: Jira webhook payload (standard Jira webhook format)

### Callback Endpoint

**POST** `/api/integration/airflow/callback`

Headers:
- `X-Callback-Secret`: Callback secret (if configured)

Body:
```json
{
  "dag_id": "scraper_alfabeta",
  "dag_run_id": "scraper_alfabeta__2025-01-05T10:00:00",
  "source": "alfabeta",
  "run_status": "success",
  "run_id": "RUN-2025-01-05-0001",
  "item_count": 4870,
  "error": null
}
```

## Troubleshooting

### Webhook Not Triggering

- Check Jira webhook configuration
- Verify webhook URL is accessible
- Check webhook secret matches
- Review Integration Service logs

### Airflow DAG Not Starting

- Verify `AIRFLOW_BASE_URL` is correct
- Check Airflow authentication credentials
- Verify DAG exists in Airflow
- Review Airflow logs

### Jira Not Updating

- Verify Jira credentials are correct
- Check custom field IDs match your Jira setup
- Review Integration Service logs for errors
- Verify Jira API token has write permissions

## Database Schema

The integration adds the following fields to `scraper.scraper_runs`:

- `jira_issue_key`: TEXT - Jira issue key
- `airflow_dag_id`: TEXT - Airflow DAG ID
- `airflow_dag_run_id`: TEXT - Airflow DAG run ID
- `run_type`: TEXT - Type of run (FULL_REFRESH, DELTA, SINGLE_PRODUCT)

See `db/migrations/023_jira_airflow_integration.sql` for the migration.

## Security Considerations

1. **Webhook Secrets**: Always use webhook secrets to validate requests
2. **API Tokens**: Store tokens in environment variables or secure vaults
3. **HTTPS**: All API calls should use HTTPS
4. **IP Allowlisting**: Consider IP allowlisting for webhook endpoints
5. **Rate Limiting**: Implement rate limiting on webhook endpoints

## Future Enhancements

- Support for multiple Jira projects
- Automatic retry on failures
- Slack/email notifications
- Run cancellation from Jira
- Parameter validation and schema

