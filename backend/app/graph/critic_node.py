"""
Runs the Critic Agent over all raw findings, grouped by file so each
verification call has the relevant diff hunk as evidence context.
"""
from app.agents.critic_agent import CriticAgent
from app.core.logging import get_logger
from app.graph.state import ReviewState

logger = get_logger(__name__)
_critic = CriticAgent()


async def critic_node(state: ReviewState) -> dict:
    raw_findings = state.get("raw_findings", [])
    hunk_by_file = {t["file_path"]: t["diff_hunk"] for t in state.get("hunk_tasks", [])}

    findings_by_file: dict[str, list[dict]] = {}
    for f in raw_findings:
        findings_by_file.setdefault(f["file_path"], []).append(f)

    verified: list[dict] = []
    for file_path, findings in findings_by_file.items():
        diff_hunk = hunk_by_file.get(file_path, "")
        verified.extend(await _critic.verify(findings, diff_hunk))

    kept = [f for f in verified if f.get("critic_verdict") != "rejected"]
    logger.info("Critic confirmed/downgraded %s of %s findings", len(kept), len(verified))
    return {"verified_findings": verified}
