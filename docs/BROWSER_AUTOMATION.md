# Browser Automation + Proxy Strategy

This guide explains how to wire the new ScraperAPI-backed proxy rotation and Groq
browser automation engine into scraper pipelines. It covers three key pillars:

1. **Proxy sourcing & rotation** (ScraperAPI or static pools)
2. **LLM/automation provider** (Groq only — no OpenAI dependency)
3. **End-to-end workflow** for resilient crawlers.

---

## 1. Proxy Strategy (`config/proxies.yaml`)

The proxy blueprint is now centralized in `config/proxies.yaml`. Each pool can
mix static proxies with ScraperAPI virtual proxies:

```yaml
default_pool:
  rotation: round_robin
  providers:
    - name: scraperapi-global
      type: scraperapi
      api_key_env: SCRAPERAPI_API_KEY
      sticky_sessions: true
      session_prefix: global
      session_pool_size: 6
      country: us
      default_params:
        render: true
    - name: static-fallback
      type: static
      proxies:
        - http://user:pass@proxy-primary:9000
```

Per-source overrides can pin a custom session prefix, static pools, or disable
ScraperAPI entirely:

```yaml
per_source_overrides:
  alfabeta:
    providers:
      - name: alfabeta-scraperapi
        type: scraperapi
        session_prefix: alfabeta
        session_pool_size: 4
        country: ar
      - name: alfabeta-static
        type: static
        proxies:
          - http://proxy-alfabeta-1:9200
```

### How it works

- `ProxyPool` automatically loads this file. No code changes needed per scraper.
- Each ScraperAPI provider materializes N sticky sessions (defined by
  `session_pool_size`) so rotation behaves like classic proxy lists.
- Static proxies remain supported for air-gapped deployments.
- Set `SCRAPERAPI_API_KEY` in your environment (or use Vault → env injection).

---

## 2. Groq Browser Automation (`src/engines/groq_browser.py`)

Groq's compound models can control BrowserBase sessions using natural language,
eliminating fragile Selenium flows.

```python
from src.engines.groq_browser import GroqBrowserAutomationClient

client = GroqBrowserAutomationClient(
    model="groq/compound-mini",
    enabled_tools=["browser_automation", "web_search"],
)

result = client.run_workflow(
    "Visit https://example.com, log in with the shared creds, "
    "capture the daily prices table, and summarize deltas vs yesterday.",
    start_url="https://example.com/login",
    max_browser_time=150,
)

print(result.content)
for tool in result.executed_tools:
    print(tool["name"], tool["status"])
```

### Key points

- Requires only `GROQ_API_KEY`; no OpenAI account.
- The wrapper exposes a predictable `BrowserAutomationResult` (content +
  executed tool log + token usage).
- Use this engine by setting `engine.type: groq_browser` in any
  `config/sources/<source>.yaml`.

---

## 3. Putting it together

1. Define proxy pools in `config/proxies.yaml`.
2. Export `SCRAPERAPI_API_KEY` (and optional stickiness/country params).
3. Export `GROQ_API_KEY`.
4. In the target source config:

```yaml
engine:
  type: groq_browser

proxies:
  provider: scraperapi  # optional shorthand; blueprint still applies

llm:
  enabled: true
  provider: groq
  model: "llama3-70b-8192"
```

5. Inside the scraper pipeline, request a proxy via `resource_manager.proxy_pool`
   (it may be a ScraperAPI-backed session) and/or bootstrap a Groq browser flow.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| `Missing GROQ_API_KEY` | Env var unset | `export GROQ_API_KEY=...` |
| `ScraperAPI provider skipped` | API key missing or invalid blueprint | Check `config/proxies.yaml` + env |
| Browser workflow hangs | `max_browser_time` too low / network slow | Increase `max_browser_time` or enable screenshots for debugging |

---

## Next Steps

- Wire Groq browser engine into DSL components (tracked in `GAP_TO_V5.md`).
- Expose proxy health metrics via Prometheus.
- Add orchestration hooks so Airflow selects Groq vs Selenium automatically.

