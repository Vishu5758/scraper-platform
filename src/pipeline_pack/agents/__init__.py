from .registry import AgentRegistry
from .http_fetch_agent import HttpFetchAgent
from .html_parse_agent import HtmlParseAgent
from .llm_normalizer_agent import LLMNormalizerAgent
from .pcid_match_agent import PCIDMatchAgent
from .qc_agent import QCAgent
from .db_export_agent import DbExportAgent

AgentRegistry.register("HttpFetchAgent", HttpFetchAgent)
AgentRegistry.register("HtmlParseAgent", HtmlParseAgent)
AgentRegistry.register("LLMNormalizerAgent", LLMNormalizerAgent)
AgentRegistry.register("PCIDMatchAgent", PCIDMatchAgent)
AgentRegistry.register("QCAgent", QCAgent)
AgentRegistry.register("DbExportAgent", DbExportAgent)

__all__ = [
    "AgentRegistry",
    "HttpFetchAgent",
    "HtmlParseAgent",
    "LLMNormalizerAgent",
    "PCIDMatchAgent",
    "QCAgent",
    "DbExportAgent",
]
