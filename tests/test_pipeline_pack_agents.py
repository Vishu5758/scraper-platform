import os

from src.pipeline_pack.agents import orchestrator
from src.pipeline_pack.agents import registry


EXPECTED_AGENTS = {
    "http_fetch",
    "html_parse",
    "llm_normalizer",
    "qc_rules",
    "pcid_match",
    "db_export",
}


def test_load_agent_config_uses_repo_config():
    base = orchestrator._config_base_dir()
    path = os.path.join(base, "config", "pipeline_pack", "pipelines.yaml")
    assert os.path.isfile(path), "pipeline pack config should exist at repository root"

    cfg = orchestrator.load_agent_config()
    assert "sources" in cfg and "alfabeta" in cfg["sources"], "config should include example source"


def test_register_default_agents_registers_all():
    registry.AgentRegistry._registry = {}
    registry._default_agents_registered = False

    registry.register_default_agents(force=True)
    registered = set(registry.AgentRegistry.list_agents())

    missing = EXPECTED_AGENTS.difference(registered)
    assert not missing, f"agents not registered: {sorted(missing)}"
