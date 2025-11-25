# Agentic Codex Master Prompt for Scraper Platform

This document packages a reusable Codex-style prompt to refactor the scraper platform into an agentic execution engine. Paste it as the system/high-level instruction when guiding a code model.

## Target Agentic Architecture

**Goal:** Turn the current scraper platform into an agentic execution engine where scrapers, LLMs, and tools are orchestrated as agents with clear roles and a pluggable execution graph.

### Core Concepts
- **AgentOrchestrator**
  - Loads YAML plan per source, builds an execution graph (nodes = agents, edges = data flow), runs sequentially or in parallel, and handles retries/timeouts/logging.
- **Agent Registry**
  - Maps agent names to implementations (e.g., `http_fetch_agent`, `browser_fetch_agent`, `html_parse_agent`, `pdf_parse_agent`, `llm_normalizer_agent`, `pcid_matcher_agent`, `qc_validator_agent`, `db_export_agent`).
- **Agent Interface**
  - Unified signature:
    ```python
    class BaseAgent(ABC):
        name: str

        def run(self, context: AgentContext) -> AgentContext:
            ...
    ```
  - `AgentContext` is a dict-like blackboard shared across agents.
- **Execution Graph / Plan**
  - YAML per source, e.g.:
    ```yaml
    sources:
      alfabeta:
        pipeline:
          - agent: http_fetch_agent
          - agent: html_parse_agent
          - agent: llm_normalizer_agent
          - agent: pcid_matcher_agent
          - agent: qc_validator_agent
          - agent: db_export_agent
    ```
  - Supports parallel blocks:
    ```yaml
    - parallel:
        - agent: http_fetch_agent
        - agent: api_fetch_agent
    ```
- **Parallel & Ensemble Patterns**
  - Orchestrator supports `parallel` blocks (run multiple agents at once) and `ensemble` blocks (run several agents and choose best) with per-agent retry policy.
- **Framework Minimalism**
  - Pure Python; no LangGraph/Haystack/Prefect. Airflow remains scheduler; orchestrator lives in `src/agents/`.

### Proposed Folder Structure
```
scraper-platform/
├── config/
│   ├── settings.yaml
│   ├── env/
│   │   ├── dev.yaml
│   │   ├── staging.yaml
│   │   └── prod.yaml
│   ├── sources/
│   │   ├── alfabeta.yaml
│   │   └── ...
│   └── agents/
│       ├── defaults.yaml
│       └── pipelines.yaml
├── src/
│   ├── agents/
│   │   ├── base.py
│   │   ├── orchestrator.py
│   │   ├── registry.py
│   │   ├── http_agent.py
│   │   ├── browser_agent.py
│   │   ├── html_parse_agent.py
│   │   ├── pdf_parse_agent.py
│   │   ├── llm_normalizer_agent.py
│   │   ├── pcid_matcher_agent.py
│   │   ├── qc_agent.py
│   │   └── db_export_agent.py
│   ├── engines/
│   ├── scrapers/
│   ├── llm/
│   ├── retrieval/
│   └── utils/
├── dags/
│   ├── scraper_<source>.py
│   └── agent_orchestrator.py
└── ...
```

## Codex Prompt (pasteable)

You are an expert software architect and senior Python engineer.

You are working on this repository:

`/mnt/data/scraper-platform-main (2).zip`

This codebase is a web-scraping platform with Airflow DAGs, per-source configs, engines, and DB exporters. The current architecture is mostly linear and imperative. There is no real multi-agent/agentic execution layer yet.

Your task is to refactor and extend this repository to implement a clean, modular agentic execution architecture while keeping existing functionality backward compatible as much as possible.

### 1. Target Architecture
Implement the following core components inside `src/agents/`:

1. **`base.py`**
   - Define `AgentContext` (dict-like shared state with nested keys, type hints, get/set/merge) and `BaseAgent` ABC.
   - Optional `AgentConfig` dataclass for per-agent settings (timeouts, retries, etc.).

2. **`registry.py`**
   - `AgentRegistry` maps `agent_name -> BaseAgent` subclass/factory with `register`, `get`, `list_agents`. Auto-register built-ins on import.

3. **`orchestrator.py`**
   - `AgentOrchestrator` loads pipeline config, supports simple steps, `parallel`, and `ensemble` blocks, runs in parallel where specified, and centralizes logging/error handling/retries/timeouts.

4. **Built-in agents**
   - Thin wrappers around existing engines/utilities: `HttpFetchAgent`, `BrowserFetchAgent`, `HtmlParseAgent`, `PdfParseAgent`, `LlmNormalizerAgent`, `PcidMatcherAgent`, `QcAgent`, `DbExportAgent`.
   - Agents read/write via `AgentContext` (e.g., `raw_html`, `records`, `normalized_records`, `pcid_matches`) and log actions.

### 2. Configuration
- Under `config/agents/`, add `defaults.yaml` (global agent policies: timeouts/retries/backoff/parallelism) and `pipelines.yaml` (per-source pipelines; include at least one real source like `alfabeta`).
- Example pipelines entry:
  ```yaml
  sources:
    alfabeta:
      pipeline:
        - agent: http_fetch_agent
        - agent: html_parse_agent
        - agent: llm_normalizer_agent
        - agent: pcid_matcher_agent
        - agent: qc_agent
        - agent: db_export_agent
  ```
- Ensure existing config loader also loads these agent configs for `AgentOrchestrator`.

### 3. Airflow Integration
- Create/update `dags/agent_orchestrator.py` to read `source_name` params, build `AgentContext` (job metadata, run id, date range, source config path), instantiate `AgentOrchestrator` with registry + pipelines config, and call `run_pipeline`.
- Update existing `scraper_<source>.py` DAGs to call the orchestrator; scrapers become thin wrappers or map old functions to agents.

### 4. Backward Compatibility and Cleanup
- Do not break existing paths. Extract scraper internals into agents where sensible, leaving compatibility layers. Remove files only when certain they are unused.

### 5. Quality, Style, and Tests
- Python 3.10+ type hints; use `logging` instead of `print`; keep classes/functions focused.
- Add unit tests for `AgentContext`, `AgentRegistry`, and `AgentOrchestrator` (simple, parallel, ensemble pipelines). Integrate with existing `tests/` if present.
- Ensure imports are correct and code passes `pytest` (or current runner).

### 6. Order of Work (do in sequence)
1. Create `src/agents/base.py`, `src/agents/registry.py`, `src/agents/orchestrator.py`.
2. Add `config/agents/defaults.yaml` and `config/agents/pipelines.yaml`.
3. Implement minimal agents: `HttpFetchAgent`, `HtmlParseAgent`, `DbExportAgent`.
4. Migrate one concrete source (e.g., `alfabeta`) end-to-end to the pipeline.
5. Update one Airflow DAG to use `AgentOrchestrator`.
6. Add tests for context/registry/orchestrator.
7. Extend agent set (`llm_normalizer_agent`, `pcid_matcher_agent`, `qc_agent`, `pdf_parse_agent`, `browser_agent`) using existing code.
8. Gradually refactor remaining scrapers to pipelines.

### 7. Constraints
- Reuse existing business logic; wrap/refactor rather than rewrite. Keep Airflow as scheduler; orchestrator stays in `src/agents/`.
- Avoid heavy frameworks (LangGraph, Haystack, Prefect). Keep dependencies minimal and Pythonic.
