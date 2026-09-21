"""
Final graph node: persists the review run + findings to Postgres and
posts the consolidated review to GitHub.
"""
from sqlalchemy import select

from app.core.logging import get_logger
from app.db.orm.finding import Finding
from app.db.orm.review_run import ReviewRun
from app.db.session import db_session_ctx
from app.github_integration.comment_poster import post_review_to_github
from app.graph.state import ReviewState

logger = get_logger(__name__)


async def commenter_node(state: ReviewState) -> dict:
    async with db_session_ctx() as db:
        result = await db.execute(select(ReviewRun).where(ReviewRun.id == state["review_run_id"]))
        review_run = result.scalar_one()

        review_run.risk_score = state["risk_score"]
        review_run.risk_level = state["risk_level"]
        review_run.verdict_action = state["verdict_action"]
        review_run.summary = state["summary"]
        review_run.status = "posting"

        finding_rows = []
        for f in state.get("verified_findings", []):
            row = Finding(
                review_run_id=review_run.id,
                source_agent=f["source_agent"],
                category=f["category"],
                severity=f["severity"],
                confidence=int(f.get("confidence", 50)),
                file_path=f["file_path"],
                start_line=int(f.get("start_line", 1)),
                end_line=int(f.get("end_line", f.get("start_line", 1))),
                title=f["title"],
                explanation=f["explanation"],
                evidence=f["evidence"],
                suggested_fix=f.get("suggested_fix"),
                tool_origin=f.get("tool_origin", "llm"),
                critic_verdict=f.get("critic_verdict"),
                critic_reasoning=f.get("critic_reasoning"),
            )
            db.add(row)
            finding_rows.append(row)
        await db.flush()

        try:
            await post_review_to_github(
                installation_id=state["installation_id"],
                owner=state["owner"],
                repo=state["repo"],
                pr_number=state["pr_number"],
                review_run=review_run,
                findings=finding_rows,
            )
            for row in finding_rows:
                row.is_posted_to_github = True
            review_run.status = "completed"
        except Exception as exc:
            logger.exception("Failed to post GitHub review")
            review_run.status = "failed"
            review_run.error_message = str(exc)

    return {}
