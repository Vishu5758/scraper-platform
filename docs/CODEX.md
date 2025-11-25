# Scraper Platform v4.9 Codex

## 0. Name & Scope
- **System name:** `scraper-platform-v4.9`
- **Type:** Multi-source, config-driven scraping platform with DeepAgent-based auto-heal and observability.
- **Scope:** Scrape hundreds of sources (AlfaBeta, Quebec, Lafa, etc.), manage accounts/proxies/sessions at scale, self-heal on DOM drift, and deliver versioned, audited data to CSV/DB targets.

## 1. Stakeholders & Roles
- **Stakeholders:** Product/Platform Owner, Scraper Devs, Infra/DevOps, Data Consumers, Compliance/Security.
- **Roles:** Admin (configs/credentials/flags), Scraper Engineer (onboarding + debugging), Observer/Analyst (dashboards + data), Auto-Heal Agent (selector repair proposals).

## 2. Environments & Deployment
- **Envs:** `dev`, `staging`, `prod` with separate configs under `config/env/`. Each environment owns its DB schema, Airflow namespace, proxies, and account lists.
- **Secrets:** Never in git; source from Vault/env vars. Distinct proxy/account pools per environment.

## 3. Platform Functional Requirements
- **Source onboarding:** Each source needs `config/sources/<source>.yaml`, `src/scrapers/<source>/pipeline.py`, selectors JSON/signature/history, `dags/scraper_<source>.py`, and tests under `src/scrapers/<source>/tests/`. Scaffolding via `tools/add_scraper_advanced.py` creates folders/configs/DAGs and optional snapshot dirs.
- **Config management:** Global `config/settings.yaml` + env overlays; per-source config covers URLs, pagination, login, concurrency, rate limits, output paths, QC thresholds, notifications. Validate on startup and per run.
- **Account & proxy management:** `account_router` maps source→accounts with success/failure tracking and cooldowns. `proxy_router` tracks health (latency/bans/error rates) and rotates unhealthy ones. `account_proxy_binding.json` maintains sticky bindings with override support.
- **Session management:** `sessions/session_manager.py` builds `SessionRecord` (source/account/proxy/timestamps), persists cookies per triple, logs events to `sessions/logs/session_events.jsonl`, and retries with new sessions on invalid cookies/login changes/bans.
- **Engine abstraction:** Selenium/Playwright expose `open_with_session`, `get_dom`, `click`, `wait_for_selector`, `scroll`; HTTP client respects proxy + rate limits. Provide FakeDriver/replay mode for snapshots and auto-heal validation.

## 4. Per-Scraper Pattern
1. **Discovery:** `get_listing_urls()` paginates with jitter, detects >30% volume drop (drift), stores sample listing snapshot; zero listings → fail run + incident log.
2. **Expansion:** `get_product_urls(listing_url)` extracts/ dedupes product links, handles infinite scroll, raises drift alerts on volume deviation, and returns partial results with warnings when degraded.
3. **Extraction:** `extract_product(product_url)` fetches via engine, reads `selectors.json`, applies fallbacks, attaches metadata (source/scrape_time/session_id), retries transient failures, and rejects silent nulls for mandatory fields.
4. **Normalization + QC:** Use `processors/unify_fields.py` and `processors/qc_rules.py`; enforce standard schema, reject impossible values (price ≤ 0, invalid currencies), flag anomalies, and emit valid/invalid/questionable counts.

## 5. DeepAgent / Auto-Heal
- **Drift detection:** `observability/drift_monitor.py` watches volume drops, HTML signature changes vs `schema_signature.json`, and selector failure spikes; saves snapshots, logs drift events to DB, and triggers auto-heal.
- **Auto-heal workflow:** `deepagent_selector_healer` proposes selector updates from DOM snapshots; `deepagent_repair_engine` applies patches in replay (no live scraping) using `tests_replay/replay_runner.py`; `patch_proposer` summarizes diffs/metrics/confidence. No PROD auto-deploy without passing replay tests and explicit approval/config flag.

