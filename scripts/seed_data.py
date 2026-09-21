"""
Inserts a fake repository + PR + review run + a few findings so the
frontend has something to render without needing a live GitHub webhook.
Run with: from the `backend/` directory, with your virtual environment
active:
    PYTHONPATH=. python ../scripts/seed_data.py
(Windows PowerShell: set PYTHONPATH to "." then run
python ..\\scripts\\seed_data.py)
"""
import asyncio
import uuid

from app.db.orm.finding import Finding
from app.db.orm.pull_request import PullRequest
from app.db.orm.repository import Repository
from app.db.orm.review_run import ReviewRun
from app.db.session import db_session_ctx


async def seed():
    async with db_session_ctx() as db:
        repo = Repository(
            github_repo_id=123456,
            full_name="acme-org/checkout-service",
            default_branch="main",
            installation_id=1,
        )
        db.add(repo)
        await db.flush()

        pr = PullRequest(
            repository_id=repo.id,
            github_pr_number=42,
            title="Add promo code validation to checkout flow",
            author_login="jsmith",
            base_branch="main",
            head_branch="feature/promo-codes",
            head_sha="a1b2c3d4e5f6",
            additions=112,
            deletions=18,
            changed_files=4,
        )
        db.add(pr)
        await db.flush()

        run = ReviewRun(
            pull_request_id=pr.id,
            trigger_sha=pr.head_sha,
            status="completed",
            risk_score=52.0,
            risk_level="high",
            verdict_action="COMMENT",
            summary=(
                "This PR introduces a SQL query built via string formatting that should be "
                "parameterized, plus a discount calculation that can go negative for edge-case "
                "promo stacking. No blocking issues, but both should be addressed before merge."
            ),
        )
        db.add(run)
        await db.flush()

        db.add_all(
            [
                Finding(
                    review_run_id=run.id, source_agent="security", category="security",
                    severity="high", confidence=88, file_path="checkout/promo.py",
                    start_line=34, end_line=34, title="SQL query built via string formatting",
                    explanation="User-supplied promo_code is interpolated directly into the SQL query, allowing injection.",
                    evidence='query = f"SELECT * FROM promos WHERE code = \'{promo_code}\'"',
                    suggested_fix="Use a parameterized query: db.execute(query, (promo_code,))",
                    tool_origin="hybrid", critic_verdict="confirmed",
                    critic_reasoning="Evidence matches diff exactly; promo_code is user input from the request body.",
                ),
                Finding(
                    review_run_id=run.id, source_agent="bug", category="bug",
                    severity="medium", confidence=76, file_path="checkout/promo.py",
                    start_line=51, end_line=53, title="Discount can exceed order total",
                    explanation="Stacking two percentage promos is not capped, so total discount can exceed 100%.",
                    evidence="total_discount = promo_a.percent + promo_b.percent",
                    suggested_fix="Clamp total_discount to a maximum of 100 before applying.",
                    tool_origin="llm", critic_verdict="confirmed",
                ),
                Finding(
                    review_run_id=run.id, source_agent="quality", category="quality",
                    severity="low", confidence=60, file_path="checkout/promo.py",
                    start_line=12, end_line=12, title="Broad except clause swallows errors",
                    explanation="Catching bare Exception here hides real failures during promo lookup.",
                    evidence="except Exception:\n    return None",
                    suggested_fix="Catch the specific DatabaseError instead.",
                    tool_origin="llm", critic_verdict="downgraded",
                    critic_reasoning="Real issue but low impact in this code path; downgraded from medium.",
                ),
            ]
        )
        print(f"Seeded repo={repo.id} pr={pr.id} run={run.id}")


if __name__ == "__main__":
    asyncio.run(seed())
