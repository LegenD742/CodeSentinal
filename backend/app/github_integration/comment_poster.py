"""
Turns verified Finding objects + the aggregated risk report into a single
GitHub PR review (one summary body + N inline comments), posted atomically.
"""
from app.core.constants import VerdictAction
from app.github_integration.client import GitHubClient


def _severity_emoji(severity: str) -> str:
    return {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🔵",
        "info": "⚪",
    }.get(severity, "⚪")


def build_inline_comment_body(finding) -> str:
    lines = [
        f"**{_severity_emoji(finding.severity)} {finding.severity.upper()} · {finding.category} "
        f"· confidence {finding.confidence}%**",
        "",
        f"**{finding.title}**",
        "",
        finding.explanation,
        "",
        "<details><summary>Evidence</summary>",
        "",
        "```",
        finding.evidence,
        "```",
        "</details>",
    ]
    if finding.suggested_fix:
        lines += ["", f"**Suggested fix:** {finding.suggested_fix}"]
    if finding.suggested_patch:
        lines += ["", "```suggestion", finding.suggested_patch, "```"]
    lines += ["", f"_Raised by `{finding.source_agent}` agent, verified by Critic Agent._"]
    return "\n".join(lines)


def build_summary_body(review_run, findings: list) -> str:
    by_sev: dict[str, int] = {}
    for f in findings:
        by_sev[f.severity] = by_sev.get(f.severity, 0) + 1

    breakdown = " · ".join(f"{_severity_emoji(s)} {s}: {c}" for s, c in by_sev.items()) or "No issues found."

    return (
        f"## CodeSentinel Review\n\n"
        f"**Risk score:** {review_run.risk_score:.0f}/100 ({review_run.risk_level})\n"
        f"**Findings:** {breakdown}\n\n"
        f"{review_run.summary}\n\n"
        f"---\n*Automated review by CodeSentinel — verify findings before acting on them. "
        f"This is not a substitute for human review.*"
    )


async def post_review_to_github(
    installation_id: int,
    owner: str,
    repo: str,
    pr_number: int,
    review_run,
    findings: list,
) -> dict:
    client = GitHubClient(installation_id)

    inline_comments = [
        {
            "path": f.file_path,
            "line": f.end_line,
            "side": "RIGHT",
            "body": build_inline_comment_body(f),
        }
        for f in findings
        if f.critic_verdict != "rejected"
    ]

    event = review_run.verdict_action or VerdictAction.COMMENT
    summary_body = build_summary_body(review_run, findings)

    return await client.create_review(
        owner=owner,
        repo=repo,
        pr_number=pr_number,
        body=summary_body,
        event=event,
        comments=inline_comments,
    )
