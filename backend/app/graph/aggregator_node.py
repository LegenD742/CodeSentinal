"""
Combines all verified findings into an overall PR risk score (0-100)
and a recommended GitHub review verdict (APPROVE / COMMENT / REQUEST_CHANGES).
"""
from app.core.config import get_settings
from app.core.constants import Severity, VerdictAction
from app.core.llm_client import chat_completion
from app.graph.state import ReviewState

settings = get_settings()


def _compute_risk_score(findings: list[dict]) -> float:
    score = 0.0
    for f in findings:
        if f.get("critic_verdict") == "rejected":
            continue
        weight = Severity.WEIGHTS.get(f["severity"], 5)
        confidence_factor = f.get("confidence", 50) / 100
        score += weight * confidence_factor
    return min(100.0, round(score, 1))


def _risk_level(score: float) -> str:
    if score >= settings.risk_high_threshold:
        return "critical"
    if score >= settings.risk_medium_threshold:
        return "high"
    if score > 10:
        return "medium"
    return "low"


def _verdict_for(risk_level: str, findings: list[dict]) -> str:
    has_critical_confirmed = any(
        f["severity"] == Severity.CRITICAL and f.get("critic_verdict") != "rejected" for f in findings
    )
    if has_critical_confirmed or risk_level == "critical":
        return VerdictAction.REQUEST_CHANGES
    if risk_level in ("high", "medium"):
        return VerdictAction.COMMENT
    return VerdictAction.APPROVE


async def _generate_summary(findings: list[dict], risk_level: str) -> str:
    kept = [f for f in findings if f.get("critic_verdict") != "rejected"]
    if not kept:
        return "No significant issues were found. The change looks safe to merge from an automated review perspective."

    bullet_points = "\n".join(f"- [{f['severity']}] {f['title']} ({f['file_path']})" for f in kept[:10])
    prompt = f"""Write a concise 3-5 sentence PR review summary for a developer, given this risk level \
({risk_level}) and these confirmed findings:

{bullet_points}

Be direct and specific. Do not repeat the raw list — synthesize it into an assessment.
Respond with plain text only, no JSON, no markdown fences."""

    try:
        return await chat_completion(
            system_prompt="You are a precise, terse code review summarizer.",
            user_prompt=prompt,
            force_json=False,
            temperature=0.3,
        )
    except Exception:
        # Local LLM unreachable — fall back to a deterministic summary so the
        # pipeline still completes and posts something useful.
        return (
            f"{len(kept)} finding(s) confirmed, overall risk level: {risk_level}. "
            f"See inline comments for details (LLM summary unavailable)."
        )


async def aggregator_node(state: ReviewState) -> dict:
    findings = state.get("verified_findings", [])
    score = _compute_risk_score(findings)
    level = _risk_level(score)
    verdict = _verdict_for(level, findings)
    summary = await _generate_summary(findings, level)

    return {
        "risk_score": score,
        "risk_level": level,
        "verdict_action": verdict,
        "summary": summary,
    }
