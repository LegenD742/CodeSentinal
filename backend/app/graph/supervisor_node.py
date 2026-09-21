"""
Entry node: fans out to the four specialist agents (bug/security/
performance/quality) for every hunk task in parallel, then fans back in
to a flat list of raw findings. This is the "multi-agent" core of the
graph — LangGraph tracks it as a single node internally, but each hunk
x agent combination runs concurrently via asyncio.gather.
"""
import asyncio

from app.agents.bug_agent import BugAgent
from app.agents.performance_agent import PerformanceAgent
from app.agents.quality_agent import QualityAgent
from app.agents.security_agent import SecurityAgent
from app.core.logging import get_logger
from app.graph.state import ReviewState

logger = get_logger(__name__)

_AGENTS = [BugAgent(), SecurityAgent(), PerformanceAgent(), QualityAgent()]


async def specialist_agents_node(state: ReviewState) -> dict:
    hunk_tasks = state.get("hunk_tasks", [])
    if not hunk_tasks:
        return {"raw_findings": []}

    coros = [agent.analyze(dict(task)) for task in hunk_tasks for agent in _AGENTS]
    results = await asyncio.gather(*coros, return_exceptions=True)

    findings: list[dict] = []
    errors: list[str] = []
    for res in results:
        if isinstance(res, Exception):
            errors.append(str(res))
            continue
        findings.extend(res)

    logger.info("Specialist agents produced %s raw findings across %s hunks", len(findings), len(hunk_tasks))
    return {"raw_findings": findings, "errors": errors}
