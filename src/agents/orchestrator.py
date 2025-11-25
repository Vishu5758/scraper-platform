"""Agent orchestrator supporting sequential, parallel, and ensemble execution."""
from __future__ import annotations

import concurrent.futures
import time
from pathlib import Path
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import yaml

from src.common.logging_utils import get_logger
from src.common.paths import CONFIG_DIR

from .base import AgentContext
from .registry import AgentRegistry, register_builtin_agents, registry

log = get_logger("agents.orchestrator")


class PipelineNotFoundError(RuntimeError):
    """Raised when a pipeline for a source cannot be located."""


class AgentOrchestrator:
    """Executes a pipeline defined in configuration using the registry."""

    def __init__(
        self,
        registry: AgentRegistry,
        pipelines_config: Mapping[str, Any],
    ) -> None:
        self.registry = registry
        self.pipelines_config = pipelines_config

    def run_pipeline(self, source_name: str, initial_context: AgentContext) -> AgentContext:
        pipeline = self._load_pipeline(source_name)
        context = initial_context.copy()

        for step in pipeline:
            if "agent" in step:
                context = self._run_agent(step["agent"], context)
            elif "parallel" in step:
                context = self._run_parallel(step["parallel"], context)
            elif "ensemble" in step:
                context = self._run_ensemble(step["ensemble"], context)
            else:
                raise ValueError(f"Unknown pipeline step: {step}")
        return context

    def _run_agent(self, agent_name: str, context: AgentContext) -> AgentContext:
        agent = self.registry.get(agent_name)
        start = time.time()
        log.info("Running agent %s", agent_name)
        updated = agent.run(context)
        log.info("Agent %s completed in %.3fs", agent_name, time.time() - start)
        return updated

    def _run_parallel(self, block: Iterable[Mapping[str, Any]], context: AgentContext) -> AgentContext:
        steps = list(block)
        log.info("Running parallel block with %d agents", len(steps))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self._run_agent, step["agent"], context.copy()): idx
                for idx, step in enumerate(steps)
            }

        merged = context.copy()
        parallel_results = merged.metadata.setdefault("parallel_results", {})
        for future in concurrent.futures.as_completed(futures):
            idx = futures[future]
            result = future.result()
            merged.merge(result)
            merged.metadata.update(result.metadata)
            parallel_results[idx] = {
                "data": dict(result),
                "metadata": dict(result.metadata),
            }
        return merged

    def _run_ensemble(self, block: Mapping[str, Any], context: AgentContext) -> AgentContext:
        strategy = block.get("strategy", "first_success")
        agent_steps = block.get("agents") or []
        if not agent_steps:
            raise ValueError("Ensemble block requires 'agents'")

        log.info("Running ensemble (%s) with %d agents", strategy, len(agent_steps))
        best_context: Optional[AgentContext] = None
        best_score: float = float("-inf")

        for step in agent_steps:
            candidate = self._run_agent(step["agent"], context.copy())
            score = candidate.get("quality_score", candidate.get_nested("quality.score", 0))
            if strategy == "first_success":
                return candidate
            if strategy == "best_score" and score > best_score:
                best_score = float(score)
                best_context = candidate

        if best_context is not None:
            return best_context
        return context

    def _load_pipeline(self, source_name: str) -> List[MutableMapping[str, Any]]:
        sources = self.pipelines_config.get("sources") or {}
        source_cfg = sources.get(source_name)
        if not source_cfg:
            raise PipelineNotFoundError(f"No pipeline configured for source '{source_name}'")
        pipeline = source_cfg.get("pipeline")
        if not isinstance(pipeline, list):
            raise PipelineNotFoundError(f"Pipeline for {source_name} is not a list")
        return pipeline


def _read_yaml(path: Path) -> Mapping[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_agent_configs(
    *, config_dir: Path = CONFIG_DIR,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    """Load defaults and pipeline configs from disk."""

    defaults_path = config_dir / "agents" / "defaults.yaml"
    pipelines_path = config_dir / "agents" / "pipelines.yaml"

    defaults = _read_yaml(defaults_path)
    pipelines = _read_yaml(pipelines_path)
    return defaults, pipelines


# Initialize registry with builtins for convenience on import
register_builtin_agents()

__all__ = ["AgentOrchestrator", "PipelineNotFoundError", "load_agent_configs", "registry"]
