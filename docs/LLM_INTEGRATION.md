# LLM Integration

Guidance for integrating LLM-driven steps into scraping pipelines.

## Recommendations
- Isolate LLM calls in dedicated agents/processors for clarity.
- Log prompts and responses when allowed for debugging.
- Provide configuration flags to disable LLM usage per environment.

Refer to `config/agents/defaults.yaml` for global settings and update as integrations grow.
