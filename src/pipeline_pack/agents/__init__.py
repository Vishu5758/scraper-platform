from .registry import AgentRegistry
from .http_fetch_agent import HttpFetchAgent
from .html_parse_agent import HtmlParseAgent
from .llm_normalizer_agent import LLMNormalizerAgent
from .pcid_match_agent import PCIDMatchAgent
from .qc_agent import QCAgent
from .db_export_agent import DbExportAgent

for agent_cls in [
    HttpFetchAgent,
    HtmlParseAgent,
    LLMNormalizerAgent,
    PCIDMatchAgent,
    QCAgent,
    DbExportAgent,
]:
    # Register by the snake_case identifier used in packaged pipelines.
    AgentRegistry.register(agent_cls.name, agent_cls)
    # Preserve compatibility for callers using the CamelCase class names.
    AgentRegistry.register(agent_cls.__name__, agent_cls)

__all__ = [
    "AgentRegistry",
    "HttpFetchAgent",
    "HtmlParseAgent",
    "LLMNormalizerAgent",
    "PCIDMatchAgent",
    "QCAgent",
    "DbExportAgent",
]