## 6. Data, DB & Storage
- **Outputs:** CSV under `output/<source>/daily/<source>_YYYY-MM-DD.csv` with fixed delimiter, UTF-8, stable column order; attach version metadata.
- **Database:** Migrations in `db/migrations/*.sql` cover runs, drift events, costs, source health, sessions, versioning, contracts, etc. Every run and drift logged; QC issues recorded at batch/record level; maintain code/selector version traceability.
- **Versioning:** `versioning/version_manager.py` exposes platform (`4.9.x`) and scraper versions, attaches metadata to runs/CSV, and tracks schema versioning.

## 7. Non-Functional Requirements
- **Reliability:** ≥99% availability for run windows; failures isolate to source with explicit FAILED status + reason. Retry transient network errors with backoff; drift triggers fail-fast + auto-heal.
- **Performance/Scale:** Target handling 25k URLs in 24h per source with ~10 accounts; tunable concurrency/proxy budgets; platform scales to 100+ sources/day.
- **Security/Compliance:** No hardcoded credentials; access control for Vault/DB/Airflow; logs must exclude sensitive secrets; support retention/purge per policy.
- **Observability:** Central logs (run/scraper/session), metrics by source/run/proxy/account, alerts for volume drift, error spikes, bans, and cost thresholds.
- **Cost governance:** `observability/cost_tracking.py` estimates proxy/compute cost, enforces per-source max budgets, and can halt runs on threshold breaches.

## 8. Testing & QA
- **Test types:** Unit (helpers/parsing), component (listing/page/product logic), replay (snapshots), integration (DAG→CSV), regression (selector/config changes).
- **Snapshots:** Maintain listing/product/special-case HTML under `snapshots/<source>/...` for replay robustness.
- **Acceptance per source:** Snapshot tests for listings/products pass; extraction yields >95% valid and <5% QC-invalid on known-good data; replay runs crash-free; end-to-end dry run produces CSV + DB rows + metrics.

## 9. Operations & Incident Handling
- **Runbook:** Steps to trigger runs, check status/logs, inspect drift alerts, run auto-heal, and rerun after patch per source.
- **Incident classes:**
  - Class A (Blocking): zero output/repeated failures.
  - Class B (Degraded): partial output/QC spike.
  - Class C (Non-critical): slower/slightly degraded.
  - For each: define notification targets, SLAs, and mitigation steps.

## 10. Change Management & Release
- All changes via PRs for new scrapers, selector updates, and core platform edits. Each PR must include updated tests/configs, migrations (if schema changes), and docs when behavior changes.
- Deploy flow: stage first with snapshots/limited live run → verify metrics/QC → schedule PROD.

## 11. Documentation
- Required docs: Platform overview/architecture, Source onboarding guide, Selector maintenance + auto-heal guide, Runbook & troubleshooting, Schema/contracts, Cost & capacity planning.

## 12. Cross-Script Flow (AlfaBeta example)
- Airflow DAG (`dags/scraper_alfabeta.py`) → `src.scrapers.alfabeta.pipeline.run_alfabeta(env=...)`.
- Config loader merges `config/settings.yaml` with `config/env/<env>.yaml` and the source file `config/sources/alfabeta.yaml`.
- Resource manager resolves account + proxy (`account_router`, `proxy_router`, `account_proxy_binding`).
- Session layer builds `SessionRecord` and cookie paths (`sessions.session_manager`).
- Engine opens session (`engines.selenium_engine.open_with_session`).
- Scraper modules orchestrate discovery/expansion/extraction (`company_index`, `product_index`, `alfabeta_full_impl`).
- Processors normalize + QC (`processors.unify_fields`, `processors.qc_rules`).
- Versioning tags records/runs (`versioning.version_manager`).
- Observability captures metrics/cost/drift/session health (`observability.metrics`, `cost_tracking`, `drift_monitor`, `session_health`).
- Outputs: CSV + DB + logs; incidents trigger agents if drift/failure detected.

## 13. Dependency Principles
- **Layering:** DAGs → scrapers → engines/resource_manager/sessions/common/config; agents/tools/API consume scrapers but lower layers never import scrapers.
- **One-way imports:** Imports only go down or sideways; engines and resource_manager never depend on scrapers; scrapers avoid importing agents.
- **Data dependencies:** selectors/schema_signature/snapshots are consumed by scrapers + agents but never create upward import edges.
- **Optional layers:** Agents, API, and some observability sinks are opt-in; the live scraping path must run without them.
