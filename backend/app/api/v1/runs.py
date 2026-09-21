from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.orm.pull_request import PullRequest
from app.db.orm.repository import Repository
from app.db.orm.review_run import ReviewRun
from app.workers.tasks import run_pr_review_pipeline

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/{run_id}/status")
async def get_run_status(run_id: UUID, db: AsyncSession = Depends(get_db)):
    run = await db.get(ReviewRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Review run not found")
    return {
        "id": str(run.id),
        "status": run.status,
        "risk_score": run.risk_score,
        "risk_level": run.risk_level,
        "verdict_action": run.verdict_action,
    }


@router.post("/{pr_id}/rerun")
async def rerun_review(pr_id: UUID, db: AsyncSession = Depends(get_db)):
    pr = await db.get(PullRequest, pr_id)
    if pr is None:
        raise HTTPException(status_code=404, detail="Pull request not found")
    repo = await db.get(Repository, pr.repository_id)

    task = run_pr_review_pipeline.delay(
        installation_id=repo.installation_id,
        repo_full_name=repo.full_name,
        repo_github_id=repo.github_repo_id,
        pr_number=pr.github_pr_number,
        pr_payload={
            "title": pr.title,
            "author_login": pr.author_login,
            "base_branch": pr.base_branch,
            "head_branch": pr.head_branch,
            "head_sha": pr.head_sha,
            "additions": pr.additions,
            "deletions": pr.deletions,
            "changed_files": pr.changed_files,
        },
    )
    return {"status": "queued", "task_id": task.id}
