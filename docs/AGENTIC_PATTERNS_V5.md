# Agentic Execution Patterns for Scraper Platform v5.0

This document summarizes the 14 orchestration patterns in the reference diagram and specifies which patterns are mandatory, optional, or out-of-scope for scraper-platform v5.0. Use this as a checklist when designing new scrapers, auto-heal flows, or RAG-driven components.

## Summary of Patterns and v5.0 Applicability

| # | Pattern | What it is | v5.0 stance |
|---|---------|------------|-------------|
| 1 | **Parallel Tool Processing** | Fire multiple tools at once (e.g., Selenium + PDF parser + regex). | **Mandatory** for heavy scrapers and multi-format extraction. |
| 2 | **Branching Thoughts** | Model drafts multiple plans, judge picks best. | Optional for LLM normalization. |
| 3 | **Parallel Evaluation** | Multiple experts judge the same plan. | Optional for LLM table normalization. |
| 4 | **Parallel Query Expansion** | Generate multiple queries to hit vector DB from multiple angles. | Optional; only if using RAG enrichment. |
| 5 | **Sharded & Scattered Retrieval** | Fan-out retrieval across vector shards. | Out-of-scope unless vector DB exceeds ~1M entries. |
| 6 | **Competitive Agent Ensembles** | Agents compete (regex vs XPath vs LLM) and best result wins. | **Mandatory** for scraper auto-heal/DeepAgent flows. |
| 7 | **Hierarchical Agent Teams** | Parent agent delegates subtasks to children. | **Mandatory** for agent pipelines (navigate → extract → clean → normalize). |
| 8 | **Blackboard Collaboration** | Agents share central state (sessions, cookies, proxies). | **Mandatory** for multi-step scrapers. |
| 9 | **Parallel Multi-Hop Retrieval** | Break question into sub-questions and run in parallel. | **Mandatory** for PCID/product multi-hop matching. |
|10 | **Redundant Execution** | Run redundant copies; fastest valid wins. | Recommended for proxy resilience. |
|11 | **Agent Assembly Line** | Station-based flow: fetch → parse → cleanup → validate → export. | **Mandatory** in core scraper pipeline. |
|12 | **Parallel Context Pre-processing** | Split/clean large docs with multiple LLMs in parallel. | Optional for PDF→table extraction. |
|13 | **Hybrid Search Fusion** | Blend keyword + embedding search and merge results. | **Mandatory** for product catalog mapping and QC 2.0. |
|14 | **Speculative Execution** | Pre-fetch/provision tools before they are needed. | Recommended for browser automation and proxy prep. |

## Where to Apply Each Mandatory Pattern

- **Parallel Tool Processing**: Heavy scrapers that combine browser automation, PDF parsing, and DOM/text regex simultaneously. Wire into pipeline stages that can parallelize independent fetch/parse tasks.
- **Competitive Agent Ensembles**: Auto-heal flows (DeepAgent style) where regex, XPath, and LLM agents produce competing extraction patches and a judge picks the winner.
- **Hierarchical Agent Teams**: Parent agent coordinates navigation, extraction, cleaning, and normalization sub-agents; fits v5.0 agent pipelines.
- **Blackboard Collaboration**: Shared state (cookies, sessions, proxies, intermediate facts) enabling agents to hand off context during multi-step scraping.
- **Parallel Multi-Hop Retrieval**: Product/content matching workflows decomposed into brand → form → pack → seller → price hops for PCID and related matchers.
- **Agent Assembly Line**: Core scraper stages should follow the station pattern: page fetch → parse → cleanup → validate → export.
- **Hybrid Search Fusion**: Combine keyword and embedding search to boost recall/precision for product catalog matching, QC 2.0, and RAG-backed enrichments.

## Optional/Recommended Patterns

- **Branching Thoughts** and **Parallel Evaluation**: Use when LLM normalization quality matters (e.g., table reconstruction from PDFs) and budget allows extra model calls.
- **Parallel Context Pre-processing**: Helps with large PDFs; split into chunks and process in parallel before aggregation.
- **Redundant Execution**: Use multiple proxies or runner instances in parallel; accept the fastest successful run to improve reliability.
- **Speculative Execution**: Pre-provision proxies, cookies, and JS payloads to reduce latency for browser automation.
- **Parallel Query Expansion**: Only enable for RAG enrichment scenarios where broader recall is needed.
- **Sharded & Scattered Retrieval**: Defer until vector stores exceed ~1M entries or span many shards.

## Implementation Pointers

- **Pipeline fit:** Map patterns into existing pipeline stages (`dsl` plans, `src/agents`, `src/processors`, and RAG components). Ensure observability captures per-pattern metrics for debugging.
- **Auto-heal:** Extend DeepAgent/auto-repair flows (`src/agents/*`) to support competitive ensembles with a judging step and blackboard-shared context.
- **PCID matcher:** Use parallel multi-hop retrieval plus hybrid search fusion to evaluate brand/form/pack candidates concurrently, then reconcile results.
- **PDF/table workflows:** Pair parallel context pre-processing with optional branching thoughts + parallel evaluation to boost normalization quality.
- **Resilience:** For proxy-heavy runs, combine redundant execution with speculative provisioning of proxies/cookies to reduce failures.

## Adoption Checklist (v5.0)

- [ ] Parallel Tool Processing integrated into heavy scraper pipelines.
- [ ] Competitive Agent Ensembles wired into auto-heal/DeepAgent loops.
- [ ] Hierarchical Agent Teams defined for agent pipelines.
- [ ] Blackboard Collaboration implemented for shared session/proxy state.
- [ ] Parallel Multi-Hop Retrieval active for PCID/product matching.
- [ ] Agent Assembly Line pattern enforced in scraper core.
- [ ] Hybrid Search Fusion enabled for catalog mapping and QC 2.0.
- [ ] Optional patterns activated selectively (LLM-heavy normalization, PDF processing, RAG enrichment).

